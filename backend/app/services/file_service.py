# services/file_service.py
import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.utils.file_exceptions import *
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class FileUploadService:
    """文件上传服务"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 图片
    async def img_save(self,file:UploadFile,old_pic:str|None=None,del_flag:bool=False,subdir:str=settings.avatar_name) -> dict:
        await self.validate_file(
            file,
            max_size=settings.avatar_max_file_size,
            allowed_extensions=settings.avatar_allowed_extensions
        )
        
        # ✅ 保存文件（如果失败会自动抛出异常）
        filename = file.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        file_info = await self.save_file(
            file,
            subdir=subdir,
            filename=filename  # 自动生成文件名
        )
         # 先删除原有头像
        if old_pic and del_flag:
            await self.delete_file(subdir,old_pic)
        return file_info

    async def validate_file(
        self,
        file: UploadFile,
        max_size: int = 10 * 1024 * 1024,  # 默认 10MB
        allowed_extensions: set | None = None,
        allowed_mime_types: set | None = None,
    ) -> None:
        """验证文件"""
        # 1. 检查文件大小
        if file.size:
            if file.size > max_size:
                raise FileTooLargeError(max_size, file.size)
        else:
            # 如果无法获取文件大小，手动读取检查
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)
            if size > max_size:
                raise FileTooLargeError(max_size, size)
        
        # 2. 检查文件扩展名
        if allowed_extensions:
            if file.filename is None:
                raise ValueError("文件名不能为空")
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in allowed_extensions:
                raise UnsupportedFileTypeError(list(allowed_extensions))
        
        # 3. 检查 MIME 类型
        if allowed_mime_types and file.content_type:
            if file.content_type not in allowed_mime_types:
                raise UnsupportedFileTypeError(list(allowed_mime_types))

    async def save_file(
        self,
        file: UploadFile,
        subdir: str = "",
        filename: str | None = None,
    ) -> dict:
        """保存文件"""
        try:
            # 创建保存目录
            save_dir = self.upload_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{file.filename}"
            
            file_path = save_dir / filename
            
            # 保存文件
            try:
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
            except OSError as e:
                if "No space left on device" in str(e):
                    logger.error(f"No space left on device:{str(e)}")
                    raise StorageFullError()
                filename = file.filename or "unknown"
                raise FileReadError(filename) from e
            
            t = {
                "filename": filename,
                "original_name": file.filename,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "content_type": file.content_type,
                "url": f"/{settings.upload_dir}/{subdir}/{filename}" if subdir else f"/uploads/{filename}"
            }
            logger.info("fileinfofileinfofileinfofileinfofileinfo:",t)
            return {
                "filename": filename,
                "original_name": file.filename,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "content_type": file.content_type,
                "url": f"/{settings.upload_dir}/{subdir}/{filename}" if subdir else f"/uploads/{filename}"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            raise FileUploadException(f"文件保存失败: {str(e)}")
        
    async def delete_file(self, subdir: str, filename: str) -> bool:
        """
        删除文件
        
        Returns:
            bool: True 表示删除成功，False 表示文件不存在
        """
        file_path = self.upload_dir / subdir / filename

        if not file_path.exists():
            return False
        try:
            file_path.unlink()
            # 可选：删除空目录
            parent_dir = file_path.parent
            if not any(parent_dir.iterdir()):
                parent_dir.rmdir()
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False

    async def delete_files(self, subdir: str, filenames: list[str]) -> dict:
        """批量删除文件"""
        results = {"success": [], "failed": []}
        for filename in filenames:
            try:
                await self.delete_file(subdir, filename)
                results["success"].append(filename)
            except Exception as e:
                results["failed"].append({"filename": filename, "error": str(e)})
        return results