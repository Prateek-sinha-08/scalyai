from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.business.domain.entities import BusinessUserRole


class BusinessDocumentResponseDTO(BaseModel):
    document_id: int = Field(..., description="Database identifier for the document")
    storage_public_id: str = Field(
        ..., description="External storage public identifier for the document"
    )
    file_url: str = Field(..., description="URL to access the stored document")
    original_filename: str = Field(..., description="Original uploaded filename")


class InitUploadFileDTO(BaseModel):
    original_filename: str = Field(..., description="Original filename from the client")
    content_type: str = Field(
        default="application/pdf", description="MIME type of the file"
    )
    size_bytes: int = Field(..., ge=1, description="Declared file size in bytes")


class CreateUploadSessionDTO(BaseModel):
    business_id: int = Field(..., ge=1, description="Business this upload belongs to")
    files: list[InitUploadFileDTO] = Field(
        ..., min_length=1, description="Files to reserve in this upload session"
    )


class UploadSlotCredentialsDTO(BaseModel):
    slot_id: UUID
    upload_url: str
    original_filename: str
    content_type: str
    expected_size_bytes: int


class CreateUploadSessionResponseDTO(BaseModel):
    upload_id: UUID
    expires_at: datetime
    slots: list[UploadSlotCredentialsDTO]


class CompleteUploadSessionResponseDTO(BaseModel):
    upload_id: UUID
    documents: list[BusinessDocumentResponseDTO]


class TransferUploadSlotResponseDTO(BaseModel):
    slot_id: UUID
    status: str
    uploaded_at: datetime


class BusinessUserDTO(BaseModel):
    id: int = Field(..., description="ID of the business")
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
