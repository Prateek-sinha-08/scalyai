from abc import ABC, abstractmethod


class IBusinessDocumentStorage(ABC):
    @abstractmethod
    async def delete(self, *, storage_public_id: str) -> None:
        pass
