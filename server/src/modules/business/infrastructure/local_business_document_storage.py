from modules.business.domain.document_storage_interface import IBusinessDocumentStorage
from modules.business.domain.exceptions import BusinessDocumentStorageFailedException
from shared.infrastructure.storage.clients.local_file_client import LocalFileStorageClient
from shared.infrastructure.storage.errors import StorageOperationError
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class LocalBusinessDocumentStorage(IBusinessDocumentStorage):
    def __init__(self, storage_client: LocalFileStorageClient) -> None:
        self._storage_client = storage_client

    async def delete(self, *, storage_public_id: str) -> None:
        try:
            await self._storage_client.delete(object_key=storage_public_id)
        except StorageOperationError as exc:
            logger.error(
                f"Local storage delete failed for object_key {storage_public_id}: {exc}"
            )
            raise BusinessDocumentStorageFailedException(
                message="Failed to delete business document from storage"
            ) from exc