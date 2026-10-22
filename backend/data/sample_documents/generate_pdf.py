"""
Script to generate a valid multi-page PDF for warranty terms.
"""
from pathlib import Path


def create_minimal_pdf(output_path: Path):
    content_page1 = (
        "FICTIONAL COMPANY HARDWARE LIMITED WARRANTY TERMS\n"
        "Disclaimer: Fictional document for RAG demonstration and automated testing.\n\n"
        "1. WARRANTY COVERAGE PERIOD\n"
        "All hardware products purchased directly through authorized retailers include a\n"
        "1-Year Limited Hardware Warranty covering defects in materials and workmanship.\n"
        "The warranty period begins on the verified delivery date shown in your carrier tracking.\n\n"
        "2. WHAT IS COVERED\n"
        "- Factory manufacturing defects in audio drivers, amplifiers, and internal circuitry.\n"
        "- Battery degradation where capacity drops below 70 percent within the first 12 months.\n"
        "- Power supply units and charging docks included in original packaging.\n"
    )

    content_page2 = (
        "3. WHAT IS NOT COVERED (EXCLUSIONS)\n"
        "- Accidental liquid spills, physical drops, and cracked enclosures.\n"
        "- Damage caused by unauthorized repair, disassembly, or third-party modifications.\n"
        "- Normal cosmetic wear including superficial surface scratches or cable fraying.\n\n"
        "4. WARRANTY CLAIM PROCEDURE\n"
        "To initiate a warranty claim, submit your proof of purchase and serial number at\n"
        "https://warranty.fictional-brand.example. Once approved, you will receive an RMA number\n"
        "and a prepaid shipping label. Replacement hardware is dispatched within 5 business days.\n"
    )

    # Simple PostScript/PDF text stream helper
    def make_stream(text):
        lines = text.split("\n")
        ops = ["BT", "/F1 12 Tf", "50 750 Td", "16 TL"]
        for line in lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            ops.append(f"({safe}) '")
        ops.append("ET")
        return "\n".join(ops).encode("latin-1")

    stream1 = make_stream(content_page1)
    stream2 = make_stream(content_page2)

    objects = []
    # 1: Catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # 2: Pages
    objects.append(b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>")
    # 3: Page 1
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
    )
    # 4: Stream 1
    objects.append(f"<< /Length {len(stream1)} >>\nstream\n".encode("latin-1") + stream1 + b"\nendstream")
    # 5: Page 2
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
    )
    # 6: Stream 2
    objects.append(f"<< /Length {len(stream2)} >>\nstream\n".encode("latin-1") + stream2 + b"\nendstream")

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(f"{i} 0 obj\n".encode("latin-1"))
        pdf_bytes.extend(obj)
        pdf_bytes.extend(b"\nendobj\n")

    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf_bytes.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Generated PDF at: {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent / "hardware_warranty_terms.pdf"
    create_minimal_pdf(out)
