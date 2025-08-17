# MyConfig

一个专为 macOS 设计的系统配置备份与恢复工具。

## 🌟 特性

- 🔄 **完整备份**: 支持 Homebrew、VS Code、dotfiles、系统偏好设置等
- 🔒 **安全可靠**: 智能跳过敏感文件，自动验证备份完整性
- 👀 **预览模式**: 操作前预览将要备份/恢复的内容
- 📊 **进度显示**: 实时显示操作进度和状态
- ⚙️ **灵活配置**: 支持多种配置档案和自定义选项
- 🔌 **可扩展**: 支持插件系统扩展功能

## 🚀 快速开始

### 安装方式

**方式一：安装到系统命令 (推荐)**

```bash
# 克隆项目
git clone <repository-url>
cd myconfig

# 交互式安装
./install.sh

# 或者直接用户安装
./install.sh --user
# 或者系统安装 (需要 sudo)
./install.sh --system

# 使用 Makefile 安装
make install-user    # 用户安装
make install-system  # 系统安装
```

**方式二：直接运行 (无需安装)**

```bash
# 克隆项目
git clone <repository-url>
cd myconfig

# 设置执行权限
chmod +x bin/myconfig

# 直接使用
./bin/myconfig doctor
```

### 基本使用

**安装后使用：**
```bash
# 导出当前系统配置
myconfig export

# 预览导出内容  
myconfig --preview export

# 从备份恢复配置
myconfig restore ./backups/backup-xxx

# 系统环境检查
myconfig doctor
```

**直接运行使用：**
```bash
# 导出当前系统配置
./bin/myconfig export

# 预览导出内容
./bin/myconfig --preview export

# 从备份恢复配置
./bin/myconfig restore ./backups/backup-xxx

# 系统环境检查
./bin/myconfig doctor
```

## 📖 文档

详细文档请参阅 [docs](./docs/) 目录：

- [使用指南](./docs/usage.md) - 详细的使用说明和示例
- [配置参考](./docs/configuration.md) - 配置文件说明和选项
- [安全特性](./docs/security.md) - 安全机制和最佳实践
- [插件开发](./docs/plugins.md) - 插件系统和扩展开发
- [优化记录](./docs/OPTIMIZATION_SUMMARY.md) - 项目优化历史

## 🔧 主要命令

| 命令 | 描述 |
|------|------|
| `export [dir]` | 导出配置到指定目录 |
| `restore <dir>` | 从备份目录恢复配置 |
| `doctor` | 系统环境检查和诊断 |
| `--preview` | 预览模式，显示操作内容 |
| `--dry-run` | 试运行模式，不执行实际操作 |

## 🛡️ 安全特性

- 自动跳过敏感文件（SSH 密钥、密码文件等）
- 备份前自动备份现有文件
- 完整性验证和校验
- 详细的操作日志

## 📋 支持的内容

- **系统工具**: Homebrew（自动生成 Brewfile）, Mac App Store 应用
- **开发环境**: VS Code 扩展, npm/pip 包
- **配置文件**: Shell 配置, Git 配置, 编辑器配置
- **系统设置**: macOS 偏好设置 (defaults)
- **服务**: LaunchAgents 用户服务

## 📁 项目结构

```
myconfig/
├── bin/myconfig              # 可执行脚本
├── config/                   # 配置文件目录
│   ├── config.toml          # 主配置文件
│   ├── defaults/            # defaults 域配置
│   └── profiles/            # 配置档案
├── docs/                    # 文档目录
├── src/                     # Python 源码包
│   ├── actions/             # 核心功能模块
│   ├── plugins/             # 插件扩展
│   ├── cli.py               # 命令行接口
│   └── utils.py             # 工具函数
└── README.md               # 项目说明
```

## 🗑️ 卸载

如果需要卸载已安装的 myconfig：

```bash
# 使用卸载脚本
./uninstall.sh

# 或者使用 pip 直接卸载
pip3 uninstall myconfig

# 使用 Makefile
make uninstall
```

## 🛠️ 开发

```bash
# 开发模式安装 (可编辑)
make install-dev

# 代码格式化
make format

# 代码检查
make lint

# 构建包
make build

# 清理
make clean
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

GPL 2.0

---

**注意**: 首次使用前请运行 `myconfig doctor` (已安装) 或 `./bin/myconfig doctor` (直接运行) 检查系统环境。
# Test change
