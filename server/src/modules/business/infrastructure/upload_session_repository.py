from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.business.domain.entities import UploadSession, UploadSlot
from modules.business.domain.repository_interface import IUploadSessionRepository
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)


class UploadSessionRepository(IUploadSessionRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_session(
        self, session: UploadSession, slots: list[UploadSlot]
    ) -> UploadSession:
        try:
            self.db.add(session)
            for slot in slots:
                self.db.add(slot)
            await self.db.flush()
            await self.db.refresh(session, attribute_names=["slots"])
            return session
        except IntegrityError as exc:
            logger.error(f"IntegrityError while creating upload session: {exc}")
            raise

    async def get_session_for_user(
        self, upload_id: UUID, user_id: int
    ) -> Optional[UploadSession]:
        stmt = (
            select(UploadSession)
            .where(
                UploadSession.upload_id == upload_id,
                UploadSession.user_id == user_id,
            )
            .options(selectinload(UploadSession.slots))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_slot_with_session(
        self, slot_id: UUID
    ) -> Optional[tuple[UploadSlot, UploadSession]]:
        stmt = (
            select(UploadSlot)
            .where(UploadSlot.slot_id == slot_id)
            .options(selectinload(UploadSlot.session))
        )
        result = await self.db.execute(stmt)
        slot = result.scalar_one_or_none()
        if slot is None:
            return None
        return slot, slot.session