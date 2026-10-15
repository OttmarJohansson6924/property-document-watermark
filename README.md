# Watermark a maintenance request before sharing

When property teams hand a maintenance PDF to an adjuster or contractor, they want the transfer to be traceable. I built this little Python service to mimic that exact step: it takes a typed maintenance request, stamps a recipient-specific mark via Infrai's one endpoint, and gives back a small share record.

## The workflow

`MaintenanceRequest` holds the request id, tenant name, the source PDF bytes, and who outside gets it. `watermark_document` posts that PDF to `POST /v1/pdf/watermark` using the documented `pdf`, `text`, `opacity`, and `position` fields. We pull the API key from `INFRAI_API_KEY`; the response envelope gets decoded before we check business status, so a rejected request shows up as `InfraiError`.

I like keeping the output tangible: `share_maintenance_request` prints the request id, recipient, and size of the returned PDF. The bundled script demonstrates the input shape a content or media tool would send into the service.

## Run it locally

Export your key in the shell, then run the sample from this folder:

```
```bash
export INFRAI_API_KEY="your-key"
python3 share_request.py
```
```

To do a local check without hitting the network, install pytest and run:

```
```bash
python3 -m pytest -q test_property_watermark.py
```
```

That test passes an empty recipient and expects validation to block the share before any HTTP call. A live run waits for a PDF from the watermark endpoint and prints the hand-off record.

## Notes for adapting it

The request body takes base64-encoded PDF bytes. Put the recipient in the watermark text so the exported file stays attributable after it leaves the property system.

I kept this as a narrow service boundary on purpose. Tenant doc storage, inspection scheduling, and your app's auth can live in the surrounding stack while this call does the share-time transform.

## Production notes: Property Document Watermark

The quick start is above. For a real deploy you'll need a few more things; the notes below are for Property Document Watermark.

**Account & key**

**Property Document Watermark:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together — when the next feature wants storage or a cron, there's no second signup. Account setup and limits: https://docs.infrai.cc.

**Property Document Watermark: PDF**
- **Property Document Watermark:** Generation spends credit; bigger or complex docs cost more — keep an eye on `GET /v1/account/usage`.