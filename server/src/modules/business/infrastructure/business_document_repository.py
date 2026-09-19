from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.business.domain.entities import BusinessDocument
from modules.business.domain.exceptions import (
    BusinessDocumentNotDraftException,
    BusinessDocumentNotFoundException,
)
from modules.business.domain.repository_interface import IBusinessDocumentRepository
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class BusinessDocumentRepository(IBusinessDocumentRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, document: BusinessDocument) -> BusinessDocument:
        try:
            self.db.add(document)
            await self.db.flush()
            await self.db.refresh(document)
            return document
        except IntegrityError as exc:
            logger.error(f"IntegrityError while creating business document: {exc}")
            raise

    async def get_by_id(self, document_id: int) -> Optional[BusinessDocument]:
        stmt = select(BusinessDocument).where(BusinessDocument.id == document_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_user(
        self, document_id: int, user_id: int
    ) -> Optional[BusinessDocument]:
        stmt = select(BusinessDocument).where(
            BusinessDocument.id == document_id,
            BusinessDocument.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_drafts_for_user(self, user_id: int) -> list[BusinessDocument]:
        stmt = (
            select(BusinessDocument)
            .where(
                BusinessDocument.user_id == user_id,
                BusinessDocument.business_id.is_(None),
            )
            .order_by(BusinessDocument.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_draft(
        self, document_id: int, user_id: int
    ) -> BusinessDocument:
        document = await self.get_by_id_for_user(document_id, user_id)
        if document is None:
            raise BusinessDocumentNotFoundException()
        if document.business_id is not None:
            raise BusinessDocumentNotDraftException()

        await self.db.delete(document)
        await self.db.flush()
        return document
