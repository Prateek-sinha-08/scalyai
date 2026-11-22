from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config.storage import build_local_file_storage_client
from shared.infrastructure.storage.errors import StorageOperationError

router = APIRouter(tags=["files"])


@router.get("/files/{object_key:path}")
async def serve_stored_file(object_key: str):
    client = build_local_file_storage_client()
    try:
        path: Path = client.resolve_filesystem_path(object_key)
    except StorageOperationError:
        raise HTTPException(status_code=404, detail="File not found")

    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )