from property_watermark import MaintenanceRequest, share_maintenance_request


def sample_pdf() -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>",
        b"<< /Length 0 >>\nstream\n\nendstream",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"
    startxref = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii")
    pdf += b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets[1:])
    pdf += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n".encode("ascii")
    return pdf


def main() -> None:
    request = MaintenanceRequest(
        request_id="MR-1042",
        tenant_name="Mina Chen",
        document_bytes=sample_pdf(),
        external_recipient="chenhua@changba.com",
    )
    print(share_maintenance_request(request))


if __name__ == "__main__":
    main()
