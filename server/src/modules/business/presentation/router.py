import os
from typing import List

from fastapi import APIRouter, Depends, File, Request, UploadFile

from container.app.dependencies import get_uow
from container.app.infrastructure_uow import InfrastructureUnitOfWork
from modules.business.application.dtos import (
    AcceptBusinessDocumentCommand,
    BusinessDocumentDraftListItemDTO,
    BusinessDocumentResponseDTO,
    BusinessMemberPatchDTO,
    BusinessPatchDTO,
    CreateBusinessDTO,
    ResponseBusinessDTO,
    ResponseBusinessMemberDTO,
)
from modules.business.domain.exceptions import (
    BusinessCreationFailedException,
    BusinessDeletionFailedException,
    BusinessDocumentStorageFailedException,
    BusinessMemberDeletionFailedException,
    BusinessMemberUpdateFailedException,
    BusinessUpdateDetailsPatchFailedException,
    YouAreNotAllowedToAccessThisBusiness,
)
from modules.user.domain.exceptions import (
    NoPatchDataFoundException,
    UserNotFoundException,
)
from shared.base_exception import BaseAppException
from shared.logger import get_scaly_logger

logger = get_scaly_logger(name=__name__)

router = APIRouter(prefix="/api/v1/business", tags=["business"])


# TODO: Should this method be moved to a utility module?
async def _resolve_upload_size_bytes(file: UploadFile) -> int:
    if file.size is not None:
        return file.size

    await file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    await file.seek(0)
    return size_bytes


@router.post("/documents", response_model=BusinessDocumentResponseDTO)
async def accept_business_document(
    request: Request,
    file: UploadFile = File(...),
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]
    size_bytes = await _resolve_upload_size_bytes(file)
    content_header = await file.read(5)
    await file.seek(0)

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        command = AcceptBusinessDocumentCommand(
            user_id=user.id,
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=size_bytes,
            content=file.file,
            content_header=content_header,
        )

        try:
            result = await uow.business_document_service.accept_document(command)
            await uow.commit()
        except BaseAppException:
            await uow.rollback()
            raise
        except Exception as exc:
            await uow.rollback()
            logger.error(f"Error accepting business document: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to persist business document"
            ) from exc

        return result


