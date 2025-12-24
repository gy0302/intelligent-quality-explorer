# Makefile
"""
项目任务自动化脚本
作用：简化开发命令，统一团队工作流程
"""
.PHONY: help init install dev test lint format clean run web

help:
	@echo "可用命令:"
	@echo "  make init       初始化开发环境"
	@echo "  make install    安装生产依赖"
	@echo "  make dev        安装开发依赖"
	@echo "  make test       运行测试"
	@echo "  make lint       代码检查"
	@echo "  make format     代码格式化"
	@echo "  make clean      清理临时文件"
	@echo "  make run        运行CLI"
	@echo "  make web        启动Web界面"

init:
	@echo "创建虚拟环境..."
	python -m venv .venv
	@echo "✅ 请激活虚拟环境"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest explore/tests/ -v --cov=src --cov-report=html

lint:
	isort explore/src/ tests/ --check-only
	black explore/src/ tests/ --check
	mypy explore/src/

format:
	isort explore/src/ tests/
	black explore/src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage .pytest_cache .mypy_cache
	rm -rf htmlcov dist build

run:
	python -m explore.src.adapters.primary.cli

web:
	streamlit run explore/src/adapters/primary/web/app.py