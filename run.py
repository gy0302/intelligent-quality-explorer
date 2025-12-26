#!/usr/bin/env python3
"""
智能测试探索架构 - 统一启动脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 现在导入配置
try:
    from src.config.settings import settings

    print(f"✅ 配置加载成功: {settings.APP_NAME} v{settings.APP_VERSION}")
except ImportError as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)


def main():
    """主函数"""
    print(f"🚀 启动 {settings.APP_NAME}")
    print(f"📁 项目根目录: {settings.BASE_DIR}")

    # 检查必要目录
    if not settings.DATA_DIR.exists():
        settings.DATA_DIR.mkdir(parents=True)

    if not settings.OUTPUT_DIR.exists():
        settings.OUTPUT_DIR.mkdir(parents=True)

    print("✅ 环境检查完成")

    # 启动服务
    start_services()


def start_services():
    """启动服务"""
    import subprocess
    import threading
    import time

    # 启动FastAPI后端
    def start_fastapi():
        print("🌐 启动FastAPI后端...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", settings.API_HOST,
            "--port", str(settings.API_PORT),
            "--reload"
        ])

    # 启动Streamlit前端
    def start_streamlit():
        print("💻 启动Streamlit前端...")
        time.sleep(2)  # 等待FastAPI启动
        subprocess.run([
            sys.executable, "-m", "streamlit",
            "run", "src.web.app.py",
            "--server.port", str(settings.WEB_PORT),
            "--server.address", settings.WEB_HOST
        ])

    # 在新线程中启动服务
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)

    fastapi_thread.start()
    streamlit_thread.start()

    print(f"✅ FastAPI: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"✅ Streamlit: http://{settings.WEB_HOST}:{settings.WEB_PORT}")
    print("\n🎉 服务已启动！按 Ctrl+C 停止")

    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止服务...")


if __name__ == "__main__":
    main()