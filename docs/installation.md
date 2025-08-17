# 安装指南

本文档详细说明了 MyConfig 的各种安装方式和使用方法。

## 📋 目录

- [系统要求](#系统要求)
- [安装方式](#安装方式)
- [验证安装](#验证安装)
- [卸载](#卸载)
- [开发安装](#开发安装)
- [故障排除](#故障排除)

## 系统要求

### 必需
- **操作系统**: macOS 10.14 或更高版本
- **Python**: 3.8 或更高版本
- **pip**: Python 包管理器

### 推荐
- **Homebrew**: macOS 包管理器
- **Git**: 版本控制系统
- **VS Code**: 代码编辑器 (如需要 VS Code 功能)

### 检查系统要求

```bash
# 检查 macOS 版本
sw_vers

# 检查 Python 版本
python3 --version

# 检查 pip
pip3 --version

# 检查 Homebrew (可选)
brew --version

# 检查 Git (可选)
git --version
```

## 安装方式

### 方式一：自动安装脚本 (推荐)

**交互式安装**
```bash
git clone <repository-url>
cd myconfig
./install.sh
```

**用户安装 (推荐)**
```bash
./install.sh --user
```
- 安装到 `~/.local/bin/myconfig`
- 不需要管理员权限
- 只对当前用户可用

**系统安装**
```bash
./install.sh --system
```
- 安装到系统路径 (如 `/usr/local/bin/myconfig`)
- 需要管理员权限 (sudo)
- 对所有用户可用

**开发模式安装**
```bash
./install.sh --dev
```
- 可编辑安装，修改代码立即生效
- 包含开发工具和依赖

### 方式二：使用 Makefile

```bash
# 用户安装
make install-user

# 系统安装
make install-system

# 开发安装
make install-dev

# 查看所有选项
make help
```

### 方式三：使用 pip 直接安装

```bash
# 用户安装
pip3 install --user -e .

# 系统安装
sudo pip3 install -e .

# 开发安装 (包含开发依赖)
pip3 install --user -e ".[dev]"
```

### 方式四：直接运行 (无需安装)

```bash
git clone <repository-url>
cd myconfig
chmod +x bin/myconfig
./bin/myconfig doctor
```

## 验证安装

### 检查命令可用性

```bash
# 检查命令是否可用
which myconfig

# 查看版本
myconfig --version

# 运行系统检查
myconfig doctor
```

### 预期输出

```
$ myconfig --version
myconfig 3.0.0

$ myconfig doctor
系统体检
────────────────────────────────────────────────────────────
✔ Xcode CLT 已安装
✔ Homebrew 4.x.x
✔ code 命令可用
✔ App Store 登录：your@email.com
✔ defaults 域清单检查通过
────────────────────────────────────────────────────────────
✔ 体检完成
```

## PATH 配置

### 用户安装的 PATH 设置

如果用户安装后命令不可用，需要添加 `~/.local/bin` 到 PATH：

**对于 Zsh (默认)**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**对于 Bash**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**验证 PATH**
```bash
echo $PATH | grep -o "$HOME/.local/bin"
```

## 卸载

### 使用卸载脚本

```bash
# 交互式卸载
./uninstall.sh

# 强制卸载
./uninstall.sh --force

# 仅卸载用户安装
./uninstall.sh --user

# 仅卸载系统安装
./uninstall.sh --system
```

### 使用 pip 卸载

```bash
# 标准卸载
pip3 uninstall myconfig

# 系统安装的卸载
sudo pip3 uninstall myconfig
```

### 使用 Makefile 卸载

```bash
make uninstall
```

### 手动清理

如果自动卸载不完整，可以手动删除：

```bash
# 用户安装路径
rm -f ~/.local/bin/myconfig
rm -rf ~/.local/lib/python*/site-packages/myconfig*

# 系统安装路径
sudo rm -f /usr/local/bin/myconfig
sudo rm -rf /usr/local/lib/python*/site-packages/myconfig*
```

## 开发安装

### 开发环境设置

```bash
# 开发模式安装
make install-dev

# 或者手动安装
pip3 install --user -e ".[dev]"
```

### 开发工具

开发安装会包含以下工具：

- **pytest**: 测试框架
- **black**: 代码格式化
- **flake8**: 代码检查
- **mypy**: 类型检查

### 开发工作流

```bash
# 代码格式化
make format

# 代码检查
make lint

# 运行测试
make test

# 完整检查
make check

# 构建包
make build

# 清理
make clean
```

## 故障排除

### 常见问题

**1. Python 版本过低**
```
错误: myconfig requires Python 3.8 or higher
解决: brew install python
```

**2. 命令未找到**
```
错误: command not found: myconfig
解决: 检查 PATH 设置，添加 ~/.local/bin 到 PATH
```

**3. 权限错误**
```
错误: Permission denied
解决: 使用 --user 安装或检查文件权限
```

**4. 依赖冲突**
```
错误: Conflicting dependencies
解决: 使用虚拟环境或升级 pip
```

### 诊断命令

```bash
# 检查安装状态
./install.sh --help

# 查看详细信息
make info

# 验证安装
make verify

# 检查系统环境
myconfig doctor  # 或 ./bin/myconfig doctor
```

### 重新安装

```bash
# 完全重新安装
./uninstall.sh --force
./install.sh --user
```

## 高级配置

### 自定义安装路径

```bash
# 指定安装路径
pip3 install --user --install-option="--prefix=/custom/path" -e .
```

### 虚拟环境安装

```bash
# 创建虚拟环境
python3 -m venv myconfig-env
source myconfig-env/bin/activate

# 在虚拟环境中安装
pip install -e .

# 使用
myconfig doctor
```

### 系统服务 (高级)

如果需要作为系统服务运行：

```bash
# 创建服务文件 (示例)
sudo tee /Library/LaunchDaemons/com.myconfig.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.myconfig</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/myconfig</string>
        <string>doctor</string>
    </array>
</dict>
</plist>
EOF
```

---

如果遇到任何安装问题，请查看项目的 Issue 页面或创建新的 Issue。
