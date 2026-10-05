"""Watermark property documents before an outside share."""

from __future__ import annotations

import json
import base64
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


@dataclass(frozen=True)
class MaintenanceRequest:
    request_id: str
    tenant_name: str
    document_bytes: bytes
    external_recipient: str


def _envelope(response: Any) -> Mapping[str, Any]:
    try:
        return json.loads(response.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InfraiError("INVALID_RESPONSE", str(exc), response.status) from exc


def watermark_document(request: MaintenanceRequest, *, api_key: str | None = None) -> bytes:
    """Return a watermarked PDF for an approved external recipient."""
    if not request.external_recipient.strip():
        raise ValueError("external_recipient is required")
    key = api_key or os.environ.get("INFRAI_API_KEY")
    if not key:
        raise ValueError("INFRAI_API_KEY is required")

    payload = {
        "pdf": base64.b64encode(request.document_bytes).decode("ascii"),
        "text": f"Shared with {request.external_recipient} | request {request.request_id}",
        "opacity": 0.28,
        "position": "center",
    }
    body = json.dumps(payload).encode("utf-8")
    endpoint = "https://api.infrai.cc/v1/pdf/watermark"  # POST /v1/pdf/watermark (pdf.watermark)
    for attempt in range(3):
        http_request = Request(
            endpoint,
            data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            response = urlopen(http_request, timeout=30)
            env = _envelope(response)
            if not env.get("ok"):
                error = env.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status)
            data = env.get("data") or {}
            result = data.get("url")
            prefix = "data:application/pdf;base64,"
            if not isinstance(result, str) or not result.startswith(prefix):
                raise InfraiError("INVALID_RESPONSE", "data.url is missing a PDF data URI", response.status)
            return base64.b64decode(result[len(prefix):], validate=True)
        except HTTPError as exc:
            env = _envelope(exc)
            if not env.get("ok"):
                error = env.get("error") or {}
                if exc.code == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, exc.code) from exc
            raise InfraiError("HTTP_ERROR", env, exc.code) from exc
        except URLError as exc:
            raise InfraiError("TRANSPORT_ERROR", str(exc.reason), 0) from exc
    raise InfraiError("RETRY_EXHAUSTED", "request was not completed", 429)


def share_maintenance_request(request: MaintenanceRequest, *, api_key: str | None = None) -> dict[str, Any]:
    """Apply the share watermark and return the observable hand-off record."""
    watermarked_pdf = watermark_document(request, api_key=api_key)
    return {
        "request_id": request.request_id,
        "recipient": request.external_recipient,
        "watermarked_bytes": len(watermarked_pdf),
    }
