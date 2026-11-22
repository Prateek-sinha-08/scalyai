import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import UUID
from shared.base_entity import Base, BaseModelMixin


class BusinessUserRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Business(BaseModelMixin, Base):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)

    business_user_mappings = relationship(
        "BusinessUserMapping",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    invites = relationship(
        "BusinessInvite",
        back_populates="business",
        cascade="all, delete-orphan",
    )


class BusinessUserMapping(Base):
    __tablename__ = "business_user_mappings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[BusinessUserRole] = mapped_column(
        Enum(BusinessUserRole), nullable=False
    )
    permissions: Mapped[dict] = mapped_column(JSON)

    user = relationship("User", back_populates="business_user_mappings")
    business = relationship("Business", back_populates="business_user_mappings")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (PrimaryKeyConstraint("user_id", "business_id"),)


class BusinessDocument(BaseModelMixin, Base):
    __tablename__ = "business_documents"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    storage_public_id: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    file_url: Mapped[str] = mapped_column(Text, nullable=False)

class UploadSessionStatus(enum.Enum):
    OPEN = "open"
    COMPLETED = "completed"
    EXPIRED = "expired"

class UploadSlotStatus(enum.Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"


class UploadSession(BaseModelMixin, Base):
    __tablename__ = "upload_sessions"
    
    upload_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[UploadSessionStatus] = mapped_column(Enum(UploadSessionStatus), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slots: Mapped[list["UploadSlot"]] = relationship("UploadSlot", back_populates="session", cascade="all, delete-orphan")

class UploadSlot(BaseModelMixin, Base):
    __tablename__ = "upload_slots"
    
    __table_args__ = (
        UniqueConstraint("object_key", name="uq_upload_slot_object_key"),
    )
    
    slot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    upload_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("upload_sessions.upload_id", ondelete="CASCADE"), nullable=False, index=True)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[UploadSlotStatus] = mapped_column(Enum(UploadSlotStatus), nullable=False, default=UploadSlotStatus.PENDING)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session: Mapped["UploadSession"] = relationship("UploadSession", back_populates="slots")