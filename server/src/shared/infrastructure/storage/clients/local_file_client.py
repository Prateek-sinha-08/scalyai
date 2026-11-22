from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from shared.infrastructure.storage.errors import StorageOperationError
from shared.infrastructure.storage.protocol import ILocalWritableStorageClient
from shared.infrastructure.storage.types import (
    DirectUploadCredentials,
    StoredObjectMetadata,
)

_CHUNK_SIZE = 64 * 1024
_UPLOADING_SUFFIX = ".uploading"
_PDF_HEADER = b"%PDF-"
_WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:")


class LocalFileStorageClient(ILocalWritableStorageClient):
    def __init__(
        self,
        *,
        root_path: Path,
        app_base_url: str,
        slot_upload_path_prefix: str = "/api/v1/business/documents/upload/slots",
        files_url_prefix: str = "/files",
    ) -> None:
        self._root_path = root_path.resolve()
        self._app_base_url = app_base_url.rstrip("/")
        self._slot_upload_path_prefix = slot_upload_path_prefix.rstrip("/")
        self._files_url_prefix = files_url_prefix.rstrip("/")
        self._root_path.mkdir(parents=True, exist_ok=True)

    def prepare_upload(
        self,
        *,
        object_key: str,
        content_type: str,
        max_size_bytes: int | None = None,
        slot_id: str | None = None,
    ) -> DirectUploadCredentials:
        if not slot_id or not slot_id.strip():
            raise StorageOperationError(
                "slot_id is required for local storage",
                operation="prepare_upload",
                object_key=object_key,
            )

        return DirectUploadCredentials(
            upload_url=(
                f"{self._app_base_url}{self._slot_upload_path_prefix}/{slot_id}"
            ),
            fields={},
            http_method="POST",
        )

    async def write_object(
        self,
        *,
        object_key: str,
        data: BinaryIO,
        content_type: str,
        max_size_bytes: int,
    ) -> None:
        path = self._resolve_path(object_key)
        try:
            await asyncio.to_thread(
                self._write_stream_to_file,
                path,
                data,
                max_size_bytes,
                object_key,
            )
        except StorageOperationError:
            raise
        except Exception as exc:
            raise StorageOperationError(
                "Failed to write object to local storage",
                operation="write_object",
                object_key=object_key,
            ) from exc

    async def delete(self, *, object_key: str) -> None:
        path = self._resolve_path(object_key)
        temp_path = self._temp_path_for(path)

        def _delete() -> None:
            try:
                if path.is_file():
                    path.unlink()
                if temp_path.is_file():
                    temp_path.unlink()
            except FileNotFoundError:
                return
            except OSError as exc:
                raise StorageOperationError(
                    "Failed to delete object from local storage",
                    operation="delete",
                    object_key=object_key,
                ) from exc

        await asyncio.to_thread(_delete)

    async def verify_object(
        self,
        *,
        object_key: str,
        expected_size_bytes: int | None = None,
        expected_content_type: str | None = None,
    ) -> StoredObjectMetadata:
        path = self._resolve_path(object_key)

        def _verify() -> StoredObjectMetadata:
            if not path.is_file():
                return StoredObjectMetadata(exists=False, size_bytes=0)

            size = path.stat().st_size
            if (
                expected_size_bytes is not None
                and size != expected_size_bytes
            ):
                raise StorageOperationError(
                    "Stored object size does not match expected size",
                    operation="verify_object",
                    object_key=object_key,
                )

            if expected_content_type is not None:
                with path.open("rb") as file:
                    header = file.read(len(_PDF_HEADER))
                if not header.startswith(_PDF_HEADER):
                    raise StorageOperationError(
                        "Invalid PDF header",
                        operation="verify_object",
                        object_key=object_key,
                    )

            return StoredObjectMetadata(exists=True, size_bytes=size)

        try:
            return await asyncio.to_thread(_verify)
        except StorageOperationError:
            raise
        except Exception as exc:
            raise StorageOperationError(
                "Failed to verify object in local storage",
                operation="verify_object",
                object_key=object_key,
            ) from exc

    def resolve_access_url(self, *, object_key: str) -> str:
        return f"{self._app_base_url}{self._files_url_prefix}/{object_key}"

    def resolve_filesystem_path(self, object_key: str) -> Path:
        return self._resolve_path(object_key)

    @staticmethod
    def _validate_object_key(object_key: str) -> None:
        if not object_key:
            raise StorageOperationError(
                "Object key is required",
                operation="validate_key",
            )
        if "\0" in object_key:
            raise StorageOperationError(
                "Object key contains invalid characters",
                operation="validate_key",
                object_key=object_key,
            )
        if object_key.startswith(("/", "\\")):
            raise StorageOperationError(
                "Object key must be relative",
                operation="validate_key",
                object_key=object_key,
            )
        if _WINDOWS_DRIVE_PATTERN.match(object_key):
            raise StorageOperationError(
                "Object key must be relative",
                operation="validate_key",
                object_key=object_key,
            )
        if ".." in PurePosixPath(object_key).parts:
            raise StorageOperationError(
                "Object key must not contain parent directory segments",
                operation="validate_key",
                object_key=object_key,
            )

    def _resolve_path(self, object_key: str) -> Path:
        self._validate_object_key(object_key)
        candidate = (self._root_path / PurePosixPath(object_key)).resolve()
        try:
            candidate.relative_to(self._root_path)
        except ValueError as exc:
            raise StorageOperationError(
                "Object key resolves outside storage root",
                operation="validate_key",
                object_key=object_key,
            ) from exc
        return candidate

    @staticmethod
    def _temp_path_for(path: Path) -> Path:
        if path.suffix:
            return path.with_suffix(f"{path.suffix}{_UPLOADING_SUFFIX}")
        return Path(f"{path}{_UPLOADING_SUFFIX}")

    @staticmethod
    def _write_stream_to_file(
        path: Path,
        data: BinaryIO,
        max_size_bytes: int,
        object_key: str,
    ) -> int:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = LocalFileStorageClient._temp_path_for(path)
        total = 0

        try:
            with temp_path.open("wb") as temp_file:
                while True:
                    chunk = data.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_size_bytes:
                        raise StorageOperationError(
                            "File exceeds max size",
                            operation="write_object",
                            object_key=object_key,
                        )
                    temp_file.write(chunk)

            os.replace(temp_path, path)
            return total
        except StorageOperationError:
            if temp_path.is_file():
                temp_path.unlink(missing_ok=True)
            raise
        except Exception:
            if temp_path.is_file():
                temp_path.unlink(missing_ok=True)
            raise
