from pathlib import Path

from config.settings import storage_config
from shared.infrastructure.storage.clients.local_file_client import LocalFileStorageClient


def build_local_file_storage_client() -> LocalFileStorageClient:
    return LocalFileStorageClient(
        root_path=Path(storage_config.FILE_STORAGE_ROOT),
        app_base_url=storage_config.APP_BASE_URL,
    )