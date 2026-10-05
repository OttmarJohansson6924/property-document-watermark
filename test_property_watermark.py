import pytest

from property_watermark import MaintenanceRequest, watermark_document


def test_external_recipient_is_required_before_api_call() -> None:
    request = MaintenanceRequest("MR-1", "Ava", b"pdf", "")
    with pytest.raises(ValueError, match="external_recipient"):
        watermark_document(request, api_key="test-key")
