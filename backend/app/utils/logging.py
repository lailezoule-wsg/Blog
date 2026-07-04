# app/core/logging.py
import logging
import logging.handlers
import sys
import json
import time
import re
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Union
from contextvars import ContextVar
from datetime import datetime, timezone
import traceback

# ============ 配置 ============
SENSITIVE_FIELDS = {
    "password", "passwd", "pwd", "secret", "token", 
    "api_key", "apikey", "authorization", "auth",
    "access_token", "refresh_token", "private_key"
}

# ============ 上下文变量 ============
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[Union[int, str]]] = ContextVar("user_id", default=None)


# ============ 安全工具函数 ============
def sanitize_log_message(msg: str) -> str:
    """清理日志消息"""
    if not isinstance(msg, str):
        return str(msg)
    # 移除换行符和回车符
    msg = msg.replace('\n', '\\n').replace('\r', '\\r')
    # 移除不可见控制字符
    msg = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', msg)
    return msg


def filter_sensitive_data(data: Any) -> Any:
    """递归过滤敏感数据"""
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in SENSITIVE_FIELDS else filter_sensitive_data(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [filter_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # 检查是否包含敏感模式
        if data.startswith("Bearer ") and len(data) > 20:
            return "Bearer ***REDACTED***"
        return data
    return data


# ============ Formatter ============
class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": sanitize_log_message(record.getMessage()),
        }

        if record.exc_info and record.exc_info != (None, None, None):
            exc_type, exc_value, exc_tb = record.exc_info
            log_obj["exception"] = {
                "type": exc_type.__name__ if exc_type else "Unknown",
                "message": sanitize_log_message(str(exc_value)) if exc_value else "",
                "traceback": "".join(traceback.format_tb(exc_tb)) if exc_tb else "",
            }

        request_id = request_id_var.get()
        if request_id:
            log_obj["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_obj["user_id"] = user_id

        extra_fields = getattr(record, "extra_fields", None)
        if extra_fields:
            log_obj["extra"] = filter_sensitive_data(extra_fields)

        return json.dumps(log_obj, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """控制台彩色日志"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = f"{color}{record.levelname}{reset}"
        logger_name = record.name
        filename = f"{record.filename}:{record.lineno}"
        func_name = record.funcName
        msg = sanitize_log_message(record.getMessage())

        context_parts = []
        request_id = request_id_var.get()
        if request_id:
            context_parts.append(f"req_id={request_id}")

        user_id = user_id_var.get()
        if user_id:
            context_parts.append(f"user_id={user_id}")

        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""

        log_line = f"{timestamp} {level} {logger_name} {filename} {func_name}{context_str} - {msg}"

        if record.exc_info:
            log_line += f"\n{color}{''.join(traceback.format_exception(*record.exc_info))}{reset}"

        return log_line


# ============ Logger 类 ============
class Logger:
    _loggers: Dict[str, "Logger"] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.INFO,
        log_dir: Optional[Union[str, Path]] = None,
        max_bytes: int = 50 * 1024 * 1024,
        backup_count: int = 10,
        use_json: bool = False,
        console: bool = True,
        file: bool = True,
        propagate: bool = False,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = propagate

        if self.logger.handlers:
            return

        if console:
            self._add_console_handler(use_json)

        if file and log_dir:
            self._add_file_handler(log_dir, max_bytes, backup_count, use_json)

    def _add_console_handler(self, use_json: bool = False) -> None:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter() if use_json else ConsoleFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(self.logger.level)
        self.logger.addHandler(handler)

    def _add_file_handler(self, log_dir: Union[str, Path], max_bytes: int, backup_count: int, use_json: bool = False) -> None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{self.name}.log"

        handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )

        formatter = JSONFormatter() if use_json else logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(self.logger.level)
        self.logger.addHandler(handler)

    # ========== 日志方法 ==========
    def debug(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.DEBUG, msg, *args, extra_fields=extra_fields, **kwargs)

    def info(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, extra_fields=extra_fields, **kwargs)

    def warning(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.WARNING, msg, *args, extra_fields=extra_fields, **kwargs)

    def error(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, extra_fields=extra_fields, **kwargs)

    def critical(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.CRITICAL, msg, *args, extra_fields=extra_fields, **kwargs)

    def exception(self, msg: str, *args, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, exc_info=True, extra_fields=extra_fields, **kwargs)

    def _log(self, level: int, msg: str, *args, exc_info=None, extra_fields: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        # ✅ 清理和过滤
        msg = sanitize_log_message(msg)
        if extra_fields:
            extra_fields = filter_sensitive_data(extra_fields)
            kwargs["extra"] = {"extra_fields": extra_fields}
        self.logger.log(level, msg, *args, exc_info=exc_info, **kwargs)

    # ========== 上下文管理 ==========
    @classmethod
    def context(cls, request_id: Optional[str] = None, user_id: Optional[Union[int, str]] = None):
        return _LogContext(request_id, user_id)

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        request_id_var.set(request_id)

    @classmethod
    def set_user_id(cls, user_id: Union[int, str]) -> None:
        user_id_var.set(user_id)

    @classmethod
    def clear_context(cls) -> None:
        request_id_var.set(None)
        user_id_var.set(None)

    # ========== 工厂方法 ==========
    @classmethod
    def get_logger(
        cls,
        name: Optional[str] = None,
        log_dir: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> "Logger":
        if name is None:
            try:
                import inspect
                frame = inspect.currentframe()
                if frame is not None:
                    caller_frame = frame.f_back
                    if caller_frame is not None:
                        name = caller_frame.f_globals.get("__name__", "root")
                    else:
                        name = "root"
                else:
                    name = "root"
            except Exception:
                name = "root"

        name = str(name) if name else "root"
        log_dir_str = str(log_dir) if log_dir else ""

        key_params = {
            "level": kwargs.get("level", logging.INFO),
            "use_json": kwargs.get("use_json", False),
            "console": kwargs.get("console", True),
            "file": kwargs.get("file", True),
            "propagate": kwargs.get("propagate", False),
            "max_bytes": kwargs.get("max_bytes", 50 * 1024 * 1024),
            "backup_count": kwargs.get("backup_count", 10),
        }

        try:
            kwargs_str = json.dumps(key_params, sort_keys=True)
        except (TypeError, ValueError):
            import hashlib
            kwargs_str = hashlib.md5(str(key_params).encode()).hexdigest()

        cache_key = f"{name}_{log_dir_str}_{kwargs_str}"

        # ✅ 使用线程锁
        with cls._lock:
            if cache_key not in cls._loggers:
                cls._loggers[cache_key] = cls(
                    name=name,
                    log_dir=log_dir,
                    **kwargs
                )
            return cls._loggers[cache_key]

    @classmethod
    def timer(cls, name: str, level: int = logging.INFO):
        return _TimerContext(name, level)

    def get_raw_logger(self) -> logging.Logger:
        return self.logger


# ============ 上下文类 ============
class _LogContext:
    def __init__(self, request_id: Optional[str] = None, user_id: Optional[Union[int, str]] = None):
        self.request_id = request_id
        self.user_id = user_id
        self._old_request_id: Optional[str] = None
        self._old_user_id: Optional[Union[int, str]] = None

    def __enter__(self):
        self._old_request_id = request_id_var.get()
        self._old_user_id = user_id_var.get()
        if self.request_id is not None:
            request_id_var.set(self.request_id)
        if self.user_id is not None:
            user_id_var.set(self.user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        request_id_var.set(self._old_request_id)
        user_id_var.set(self._old_user_id)
        return False


# ============ 计时器类 ============
class _TimerContext:
    def __init__(self, name: str, level: int = logging.INFO):
        self.name = name
        self.level = level
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            return False
        elapsed = time.perf_counter() - self.start_time
        msg = f"Timer [{self.name}] completed in {elapsed:.3f}s"
        if exc_type:
            msg += f" with exception: {exc_type.__name__}"
        logger = Logger.get_logger("timer")
        logger.logger.log(self.level, msg)
        return False


# ============ 便捷函数 ============
def get_logger(name: Optional[str] = None) -> Logger:
    return Logger.get_logger(name=name)


def setup_logging(level: Union[str, int] = logging.INFO, log_dir: Optional[Union[str, Path]] = None, **kwargs) -> None:
    Logger.get_logger("root", level=level, log_dir=log_dir, **kwargs)