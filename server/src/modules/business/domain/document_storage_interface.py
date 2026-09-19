from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    file_url: str
    original_filename: str


class IBusinessDocumentStorage(ABC):
    @abstractmethod
    async def store(
        self,
        *,
        user_id: int,
        storage_filename: str,
        content: BinaryIO,
        content_type: str,
        original_filename: str,
    ) -> StoredDocument:
        pass

    @abstractmethod
    async def delete(self, *, storage_public_id: str) -> None:
        pass
