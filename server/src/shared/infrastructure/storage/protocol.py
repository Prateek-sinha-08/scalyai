from abc import ABC, abstractmethod
from typing import BinaryIO

from shared.infrastructure.storage.types import (
    DirectUploadCredentials,
    StoredObjectMetadata,
)


class IFileStorageClient(ABC):
    @abstractmethod
    def prepare_upload(
        self,
        *,
        object_key: str,
        content_type: str,
        max_size_bytes: int | None = None,
        slot_id: str | None = None,
    ) -> DirectUploadCredentials: ...

    @abstractmethod
    async def delete(self, *, object_key: str) -> None: ...

    @abstractmethod
    async def verify_object(
        self,
        *,
        object_key: str,
        expected_size_bytes: int | None = None,
        expected_content_type: str | None = None,
    ) -> StoredObjectMetadata: ...

    @abstractmethod
    def resolve_access_url(self, *, object_key: str) -> str: ...


class ILocalWritableStorageClient(IFileStorageClient):
    @abstractmethod
    async def write_object(
        self,
        *,
        object_key: str,
        data: BinaryIO,
        content_type: str,
        max_size_bytes: int,
    ) -> None: ...
