from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from uuid import UUID

from modules.business.domain.entities import (
    Business,
    BusinessDocument,
    BusinessUserMapping,
    UploadSession,
    UploadSlot,
)
from modules.user.domain.entity import User


class IBusinessRepository(ABC):
    @abstractmethod
    async def create(self, business: Business) -> Business:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Business]:
        pass

    @abstractmethod
    async def update(self, business: Business, data: dict) -> None:
        pass

    @abstractmethod
    async def delete(self, business: Business) -> None:
        pass


class IBusinessMemberRepository(ABC):
    @abstractmethod
    async def add_member_to_business(
        self, business_user_mapping: BusinessUserMapping
    ) -> BusinessUserMapping:
        pass

    @abstractmethod
    async def get_member_by_business_id_and_user_id(
        self, business_id: int, user_id: int
    ) -> Optional[BusinessUserMapping]:
        pass

    @abstractmethod
    async def get_members_of_business(
        self, business_id: int
    ) -> List[Tuple[User, BusinessUserMapping]]:
        pass

    @abstractmethod
    async def get_businesses_by_member_id(
        self, member_id: int
    ) -> List[Tuple[BusinessUserMapping, Business]]:
        pass

    @abstractmethod
    async def update(self, business_member: BusinessUserMapping, data: dict) -> None:
        pass

    @abstractmethod
    async def delete(self, business_member: BusinessUserMapping) -> None:
        pass


class IBusinessDocumentRepository(ABC):
    @abstractmethod
    async def create(self, document: BusinessDocument) -> BusinessDocument:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: int) -> Optional[BusinessDocument]:
        pass

    @abstractmethod
    async def get_by_id_for_user(
        self, document_id: int, user_id: int
    ) -> Optional[BusinessDocument]:
        pass

    @abstractmethod
    async def get_by_user_business(
        self, user_id: int, business_id: int
    ) -> Optional[BusinessDocument]:
        pass

    @abstractmethod
    async def list_by_storage_public_ids_for_user(
        self, user_id: int, storage_public_ids: List[str]
    ) -> List[BusinessDocument]:
        pass


class IUploadSessionRepository(ABC):
    @abstractmethod
    async def add_session(
        self, session: UploadSession, slots: List[UploadSlot]
    ) -> UploadSession:
        pass

    @abstractmethod
    async def get_session_for_user(
        self, upload_id: UUID, user_id: int
    ) -> Optional[UploadSession]:
        pass

    @abstractmethod
    async def get_slot_with_session(
        self, slot_id: UUID
    ) -> Optional[tuple[UploadSlot, UploadSession]]:
        pass
