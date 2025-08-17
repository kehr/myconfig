# MyConfig Makefile

.PHONY: help install install-user install-system install-dev uninstall clean build test lint format check

# 默认目标
help:
	@echo "MyConfig - macOS 配置备份与恢复工具"
	@echo ""
	@echo "可用命令:"
	@echo "  help          显示此帮助信息"
	@echo "  install       交互式安装"
	@echo "  install-user  用户安装 (推荐)"
	@echo "  install-system 系统安装 (需要 sudo)"
	@echo "  install-dev   开发模式安装"
	@echo "  uninstall     卸载"
	@echo "  clean         清理构建文件"
	@echo "  build         构建包"
	@echo "  test          运行测试"
	@echo "  lint          代码检查"
	@echo "  format        代码格式化"
	@echo "  check         完整检查 (lint + test)"

# 安装相关
install:
	@./install.sh

install-user:
	@./install.sh --user

install-system:
	@./install.sh --system

install-dev:
	@./install.sh --dev

uninstall:
	@echo "卸载 MyConfig..."
	pip3 uninstall myconfig -y || echo "未找到已安装的版本"

# 开发相关
clean:
	@echo "清理构建文件..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@find . -name ".coverage" -delete
	@find . -name "*.cover" -delete
	@find . -name "*.log" -delete

build: clean
	@echo "构建包..."
	@python3 -m build

test:
	@echo "运行测试..."
	@if [ -d "tests" ]; then \
		python3 -m pytest tests/ -v; \
	else \
		echo "暂无测试文件"; \
	fi

lint:
	@echo "代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 未安装，跳过检查"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/ --ignore-missing-imports; \
	else \
		echo "mypy 未安装，跳过类型检查"; \
	fi

format:
	@echo "代码格式化..."
	@if command -v black >/dev/null 2>&1; then \
		black src/; \
	else \
		echo "black 未安装，跳过格式化"; \
	fi

check: lint test
	@echo "完整检查完成"

# 发布相关
package: clean build
	@echo "创建发布包..."
	@ls -la dist/

# 开发环境设置
dev-setup:
	@echo "设置开发环境..."
	@pip3 install --user -e ".[dev]"
	@echo "开发环境设置完成"

# 验证安装
verify:
	@echo "验证安装..."
	@if command -v myconfig >/dev/null 2>&1; then \
		echo "✓ myconfig 命令可用"; \
		echo "版本: $$(myconfig --version)"; \
		myconfig doctor; \
	else \
		echo "✗ myconfig 命令不可用"; \
		exit 1; \
	fi

# 显示项目信息
info:
	@echo "项目信息:"
	@echo "  名称: MyConfig"
	@echo "  版本: $$(python3 -c 'import sys; sys.path.insert(0, "src"); from _version import VERSION; print(VERSION)')"
	@echo "  Python: $$(python3 --version)"
	@echo "  目录: $$(pwd)"
	@echo "  包数量: $$(find src -name '*.py' | wc -l | tr -d ' ') 个 Python 文件"
