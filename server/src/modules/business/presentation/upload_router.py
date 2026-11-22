from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile

from container.app.dependencies import get_uow
from container.app.infrastructure_uow import InfrastructureUnitOfWork
from modules.business.application.dtos import (
    CompleteUploadSessionResponseDTO,
    CreateUploadSessionDTO,
    CreateUploadSessionResponseDTO,
    TransferUploadSlotResponseDTO,
)
from modules.business.domain.exceptions import (
    BusinessDocumentStorageFailedException,
    YouAreNotAllowedToAccessThisBusiness,
)
from modules.user.domain.exceptions import UserNotFoundException
from shared.base_exception import BaseAppException
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)

router = APIRouter(prefix="/api/v1/business", tags=["business-upload"])


@router.post(
    "/documents/upload/sessions",
    response_model=CreateUploadSessionResponseDTO,
)
async def init_upload_session(
    request: Request,
    payload: CreateUploadSessionDTO,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        is_member = await uow.business_member_service.is_user_a_member_of_business(
            payload.business_id, user_id=user.id
        )
        if not is_member:
            raise YouAreNotAllowedToAccessThisBusiness()

        try:
            response = await uow.business_upload_service.init_session(user.id, payload)
            await uow.commit()
        except BaseAppException:
            await uow.rollback()
            raise
        except Exception as exc:
            await uow.rollback()
            logger.error(f"Error initializing upload session: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to initialize upload session"
            ) from exc

        return response


@router.post(
    "/documents/upload/slots/{slot_id}",
    response_model=TransferUploadSlotResponseDTO,
)
async def transfer_upload_slot(
    slot_id: UUID,
    request: Request,
    file: UploadFile = File(...),
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        try:
            response = await uow.business_upload_service.transfer_slot(
                user.id, slot_id, file
            )
            await uow.commit()
        except BaseAppException:
            await uow.rollback()
            raise
        except Exception as exc:
            await uow.rollback()
            logger.error(f"Error transferring upload slot {slot_id}: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to transfer uploaded file"
            ) from exc

        return response


@router.post(
    "/documents/upload/sessions/{upload_id}/complete",
    response_model=CompleteUploadSessionResponseDTO,
)
async def complete_upload_session(
    upload_id: UUID,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        try:
            response = await uow.business_upload_service.complete_session(
                user.id, upload_id
            )
            await uow.commit()
        except BaseAppException:
            await uow.rollback()
            raise
        except Exception as exc:
            await uow.rollback()
            logger.error(f"Error completing upload session {upload_id}: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to complete upload session"
            ) from exc

        return response