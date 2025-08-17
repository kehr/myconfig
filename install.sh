#!/bin/bash
#########################################################################
# @File Name:    install.sh
# @Author:       MyConfig Team
# @Created Time: 2024
# @Copyright:    GPL 2.0
# @Description:  MyConfig installation script
#########################################################################

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}▸${NC} $1"
}

print_success() {
    echo -e "${GREEN}✔${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✖${NC} $1"
}

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  MyConfig - macOS 配置备份与恢复工具${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
}

# 检查系统
check_system() {
    print_info "检查系统环境..."
    
    # 检查 macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "此工具仅支持 macOS 系统"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "未找到 python3，请先安装："
        echo "  brew install python"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 >/dev/null 2>&1; then
        print_error "未找到 pip3，请先安装 Python"
        exit 1
    fi
    
    print_success "系统环境检查通过"
}

# 安装选择
install_choice() {
    echo
    print_info "请选择安装方式："
    echo "  1) 用户安装 (推荐) - 安装到当前用户"
    echo "  2) 系统安装 - 安装到系统（需要 sudo）"
    echo "  3) 开发安装 - 可编辑模式安装"
    echo "  4) 取消安装"
    echo
    
    while true; do
        read -p "请输入选择 [1-4]: " choice
        case $choice in
            1)
                install_user
                break
                ;;
            2)
                install_system
                break
                ;;
            3)
                install_dev
                break
                ;;
            4)
                print_info "安装已取消"
                exit 0
                ;;
            *)
                print_warning "请输入有效选择 (1-4)"
                ;;
        esac
    done
}

# 用户安装
install_user() {
    print_info "开始用户安装..."
    
    # 检查是否在项目目录
    if [[ ! -f "setup.py" ]] || [[ ! -f "pyproject.toml" ]]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 安装
    print_info "使用 pip 安装到用户目录..."
    pip3 install --user -e .
    
    # 检查安装路径
    USER_BIN="$HOME/.local/bin"
    if [[ -f "$USER_BIN/myconfig" ]]; then
        print_success "安装成功！命令位置: $USER_BIN/myconfig"
        
        # 检查 PATH
        if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
            print_warning "需要将 $USER_BIN 添加到 PATH"
            echo "请在你的 shell 配置文件中添加："
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo
            echo "然后重新加载配置："
            echo "  source ~/.zshrc  # 或 ~/.bashrc"
        fi
    else
        print_warning "未在预期位置找到命令，但安装可能成功"
    fi
}

# 系统安装
install_system() {
    print_info "开始系统安装..."
    print_warning "这将需要管理员权限"
    
    # 检查是否在项目目录
    if [[ ! -f "setup.py" ]] || [[ ! -f "pyproject.toml" ]]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 安装
    print_info "使用 sudo pip 安装到系统..."
    sudo pip3 install -e .
    
    print_success "系统安装完成！"
}

# 开发安装
install_dev() {
    print_info "开始开发模式安装..."
    
    # 检查是否在项目目录
    if [[ ! -f "setup.py" ]] || [[ ! -f "pyproject.toml" ]]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 安装开发依赖
    print_info "安装开发依赖..."
    pip3 install --user -e ".[dev]"
    
    print_success "开发模式安装完成！"
    print_info "现在你可以直接修改代码，更改会立即生效"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    if command -v myconfig >/dev/null 2>&1; then
        print_success "myconfig 命令可用"
        
        # 测试版本
        version=$(myconfig --version 2>/dev/null || echo "未知")
        print_info "版本: $version"
        
        # 测试基本功能
        if myconfig doctor >/dev/null 2>&1; then
            print_success "基本功能测试通过"
        else
            print_warning "基本功能测试失败，但命令已安装"
        fi
    else
        print_error "myconfig 命令不可用"
        print_info "可能的解决方案："
        echo "  1. 重新加载 shell 配置"
        echo "  2. 检查 PATH 设置"
        echo "  3. 重新运行安装"
    fi
}

# 显示使用说明
show_usage() {
    echo
    print_success "安装完成！"
    echo
    print_info "使用方法："
    echo "  myconfig --help          # 查看帮助"
    echo "  myconfig doctor          # 系统检查"
    echo "  myconfig export          # 导出配置"
    echo "  myconfig restore <dir>   # 恢复配置"
    echo
    print_info "更多信息请查看："
    echo "  项目文档: ./docs/"
    echo "  在线帮助: myconfig --help"
    echo
}

# 卸载说明
show_uninstall() {
    echo
    print_info "卸载方法："
    echo "  用户安装: pip3 uninstall myconfig"
    echo "  系统安装: sudo pip3 uninstall myconfig"
    echo
}

# 主函数
main() {
    print_header
    
    # 处理命令行参数
    case "${1:-}" in
        --user)
            check_system
            install_user
            verify_installation
            show_usage
            ;;
        --system)
            check_system
            install_system
            verify_installation
            show_usage
            ;;
        --dev)
            check_system
            install_dev
            verify_installation
            show_usage
            ;;
        --uninstall)
            show_uninstall
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo
            echo "选项:"
            echo "  --user      用户安装（推荐）"
            echo "  --system    系统安装（需要 sudo）"
            echo "  --dev       开发模式安装"
            echo "  --uninstall 显示卸载说明"
            echo "  --help      显示此帮助"
            echo
            echo "不带参数运行将显示交互式安装菜单"
            ;;
        "")
            check_system
            install_choice
            verify_installation
            show_usage
            show_uninstall
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用 $0 --help 查看帮助"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
