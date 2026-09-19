import asyncio
from typing import BinaryIO

import cloudinary
import cloudinary.uploader

from modules.business.domain.document_storage_interface import (
    IBusinessDocumentStorage,
    StoredDocument,
)
from modules.business.domain.exceptions import BusinessDocumentStorageFailedException
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class CloudinaryDocumentStorage(IBusinessDocumentStorage):
    def __init__(
        self,
        *,
        cloud_name: str,
        api_key: str,
        api_secret: str,
        folder_prefix: str,
    ) -> None:
        self._folder_prefix = folder_prefix.rstrip("/")
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    async def store(
        self,
        *,
        user_id: int,
        storage_filename: str,
        content: BinaryIO,
        content_type: str,
        original_filename: str,
    ) -> StoredDocument:
        folder = f"{self._folder_prefix}/{user_id}"
        public_id = storage_filename.rsplit(".", 1)[0]

        try:
            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                content,
                resource_type="raw",
                folder=folder,
                public_id=public_id,
                use_filename=False,
                overwrite=True,
            )
        except Exception as exc:
            logger.error(f"Cloudinary upload failed for user {user_id}: {exc}")
            raise BusinessDocumentStorageFailedException() from exc

        secure_url = result.get("secure_url")
        document_id = result.get("public_id")

        if not secure_url or not document_id:
            logger.error(
                f"Cloudinary upload returned incomplete response for user {user_id}"
            )
            raise BusinessDocumentStorageFailedException()

        return StoredDocument(
            document_id=document_id,
            file_url=secure_url,
            original_filename=original_filename,
        )

    async def delete(self, *, storage_public_id: str) -> None:
        try:
            result = await asyncio.to_thread(
                cloudinary.uploader.destroy,
                storage_public_id,
                resource_type="raw",
            )
        except Exception as exc:
            logger.error(
                f"Cloudinary delete failed for public_id {storage_public_id}: {exc}"
            )
            raise BusinessDocumentStorageFailedException(
                message="Failed to delete business document from storage"
            ) from exc

        if result.get("result") not in ("ok", "not found"):
            logger.error(
                f"Cloudinary delete returned unexpected result for "
                f"{storage_public_id}: {result}"
            )
            raise BusinessDocumentStorageFailedException(
                message="Failed to delete business document from storage"
            )
