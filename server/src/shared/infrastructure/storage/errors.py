class StorageOperationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        operation: str,
        object_key: str | None = None,
    ) -> None:
        self.message = message
        self.operation = operation
        self.object_key = object_key
        super().__init__(message)


class UnsupportedStorageOperationError(StorageOperationError):
    pass
