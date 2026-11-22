from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePath

from modules.business.domain.exceptions import InvalidBusinessDocumentException

PDF_MAGIC_BYTES = b"%PDF-"
DEFAULT_FALLBACK_FILENAME = "Untitled_Document.pdf"


@dataclass
class DocumentPolicyConfig:
    max_size_bytes: int = 25 * 1024 * 1024
    min_size_bytes: int = 1
    max_filename_length: int = 255
    allowed_extensions: frozenset[str] = frozenset({".pdf"})
    allowed_content_types: frozenset[str] = frozenset({"application/pdf"})
    require_pdf_signature: bool = True


@dataclass(frozen=True)
class SanitizedDocumentMetadata:
    original_filename: str
    storage_filename: str


class DocumentPolicy:
    def __init__(self, config: DocumentPolicyConfig | None = None) -> None:
        self._config = config or DocumentPolicyConfig()

    def sanitize_filename(self, filename: str) -> str:
        basename = PurePath(filename).name.strip()

        if not basename:
            basename = DEFAULT_FALLBACK_FILENAME

        sanitized = re.sub(r"[^\w.\- ]", "_", basename)
        sanitized = re.sub(r"\s+", " ", sanitized).strip()

        if not sanitized.lower().endswith(".pdf"):
            sanitized = f"{sanitized}.pdf"

        return sanitized[: self._config.max_filename_length]

    def build_storage_filename(self, original_filename: str) -> str:
        return self.sanitize_filename(original_filename)

    def normalize_filename(self, filename: str | None) -> str:
        return (filename or "").strip()

    def _validate_filename_present(self, filename: str) -> None:
        if not filename:
            raise InvalidBusinessDocumentException("Filename is required")

    def _validate_filename_length(self, filename: str) -> None:
        if len(filename) > self._config.max_filename_length:
            raise InvalidBusinessDocumentException(
                f"Filename must be at most {self._config.max_filename_length} characters"
            )

    def _validate_no_path_traversal(self, filename: str) -> None:
        if filename != PurePath(filename).name:
            raise InvalidBusinessDocumentException("Invalid filename")

        if ".." in filename or "\x00" in filename:
            raise InvalidBusinessDocumentException("Invalid filename")

    def _validate_extension(self, filename: str) -> None:
        extension = PurePath(filename).suffix.lower()
        if extension not in self._config.allowed_extensions:
            raise InvalidBusinessDocumentException("Only PDF documents are allowed")

    def _validate_content_type(self, content_type: str | None) -> None:
        normalized = (content_type or "").split(";", 1)[0].strip().lower()
        if normalized not in self._config.allowed_content_types:
            raise InvalidBusinessDocumentException("Only PDF documents are allowed")

    def _validate_size(self, size_bytes: int) -> None:
        if size_bytes < self._config.min_size_bytes:
            raise InvalidBusinessDocumentException("File is empty")

        if size_bytes > self._config.max_size_bytes:
            max_mb = self._config.max_size_bytes // (1024 * 1024)
            raise InvalidBusinessDocumentException(
                f"File exceeds maximum size of {max_mb} MB"
            )

    def _validate_pdf_signature(self, content_header: bytes | None) -> None:
        if not self._config.require_pdf_signature:
            return

        if not content_header or not content_header.startswith(PDF_MAGIC_BYTES):
            raise InvalidBusinessDocumentException("File is not a valid PDF")

    @property
    def max_size_bytes(self) -> int:
        return self._config.max_size_bytes

    def validate_upload_intent(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        size_bytes: int,
    ) -> SanitizedDocumentMetadata:
        normalized = self.normalize_filename(filename)
        self._validate_filename_present(normalized)
        self._validate_filename_length(normalized)
        self._validate_no_path_traversal(normalized)
        self._validate_extension(normalized)
        self._validate_content_type(content_type)
        self._validate_size(size_bytes)
        return SanitizedDocumentMetadata(
            original_filename=normalized,
            storage_filename=self.build_storage_filename(normalized),
        )