@router.get("/documents", response_model=List[BusinessDocumentDraftListItemDTO])
async def list_business_document_drafts(
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        return await uow.business_document_service.list_drafts_for_user(user.id)


@router.get("/documents/{document_id}", response_model=BusinessDocumentResponseDTO)
async def get_business_document(
    document_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        return await uow.business_document_service.get_for_user(document_id, user.id)


@router.delete("/documents/{document_id}", status_code=204)
async def discard_business_document_draft(
    document_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]

    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()

        try:
            await uow.business_document_service.discard_draft(document_id, user.id)
            await uow.commit()
        except BaseAppException:
            await uow.rollback()
            raise
        except Exception as exc:
            await uow.rollback()
            logger.error(f"Error discarding business document draft: {exc}")
            raise BusinessDocumentStorageFailedException(
                message="Failed to discard business document draft"
            ) from exc


@router.post("/", response_model=ResponseBusinessDTO)
async def create_business(
    request: Request,
    business: CreateBusinessDTO,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    clerk_id = request.state.user["sub"]
    async with uow:
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        response_business_dto = await uow.business_service.create_business(
            business, user_id=user.id
        )
        try:
            await uow.commit()
        except Exception as e:
            await uow.rollback()
            logger.error(f"Error creating business: {e}")
            raise BusinessCreationFailedException()
        return response_business_dto


@router.get("/{business_id}", response_model=ResponseBusinessDTO)
async def get_business_by_id(
    business_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        is_member = await uow.business_member_service.is_user_a_member_of_business(
            business_id, user_id=user.id
        )
        if not is_member:
            raise YouAreNotAllowedToAccessThisBusiness()
        business = await uow.business_service.get_business_by_id(business_id)
        return business


@router.patch("/{business_id}", response_model=ResponseBusinessDTO)
async def patch_business(
    business_id: int,
    request: Request,
    patch: BusinessPatchDTO,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        have_access = (
            await uow.business_member_service.have_user_access_to_update_or_delete_business(
                business_id, user_id=user.id
            )
        )
        if not have_access:
            raise YouAreNotAllowedToAccessThisBusiness()
        patch_data = patch.model_dump(exclude_none=True)
        if not patch_data:
            raise NoPatchDataFoundException()
        updated_business = await uow.business_service.patch_business_details(
            business_id, patch_data
        )
        try:
            await uow.commit()
        except Exception as e:
            await uow.rollback()
            logger.error(f"Error patching business: {e}")
            raise BusinessUpdateDetailsPatchFailedException()
        return updated_business


@router.delete("/{business_id}", response_model=ResponseBusinessDTO)
async def delete_business(
    business_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        have_access = (
            await uow.business_member_service.have_user_access_to_update_or_delete_business(
                business_id, user_id=user.id
            )
        )
        if not have_access:
            raise YouAreNotAllowedToAccessThisBusiness()
        deleted_business = await uow.business_service.delete_business(business_id)
        try:
            await uow.commit()
        except Exception as e:
            await uow.rollback()
            logger.error(f"Error deleting business: {e}")
            raise BusinessDeletionFailedException()
        return deleted_business


@router.get("/{business_id}/members", response_model=List[ResponseBusinessMemberDTO])
async def get_members_of_business(
    business_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        is_member = await uow.business_member_service.is_user_a_member_of_business(
            business_id, user_id=user.id
        )
        if not is_member:
            raise YouAreNotAllowedToAccessThisBusiness()
        members = await uow.business_member_service.get_members_of_business(
            business_id
        )
        return members


@router.patch(
    "/{business_id}/members/{member_id}", response_model=ResponseBusinessMemberDTO
)
async def patch_business_member(
    business_id: int,
    member_id: int,
    request: Request,
    patch: BusinessMemberPatchDTO,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        have_access = (
            await uow.business_member_service.have_user_access_to_update_or_delete_business(
                business_id, user_id=user.id
            )
        )
        if not have_access:
            raise YouAreNotAllowedToAccessThisBusiness(
                "You are not allowed to update the role or permissions of this member"
            )

        patch_data = patch.model_dump(exclude_none=True)
        if not patch_data:
            raise NoPatchDataFoundException()
        updated_member = await uow.business_member_service.patch_business_member(
            business_id, member_id, patch_data
        )
        try:
            await uow.commit()
        except Exception as e:
            await uow.rollback()
            logger.error(f"Error patching business member: {e}")
            raise BusinessMemberUpdateFailedException()
        return updated_member


@router.delete(
    "/{business_id}/members/{member_id}", response_model=ResponseBusinessMemberDTO
)
async def delete_business_member(
    business_id: int,
    member_id: int,
    request: Request,
    uow: InfrastructureUnitOfWork = Depends(get_uow),
):
    async with uow:
        clerk_id = request.state.user["sub"]
        user = await uow.user_service.get_user_by_clerk_id(clerk_id=clerk_id)
        if user is None:
            raise UserNotFoundException()
        have_access = (
            await uow.business_member_service.have_user_access_to_update_or_delete_business(
                business_id, user_id=user.id
            )
        )
        if not have_access:
            raise YouAreNotAllowedToAccessThisBusiness(
                "You are not allowed to delete this member"
            )
        deleted_member = await uow.business_member_service.delete_business_member(
            business_id, member_id
        )
        try:
            await uow.commit()
        except Exception as e:
            await uow.rollback()
            logger.error(f"Error deleting business member: {e}")
            raise BusinessMemberDeletionFailedException()
        return deleted_member
