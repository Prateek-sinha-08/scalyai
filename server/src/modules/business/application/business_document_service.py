from modules.business.application.dtos import BusinessDocumentResponseDTO
from modules.business.domain.entities import BusinessDocument
from modules.business.domain.exceptions import (
    BusinessDocumentAccessDeniedException,
    BusinessDocumentNotFoundException,
)
from modules.business.domain.repository_interface import IBusinessDocumentRepository
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class BusinessDocumentService:
    def __init__(self, document_repo: IBusinessDocumentRepository) -> None:
        self._document_repo = document_repo

    async def get_by_user_business(
        self, user_id: int, business_id: int
    ) -> BusinessDocumentResponseDTO:
        document = await self._document_repo.get_by_user_business(user_id, business_id)
        if document is None:
            raise BusinessDocumentNotFoundException()
        return self.to_response_dto(document)

    async def get_for_user(
        self, document_id: int, user_id: int
    ) -> BusinessDocumentResponseDTO:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise BusinessDocumentNotFoundException()
        if document.user_id != user_id:
            raise BusinessDocumentAccessDeniedException()
        return self.to_response_dto(document)

    @staticmethod
    def to_response_dto(document: BusinessDocument) -> BusinessDocumentResponseDTO:
        return BusinessDocumentResponseDTO(
            document_id=document.id,
            storage_public_id=document.storage_public_id,
            file_url=document.file_url,
            original_filename=document.original_filename,
        )