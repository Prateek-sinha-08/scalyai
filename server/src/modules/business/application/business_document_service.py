from uuid import uuid4

from modules.business.application.dtos import (
    AcceptBusinessDocumentCommand,
    BusinessDocumentDraftListItemDTO,
    BusinessDocumentResponseDTO,
)
from modules.business.domain.document_storage_interface import IBusinessDocumentStorage
from modules.business.domain.entities import BusinessDocument
from modules.business.domain.exceptions import (
    BusinessDocumentAccessDeniedException,
    BusinessDocumentNotDraftException,
    BusinessDocumentNotFoundException,
)
from modules.business.domain.repository_interface import IBusinessDocumentRepository
from modules.business.domain.utils.document_policy import DocumentPolicy
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class BusinessDocumentService:
    def __init__(
        self,
        document_policy: DocumentPolicy,
        storage: IBusinessDocumentStorage,
        document_repo: IBusinessDocumentRepository,
    ) -> None:
        self._document_policy = document_policy
        self._storage = storage
        self._document_repo = document_repo

    async def accept_document(
        self, command: AcceptBusinessDocumentCommand
    ) -> BusinessDocumentResponseDTO:
        metadata = self._document_policy.validate_for_acceptance(
            filename=command.filename,
            content_type=command.content_type,
            size_bytes=command.size_bytes,
            content_header=command.content_header,
        )

        storage_filename = f"{uuid4()}_{metadata.storage_filename}"

        stored = await self._storage.store(
            user_id=command.user_id,
            storage_filename=storage_filename,
            content=command.content,
            content_type=command.content_type or "application/pdf",
            original_filename=metadata.original_filename,
        )

        document = BusinessDocument(
            user_id=command.user_id,
            business_id=None,
            original_filename=metadata.original_filename,
            content_type=command.content_type or "application/pdf",
            size_bytes=command.size_bytes,
            storage_public_id=stored.document_id,
            file_url=stored.file_url,
        )

        try:
            created = await self._document_repo.create(document)
        except Exception:
            logger.error(
                "Failed to persist business document after Cloudinary upload: "
                f"storage_public_id={stored.document_id}, user_id={command.user_id}"
            )
            raise

        return self._to_response_dto(created)

    async def get_for_user(
        self, document_id: int, user_id: int
    ) -> BusinessDocumentResponseDTO:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise BusinessDocumentNotFoundException()
        if document.user_id != user_id:
            raise BusinessDocumentAccessDeniedException()
        return self._to_response_dto(document)

    async def list_drafts_for_user(
        self, user_id: int
    ) -> list[BusinessDocumentDraftListItemDTO]:
        documents = await self._document_repo.list_drafts_for_user(user_id)
        return [
            BusinessDocumentDraftListItemDTO(
                document_id=document.id,
                original_filename=document.original_filename,
                size_bytes=document.size_bytes,
                created_at=document.created_at,
            )
            for document in documents
        ]

    async def discard_draft(self, document_id: int, user_id: int) -> None:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise BusinessDocumentNotFoundException()
        if document.user_id != user_id:
            raise BusinessDocumentAccessDeniedException()
        if document.business_id is not None:
            raise BusinessDocumentNotDraftException()

        await self._storage.delete(storage_public_id=document.storage_public_id)

        try:
            await self._document_repo.delete_draft(document_id, user_id)
        except Exception:
            logger.error(
                "Failed to delete business document row after Cloudinary delete: "
                f"document_id={document_id}, storage_public_id={document.storage_public_id}"
            )
            raise

    @staticmethod
    def _to_response_dto(document: BusinessDocument) -> BusinessDocumentResponseDTO:
        return BusinessDocumentResponseDTO(
            document_id=document.id,
            storage_public_id=document.storage_public_id,
            file_url=document.file_url,
            original_filename=document.original_filename,
        )
