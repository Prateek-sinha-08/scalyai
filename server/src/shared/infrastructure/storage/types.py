from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DirectUploadCredentials:
    upload_url: str
    fields: dict[str, str] = field(default_factory=dict)
    http_method: str = "POST"
    headers: dict[str, str] | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class StoredObjectMetadata:
    exists: bool
    size_bytes: int
    content_type: str | None = None
