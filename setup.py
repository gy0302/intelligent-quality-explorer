"""
安装配置文件
将项目安装为Python包，解决导入问题
"""
from setuptools import setup, find_packages

setup(
    name="smart-test-pilot-pro",
    version="0.1.0",
    description="智能测试探索架构 - AI驱动的智能测试生成平台",
    author="智能测试团队",
    packages=find_packages(where="."),
    package_dir={
        "": ".",  # 告诉setuptools在根目录查找包
    },
    include_package_data=True,
    install_requires=[
        "fastapi>=0.104.0",
        "streamlit>=1.28.0",
        "langchain>=0.0.340",
        "openai>=1.3.0",
        "pydantic>=2.5.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-test-pilot=run:main",
        ],
    },
    python_requires=">=3.9",
)