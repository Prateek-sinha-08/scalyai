import asyncio

import cloudinary
import cloudinary.uploader

from modules.business.domain.document_storage_interface import IBusinessDocumentStorage
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
