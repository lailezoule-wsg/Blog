# backend/run.py
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=[
            "uploads/*",
            "logs/*",
            "*.db",
            "__pycache__",
            "*.pyc",
            ".env",
        ]
    )