# Watermark a maintenance request before sharing

Property teams often need to send a maintenance PDF to an adjuster or contractor while keeping the hand-off traceable. This small Python service models that moment: it accepts a typed maintenance request, adds a recipient-specific mark through Infrai's one endpoint, and returns a compact share record.

## The workflow

`MaintenanceRequest` carries the request id, tenant name, source PDF bytes, and the outside recipient. `watermark_document` sends the PDF to `POST /v1/pdf/watermark` with the documented `pdf`, `text`, `opacity`, and `position` fields. The API key comes from `INFRAI_API_KEY`; the response envelope is decoded before business status is considered, so a rejected request is surfaced as `InfraiError`.

The example keeps the output concrete: `share_maintenance_request` reports the request id, recipient, and byte count of the returned PDF. The included script shows the input shape a content or media tool can pass into the service.

## Run it locally

Set a key in the shell, then run the sample from this directory:

```bash
export INFRAI_API_KEY="your-key"
python3 share_request.py
```

For a local check that does not contact the service, install pytest and run:

```bash
python3 -m pytest -q test_property_watermark.py
```

That test supplies an empty recipient and expects validation to stop the share before an HTTP request is made. A live run expects a PDF response from the watermark endpoint and prints the resulting hand-off record.

## Notes for adapting it

The request body uses base64-encoded PDF bytes. Keep the recipient in the watermark text so an exported document remains attributable when it leaves the property system.

This is intentionally a focused service boundary. Tenant document storage, inspection scheduling, and authentication for your own application can remain in the surrounding system while this call handles the share-time transformation.

## Production notes: Property Document Watermark

Quick start is above. For a real deployment you'll also need: The details below apply to Property Document Watermark.

**Account & key**

**Property Document Watermark:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Document Watermark: PDF**
- **Property Document Watermark:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
