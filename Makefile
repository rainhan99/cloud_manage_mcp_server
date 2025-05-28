# 多云服务器管理系统 Makefile
# 使用 uv 作为包管理器

.PHONY: help install install-dev install-all run clean test lint format type-check build publish

# 默认目标
help:
	@echo "可用的命令："
	@echo "  install      - 安装基础依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  install-all  - 安装所有依赖（包括可选）"
	@echo "  run          - 运行应用程序"
	@echo "  clean        - 清理构建文件和虚拟环境"
	@echo "  test         - 运行测试"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  type-check   - 运行类型检查"
	@echo "  build        - 构建项目"
	@echo "  publish      - 发布到PyPI"
	@echo "  sync         - 同步依赖"

# 安装依赖
install:
	uv sync

install-dev:
	uv sync --extra dev

install-all:
	uv sync --extra full

# 同步依赖
sync:
	uv sync --refresh

# 运行应用
run:
	uv run python main.py

# 清理
clean:
	rm -rf .venv
	rm -rf uv.lock
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 开发工具
test:
	uv run pytest

lint:
	uv run flake8 .

format:
	uv run black .
	uv run isort .

type-check:
	uv run mypy .

# 代码质量检查（包含所有检查）
check: format lint type-check test
	@echo "所有代码质量检查完成！"

# 构建和发布
build:
	uv build

publish:
	uv publish

# 开发环境设置
dev-setup: install-dev
	@echo "开发环境设置完成！"
	@echo "运行 'make run' 启动应用程序"
	@echo "运行 'make check' 执行所有代码检查"

# 快速启动（安装依赖并运行）
quick-start: install run

# 添加依赖
add-dep:
	@echo "添加生产依赖: uv add <package-name>"
	@echo "添加开发依赖: uv add --dev <package-name>"
	@echo "添加可选依赖: uv add --optional <group> <package-name>"

# 显示依赖信息
show-deps:
	uv pip list

# 检查系统状态
status:
	uv run python -c "from main import get_system_status; import json; print(json.dumps(get_system_status(), indent=2, ensure_ascii=False))"

# 检查所有提供商状态
check-providers:
	uv run python -c "from main import get_supported_providers; import json; print(json.dumps(get_supported_providers(), indent=2, ensure_ascii=False))" 