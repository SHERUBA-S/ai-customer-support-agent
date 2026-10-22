import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import asyncio
import shutil
from app.core.config import settings
from app.services.ingestion import ingestion_service


async def seed():
    sample_dir = Path(__file__).resolve().parent.parent / "data" / "sample_documents"
    upload_dir = Path(__file__).resolve().parent.parent / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning sample documents in: {sample_dir}")
    sample_files = list(sample_dir.glob("*.md")) + list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))

    if not sample_files:
        print("No sample files found to seed.")
        return

    for file_path in sample_files:
        dest_path = upload_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        print(f"Ingesting '{file_path.name}'...")
        doc_record, count = await ingestion_service.ingest_file(dest_path, file_path.name)
        print(f" -> Indexed '{file_path.name}' into {count} chunks. (ID: {doc_record['document_id']})")

    print("\nKnowledge Base Seeding Complete!")


if __name__ == "__main__":
    asyncio.run(seed())
