from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import UploadFile

from modules.business.application.business_document_service import BusinessDocumentService
from modules.business.application.dtos import (
    BusinessDocumentResponseDTO,
    CompleteUploadSessionResponseDTO,
    CreateUploadSessionDTO,
    CreateUploadSessionResponseDTO,
    TransferUploadSlotResponseDTO,
    UploadSlotCredentialsDTO,
)
from modules.business.domain.entities import (
    BusinessDocument,
    UploadSession,
    UploadSessionStatus,
    UploadSlot,
    UploadSlotStatus,
)
from modules.business.domain.exceptions import (
    BusinessDocumentStorageFailedException,
    IncompleteUploadException,
    InvalidBusinessDocumentException,
    UploadSessionExpiredException,
    UploadSessionNotFoundException,
    UploadSessionNotOpenException,
    UploadSlotNotFoundException,
)
from modules.business.domain.repository_interface import (
    IBusinessDocumentRepository,
    IUploadSessionRepository,
)
from modules.business.domain.utils.document_policy import DocumentPolicy
from shared.infrastructure.storage.clients.local_file_client import LocalFileStorageClient
from shared.infrastructure.storage.errors import StorageOperationError
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class BusinessUploadService:
    def __init__(
        self,
        *,
        upload_repo: IUploadSessionRepository,
        document_repo: IBusinessDocumentRepository,
        document_policy: DocumentPolicy,
        storage_client: LocalFileStorageClient,
        upload_session_ttl_seconds: int,
        max_files_per_session: int,
    ) -> None:
        self._upload_repo = upload_repo
        self._document_repo = document_repo
        self._document_policy = document_policy
        self._storage_client = storage_client
        self._upload_session_ttl_seconds = upload_session_ttl_seconds
        self._max_files_per_session = max_files_per_session

    async def init_session(
        self, user_id: int, payload: CreateUploadSessionDTO
    ) -> CreateUploadSessionResponseDTO:
        if len(payload.files) > self._max_files_per_session:
            raise InvalidBusinessDocumentException(
                f"At most {self._max_files_per_session} files per upload session"
            )

        upload_id = uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=self._upload_session_ttl_seconds
        )
        session = UploadSession(
            upload_id=upload_id,
            user_id=user_id,
            business_id=payload.business_id,
            status=UploadSessionStatus.OPEN,
            expires_at=expires_at,
        )
        slots: list[UploadSlot] = []
        credentials: list[UploadSlotCredentialsDTO] = []

        for file_descriptor in payload.files:
            metadata = self._document_policy.validate_upload_intent(
                filename=file_descriptor.original_filename,
                content_type=file_descriptor.content_type,
                size_bytes=file_descriptor.size_bytes,
            )
            slot_id = uuid4()
            object_key = f"uploads/{user_id}/{upload_id}/{slot_id}.pdf"
            slot = UploadSlot(
                slot_id=slot_id,
                upload_id=upload_id,
                object_key=object_key,
                original_filename=metadata.original_filename,
                content_type=file_descriptor.content_type,
                expected_size_bytes=file_descriptor.size_bytes,
                status=UploadSlotStatus.PENDING,
            )
            slots.append(slot)

            prepared = self._storage_client.prepare_upload(
                object_key=object_key,
                content_type=file_descriptor.content_type,
                max_size_bytes=self._document_policy.max_size_bytes,
                slot_id=str(slot_id),
            )
            credentials.append(
                UploadSlotCredentialsDTO(
                    slot_id=slot_id,
                    upload_url=prepared.upload_url,
                    original_filename=metadata.original_filename,
                    content_type=file_descriptor.content_type,
                    expected_size_bytes=file_descriptor.size_bytes,
                )
            )

        await self._upload_repo.add_session(session, slots)

        return CreateUploadSessionResponseDTO(
            upload_id=upload_id,
            expires_at=expires_at,
            slots=credentials,
        )

    async def transfer_slot(
        self, user_id: int, slot_id: UUID, file: UploadFile
    ) -> TransferUploadSlotResponseDTO:
        resolved = await self._upload_repo.get_slot_with_session(slot_id)
        if resolved is None:
            raise UploadSlotNotFoundException()

        slot, session = resolved
        if session.user_id != user_id:
            raise UploadSlotNotFoundException()

        self._ensure_session_open(session)

        actual_size = await self._resolve_upload_size_bytes(file)
        if actual_size != slot.expected_size_bytes:
            raise InvalidBusinessDocumentException(
                "Uploaded file size does not match declared size"
            )

        self._document_policy.validate_upload_intent(
            filename=slot.original_filename,
            content_type=slot.content_type,
            size_bytes=actual_size,
        )

        await file.seek(0)
        try:
            await self._storage_client.write_object(
                object_key=slot.object_key,
                data=file.file,
                content_type=slot.content_type,
                max_size_bytes=self._document_policy.max_size_bytes,
            )
            await self._storage_client.verify_object(
                object_key=slot.object_key,
                expected_size_bytes=slot.expected_size_bytes,
                expected_content_type=slot.content_type,
            )
        except StorageOperationError as exc:
            logger.error(f"Storage error during slot transfer {slot_id}: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to store uploaded file"
            ) from exc

        slot.status = UploadSlotStatus.UPLOADED
        slot.uploaded_at = datetime.now(timezone.utc)

        return TransferUploadSlotResponseDTO(
            slot_id=slot.slot_id,
            status=slot.status.value,
            uploaded_at=slot.uploaded_at,
        )

    async def complete_session(
        self, user_id: int, upload_id: UUID
    ) -> CompleteUploadSessionResponseDTO:
        session = await self._upload_repo.get_session_for_user(upload_id, user_id)
        if session is None:
            raise UploadSessionNotFoundException()

        if session.status == UploadSessionStatus.COMPLETED:
            object_keys = [slot.object_key for slot in session.slots]
            documents = await self._document_repo.list_by_storage_public_ids_for_user(
                user_id, object_keys
            )
            return CompleteUploadSessionResponseDTO(
                upload_id=upload_id,
                documents=[
                    BusinessDocumentService.to_response_dto(document)
                    for document in documents
                ],
            )

        self._ensure_session_open(session)

        pending = [slot for slot in session.slots if slot.status != UploadSlotStatus.UPLOADED]
        if pending:
            raise IncompleteUploadException()

        created_documents: list[BusinessDocumentResponseDTO] = []
        for slot in session.slots:
            existing = await self._document_repo.list_by_storage_public_ids_for_user(
                user_id, [slot.object_key]
            )
            if existing:
                created_documents.append(
                    BusinessDocumentService.to_response_dto(existing[0])
                )
                continue

            file_url = self._storage_client.resolve_access_url(
                object_key=slot.object_key
            )
            document = BusinessDocument(
                user_id=user_id,
                business_id=session.business_id,
                original_filename=slot.original_filename,
                content_type=slot.content_type,
                size_bytes=slot.expected_size_bytes,
                storage_public_id=slot.object_key,
                file_url=file_url,
            )
            created = await self._document_repo.create(document)
            created_documents.append(BusinessDocumentService.to_response_dto(created))

        session.status = UploadSessionStatus.COMPLETED

        return CompleteUploadSessionResponseDTO(
            upload_id=upload_id,
            documents=created_documents,
        )

    @staticmethod
    def _ensure_session_open(session: UploadSession) -> None:
        now = datetime.now(timezone.utc)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if session.status == UploadSessionStatus.EXPIRED:
            raise UploadSessionExpiredException()
        if expires_at <= now:
            session.status = UploadSessionStatus.EXPIRED
            raise UploadSessionExpiredException()
        if session.status != UploadSessionStatus.OPEN:
            raise UploadSessionNotOpenException()

    @staticmethod
    async def _resolve_upload_size_bytes(file: UploadFile) -> int:
        if file.size is not None:
            return file.size

        await file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        await file.seek(0)
        return size_bytes