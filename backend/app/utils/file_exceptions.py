# exceptions/file_exceptions.py
from fastapi import HTTPException, status

class FileUploadException(HTTPException):
    """文件上传基础异常"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class FileTooLargeError(FileUploadException):
    """文件过大异常"""
    def __init__(self, max_size: int, actual_size: int):
        detail = f"文件大小超过限制：最大 {max_size // (1024*1024)}MB，实际 {actual_size // (1024*1024)}MB"
        super().__init__(detail=detail, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

class UnsupportedFileTypeError(FileUploadException):
    """不支持的文件类型异常"""
    def __init__(self, allowed_types: list):
        detail = f"不支持的文件类型，请上传: {', '.join(allowed_types)}"
        super().__init__(detail=detail, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

class FileReadError(FileUploadException):
    """文件读取失败异常"""
    def __init__(self, filename: str):
        detail = f"文件读取失败: {filename}"
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class StorageFullError(FileUploadException):
    """存储空间不足异常"""
    def __init__(self, detail: str = "存储空间不足"):
        super().__init__(detail=detail, status_code=status.HTTP_507_INSUFFICIENT_STORAGE)