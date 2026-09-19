import shutil
import tempfile
from pathlib import Path
from typing import BinaryIO

from modules.business.domain.document_storage_interface import (
    IBusinessDocumentStorage,
    StoredDocument,
)


class InMemoryDocumentStorage(IBusinessDocumentStorage):
    def __init__(self, base_url: str = "https://example.test/documents") -> None:
        self._base_url = base_url.rstrip("/")
        self._root = Path(tempfile.mkdtemp(prefix="business_documents_"))
        self.stored_files: list[Path] = []

    async def store(
        self,
        *,
        user_id: int,
        storage_filename: str,
        content: BinaryIO,
        content_type: str,
        original_filename: str,
    ) -> StoredDocument:
        user_dir = self._root / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        destination = user_dir / storage_filename
        with destination.open("wb") as buffer:
            shutil.copyfileobj(content, buffer)

        self.stored_files.append(destination)
        document_id = f"in-memory/{user_id}/{storage_filename}"

        return StoredDocument(
            document_id=document_id,
            file_url=f"{self._base_url}/{user_id}/{storage_filename}",
            original_filename=original_filename,
        )

    async def delete(self, *, storage_public_id: str) -> None:
        prefix = "in-memory/"
        if not storage_public_id.startswith(prefix):
            return

        relative = storage_public_id[len(prefix) :]
        parts = relative.split("/", 1)
        if len(parts) != 2:
            return

        user_id, storage_filename = parts
        destination = self._root / user_id / storage_filename
        if destination.exists():
            destination.unlink()
            if destination in self.stored_files:
                self.stored_files.remove(destination)
