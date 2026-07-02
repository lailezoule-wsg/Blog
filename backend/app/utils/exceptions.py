import logging
from fastapi import FastAPI, Request, status,HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.utils.file_exceptions import *

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """配置全局异常处理器"""
    
    # 1. 处理 HTTPException
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
                "detail": None
            }
        )
    
    # 2. 处理请求验证错误（Pydantic）
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "; ".join(errors),
                "data": None,
                "detail": None
            }
        )
    
    # 3. 处理 SQLAlchemy 数据库错误
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "数据库错误",
                "data": None,
                "detail": str(exc) if app.debug else None
            }
        )
    
    # 4. 处理全局未捕获异常
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器内部错误",
                "data": None,
                "detail": str(exc) if app.debug else None
            }
        )
    
    # 5. 文件上传异常
    @app.exception_handler(FileUploadException)
    async def file_upload_exception_handler(request: Request, exc: FileUploadException):
        logger.error(f"文件上传错误: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
                "detail": None
            }
        )
    
    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(request: Request, exc: FileTooLargeError):
        logger.error(f"文件过大: {exc.detail}")
        return JSONResponse(
            # status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "文件大小超过限制",
                "data": None,
                "detail": exc.detail
            }
        )
    
    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_file_type_handler(request: Request, exc: UnsupportedFileTypeError):
        return JSONResponse(
            # status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "不支持的文件类型",
                "data": None,
                "detail": exc.detail
            }
        )
    
    @app.exception_handler(StorageFullError)
    async def storage_full_handler(request: Request, exc: StorageFullError):
        logger.error(f"存储空间不足: {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            content={
                "code": status.HTTP_507_INSUFFICIENT_STORAGE,
                "message": "存储空间不足",
                "data": None,
                "detail": exc.detail
            }
        )