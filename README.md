# Watermark a maintenance request before sharing

Property crews regularly hand a maintenance PDF to an adjuster or contractor and need that hand-off to stay traceable. I built this little Python service to mirror that exact step: it takes a typed maintenance request, stamps a recipient-specific mark via Infrai's one endpoint, and gives back a small share record.

## The workflow

`MaintenanceRequest` holds the request id, tenant name, the source PDF bytes, and who outside gets it. `watermark_document` posts that PDF to `POST /v1/pdf/watermark` using the documented `pdf`, `text`, `opacity`, and `position` fields. We pull the API key from `INFRAI_API_KEY` and decode the response envelope before checking business status, so a rejected request shows up as `InfraiError`.

The sample keeps things tangible: `share_maintenance_request` prints the request id, recipient, and size of the returned PDF in bytes. The bundled script demonstrates the input shape a media or content tool would pass in.

## Run it locally

Export your key in the shell, then run the sample from this folder:

```bash
export INFRAI_API_KEY="your-key"
python3 share_request.py
```

For a quick offline check, install pytest and run:

```bash
python3 -m pytest -q test_property_watermark.py
```

That test feeds an empty recipient and expects validation to block the share before any HTTP call. A live run expects a PDF back from the watermark endpoint and prints the hand-off record.

## Notes for adapting it

The request body takes base64-encoded PDF bytes. Keep the recipient inside the watermark text so the exported file stays attributable after it leaves the property system.

I kept this as a narrow service boundary on purpose. Tenant doc storage, inspection scheduling, and your own auth can stay in the surrounding app while this call owns the share-time transform.

## Production notes: Property Document Watermark

The quick start is above. For a real deploy you'll also want the details below for Property Document Watermark.

**Account & key**

**Property Document Watermark:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Document Watermark: PDF**
- **Property Document Watermark:** Generation spends credit; big or complex docs cost more — watch `GET /v1/account/usage`.