from config.settings import storage_config
from modules.business.application.business_document_service import (
    BusinessDocumentService,
)
from modules.business.application.business_service import BusinessService
from modules.business.application.business_upload_service import BusinessUploadService
from modules.business.application.member_service import BusinessMemberService
from modules.business.domain.utils.document_policy import DocumentPolicy
from modules.business.infrastructure.business_document_repository import (
    BusinessDocumentRepository,
)
from modules.business.infrastructure.business_repository import BusinessRepository
from modules.business.infrastructure.member_repository import BusinessMemberRepository
from modules.business.infrastructure.upload_session_repository import (
    UploadSessionRepository,
)
from config.storage import build_local_file_storage_client
from modules.invitation.application.invitation_service import BusinessInviteService
from modules.invitation.infrastructure.invitation_repository import (
    InvitationsRepository,
)
from modules.notification.application.notification_service import NotificationService
from modules.notification.infrastructure.notification_repository import (
    NotificationRepository,
)
from modules.user.application.user_service import UserService
from modules.user.infrastructure.user_repository import UserRepository
from shared.infrastructure.storage.clients.local_file_client import LocalFileStorageClient
from shared.uow import BaseUnitOfWork


class InfrastructureUnitOfWork(BaseUnitOfWork):
    def __init__(self):
        super().__init__()
        self._user_repo: UserRepository | None = None
        self._business_repo: BusinessRepository | None = None
        self._business_member_repo: BusinessMemberRepository | None = None
        self._user_service: UserService | None = None
        self._business_service: BusinessService | None = None
        self._business_member_service: BusinessMemberService | None = None
        self._invitation_service: BusinessInviteService | None = None
        self._business_document_repo: BusinessDocumentRepository | None = None
        self._upload_session_repo: UploadSessionRepository | None = None
        self._business_document_service: BusinessDocumentService | None = None
        self._business_upload_service: BusinessUploadService | None = None
        self._local_file_storage: LocalFileStorageClient | None = None
        self._document_policy: DocumentPolicy | None = None
        self._notification_service: NotificationService | None = None

    @property
    def user_repo(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository(db=self.session)
        return self._user_repo

    @property
    def business_repo(self) -> BusinessRepository:
        if self._business_repo is None:
            self._business_repo = BusinessRepository(db=self.session)
        return self._business_repo

    @property
    def business_member_repo(self) -> BusinessMemberRepository:
        if self._business_member_repo is None:
            self._business_member_repo = BusinessMemberRepository(db=self.session)
        return self._business_member_repo

    @property
    def user_service(self) -> UserService:
        if self._user_service is None:
            self._user_service = UserService(user_repo=self.user_repo)
        return self._user_service

    @property
    def business_service(self) -> BusinessService:
        if self._business_service is None:
            self._business_service = BusinessService(
                business_repo=self.business_repo,
                business_member_repo=self.business_member_repo,
            )
        return self._business_service

    @property
    def business_member_service(self) -> BusinessMemberService:
        if self._business_member_service is None:
            self._business_member_service = BusinessMemberService(
                business_member_repo=self.business_member_repo,
                business_repo=self.business_repo,
                user_repo=self.user_repo,
            )
        return self._business_member_service

    @property
    def notification_service(self) -> NotificationService:
        if self._notification_service is None:
            notification_repo = NotificationRepository(db=self.session)
            self._notification_service = NotificationService(
                notification_repo=notification_repo
            )
        return self._notification_service

    @property
    def invitation_service(self) -> BusinessInviteService:
        if self._invitation_service is None:
            invitations_repo = InvitationsRepository(db=self.session)
            self._invitation_service = BusinessInviteService(
                invitations_repository=invitations_repo,
                notification_send_service=self.notification_service,
            )
        return self._invitation_service

    @property
    def business_document_repo(self) -> BusinessDocumentRepository:
        if self._business_document_repo is None:
            self._business_document_repo = BusinessDocumentRepository(db=self.session)
        return self._business_document_repo

    @property
    def upload_session_repo(self) -> UploadSessionRepository:
        if self._upload_session_repo is None:
            self._upload_session_repo = UploadSessionRepository(db=self.session)
        return self._upload_session_repo

    @property
    def local_file_storage(self) -> LocalFileStorageClient:
        if self._local_file_storage is None:
            self._local_file_storage = build_local_file_storage_client()
        return self._local_file_storage

    @property
    def document_policy(self) -> DocumentPolicy:
        if self._document_policy is None:
            self._document_policy = DocumentPolicy()
        return self._document_policy

    @property
    def business_document_service(self) -> BusinessDocumentService:
        if self._business_document_service is None:
            self._business_document_service = BusinessDocumentService(
                document_repo=self.business_document_repo,
            )
        return self._business_document_service

    @property
    def business_upload_service(self) -> BusinessUploadService:
        if self._business_upload_service is None:
            self._business_upload_service = BusinessUploadService(
                upload_repo=self.upload_session_repo,
                document_repo=self.business_document_repo,
                document_policy=self.document_policy,
                storage_client=self.local_file_storage,
                upload_session_ttl_seconds=storage_config.UPLOAD_SESSION_TTL_SECONDS,
                max_files_per_session=storage_config.MAX_FILES_PER_UPLOAD_SESSION,
            )
        return self._business_upload_service