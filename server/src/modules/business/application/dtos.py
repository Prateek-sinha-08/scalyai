from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO, Optional

from pydantic import BaseModel, Field

from modules.business.domain.entities import BusinessUserRole


@dataclass(frozen=True)
class AcceptBusinessDocumentCommand:
    user_id: int
    filename: str | None
    content_type: str | None
    size_bytes: int
    content: BinaryIO
    content_header: bytes


class BusinessDocumentResponseDTO(BaseModel):
    document_id: int = Field(..., description="Database identifier for the document")
    storage_public_id: str = Field(
        ..., description="External storage public identifier for the document"
    )
    file_url: str = Field(..., description="URL to access the stored document")
    original_filename: str = Field(..., description="Original uploaded filename")


class BusinessDocumentDraftListItemDTO(BaseModel):
    document_id: int = Field(..., description="Database identifier for the document")
    original_filename: str = Field(..., description="Original uploaded filename")
    size_bytes: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="When the draft was created")


class BusinessUserDTO(BaseModel):
    name: str = Field(..., description="Name of the business")
    description: str = Field(..., description="Description of the business")
    industry: str = Field(..., description="Industry of the business")
    permissions: dict = Field(..., description="Permissions of the business")
    role: BusinessUserRole = Field(
        ..., description="Role of the user in the business"
    )


class ResponseBusinessDTO(BaseModel):
    id: int = Field(..., description="ID of the business")
    name: str = Field(..., description="Name of the business")
    description: str = Field(..., description="Description of the business")
    industry: str = Field(..., description="Industry of the business")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")


class CreateBusinessDTO(BaseModel):
    name: str = Field(..., description="Name of the business")
    description: str = Field(..., description="Description of the business")
    industry: str = Field(..., description="Industry of the business")


class ResponseBusinessMemberDTO(BaseModel):
    id: int = Field(..., description="ID of the member")
    name: str = Field(..., description="Name of the member")
    email: str = Field(..., description="Email of the member")
    role: BusinessUserRole = Field(..., description="Role of the member")
    permissions: dict = Field(..., description="Permissions of the member")


class BusinessPatchDTO(BaseModel):
    name: Optional[str] = Field(None, description="Name of the business")
    description: Optional[str] = Field(None, description="Description of the business")
    industry: Optional[str] = Field(None, description="Industry of the business")


class BusinessMemberPatchDTO(BaseModel):
    role: Optional[BusinessUserRole] = Field(None, description="Role of the member")
    permissions: Optional[dict] = Field(None, description="Permissions of the member")
