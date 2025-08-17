# 配置参考

## 📋 目录

- [配置文件结构](#配置文件结构)
- [主配置选项](#主配置选项)
- [域配置文件](#域配置文件)
- [配置档案系统](#配置档案系统)
- [环境变量](#环境变量)

## 配置文件结构

MyConfig 使用 TOML 格式的配置文件，主要配置文件位于 `config/config.toml`。

```
myconfig/
├── config/
│   ├── config.toml          # 主配置文件
│   ├── defaults/
│   │   ├── domains.txt      # defaults 域清单
│   │   └── exclude.txt      # defaults 排除清单
│   └── profiles/
│       ├── minimal.toml     # 最小配置档案
│       └── dev-full.toml    # 完整开发环境配置
└── src/                     # Python 源码包
    ├── actions/             # 核心功能模块
    ├── plugins/             # 插件扩展
    ├── cli.py               # 命令行接口
    └── utils.py             # 工具函数
```

## 主配置选项

### config/config.toml

```toml
# 主开关
interactive = true          # 是否启用交互模式
enable_npm = false         # 是否导出 npm 全局包
enable_pip_user = false    # 是否导出 pip 用户包
enable_pipx = false        # 是否导出 pipx 包
enable_defaults = true     # 是否导出系统偏好设置
enable_vscode = true       # 是否导出 VS Code 扩展
enable_launchagents = true # 是否导出 LaunchAgents
enable_mas = true          # 是否导出 Mac App Store 应用

# 增量备份设置
enable_incremental = false # 是否启用增量备份
base_backup_dir = ""       # 基础备份目录，用于增量比较

# defaults 清单文件路径
defaults_domains_file = "config/defaults/domains.txt"   # 精选域清单
defaults_exclude_file = "config/defaults/exclude.txt"   # 排除域清单

# dotfiles 采集路径白名单（相对用户HOME；支持目录/文件）
# 空行或以#开头为注释
```

### 配置选项详解

#### 交互模式
```toml
interactive = true   # 每个操作前询问用户确认
interactive = false  # 自动执行所有操作（等同于 -y 参数）
```

#### 功能模块开关

**npm 全局包**
```toml
enable_npm = true    # 导出/恢复 npm -g list 的全局包
```

**Python 包管理**
```toml
enable_pip_user = true   # 导出/恢复 pip --user 安装的包
enable_pipx = true       # 导出/恢复 pipx 管理的工具
```

**应用和扩展**
```toml
enable_vscode = true     # VS Code 扩展列表
enable_mas = true        # Mac App Store 应用
```

**系统配置**
```toml
enable_defaults = true       # macOS 系统偏好设置
enable_launchagents = true   # 用户自定义服务
```

**增量备份**
```toml
enable_incremental = true
base_backup_dir = "./backups/backup-base"  # 用于比较的基础备份
```

## 域配置文件

### config/defaults/domains.txt

这个文件定义了要导出的 macOS defaults 域。每行一个域名，支持注释。

```txt
# 系统核心设置
NSGlobalDomain
com.apple.finder
com.apple.dock
com.apple.screencapture

# 可访问性
com.apple.Accessibility
com.apple.universalaccess

# 输入设备
com.apple.AppleMultitouchTrackpad
com.apple.symbolichotkeys

# 应用程序
com.apple.Safari
com.googlecode.iterm2

# 系统服务
com.apple.controlcenter
com.apple.WindowManager
com.apple.spaces
com.apple.SoftwareUpdate
com.apple.HIToolbox
com.apple.loginwindow
```

**常用域说明：**

| 域名 | 用途 |
|------|------|
| `NSGlobalDomain` | 全局系统设置 |
| `com.apple.finder` | 访达设置 |
| `com.apple.dock` | 程序坞设置 |
| `com.apple.screencapture` | 截图设置 |
| `com.apple.Accessibility` | 辅助功能 |
| `com.apple.Safari` | Safari 浏览器 |
| `com.googlecode.iterm2` | iTerm2 终端 |

### config/defaults/exclude.txt

定义不需要导出的 defaults 域（用于全量导出时排除）。

```txt
# 排除示例：iCloud/照片/安全沙盒/WebKit缓存/临时/统计类
com.apple.iCloudHelper
com.apple.cloudphotod
com.apple.cmfsyncagent
com.apple.WebKit
com.apple.Siri
com.apple.ctkplugin
com.apple.parsec-fbf
com.apple.telemetry
com.apple.diagnosticd
com.apple.quicklook
com.apple.touristd
com.apple.sidecar
com.apple.GameController
com.apple.Music
com.apple.Photos
```

## 配置档案系统

### 内置配置档案

**最小配置 (minimal.toml)**
```toml
interactive = true
enable_npm = false
enable_pip_user = false
enable_pipx = false
enable_defaults = true
enable_vscode = false
enable_launchagents = false
enable_mas = false
defaults_domains_file = "config/defaults/domains.txt"
defaults_exclude_file = "config/defaults/exclude.txt"
```

**完整开发环境 (dev-full.toml)**
```toml
interactive = true
enable_npm = true
enable_pip_user = true
enable_pipx = false
enable_defaults = true
enable_vscode = true
enable_launchagents = true
enable_mas = true
defaults_domains_file = "config/defaults/domains.txt"
defaults_exclude_file = "config/defaults/exclude.txt"
```

### 自定义配置档案

```bash
# 创建自定义配置档案
./bin/myconfig profile save my-config

# 使用配置档案
./bin/myconfig profile use my-config

# 列出所有配置档案
./bin/myconfig profile list
```

### 配置档案管理

```bash
# 保存当前配置为新档案
./bin/myconfig profile save server-env

# 编辑配置档案
nano ./config/profiles/server-env.toml

# 应用配置档案
./bin/myconfig profile use server-env
```

## 环境变量

### 运行时环境变量

```bash
# 强制非交互模式
export MYCONFIG_NON_INTERACTIVE=1

# 设置默认输出目录
export MYCONFIG_DEFAULT_OUTPUT="./my-backups"

# 启用调试模式
export MYCONFIG_DEBUG=1
```

### Python 环境要求

```bash
# Python 版本要求
python3 --version  # >= 3.8

# 可选依赖
pip install tomli  # TOML 解析库（Python < 3.11）
```

## 配置验证

### 检查配置有效性

```bash
# 系统环境检查
./bin/myconfig doctor

# 配置文件语法检查
python3 -c "
import sys
sys.path.insert(0, '.')
from myconfig.utils import load_config
cfg = load_config('./config/config.toml')
print('配置加载成功:', cfg)
"
```

### 常见配置错误

**1. TOML 语法错误**
```toml
# 错误：缺少引号
enable_npm = true
defaults_domains_file = config/defaults/domains.txt  # 错误

# 正确
enable_npm = true
defaults_domains_file = "config/defaults/domains.txt"  # 正确
```

**2. 路径错误**
```toml
# 错误：绝对路径
defaults_domains_file = "/usr/local/domains.txt"

# 正确：相对于项目根目录
defaults_domains_file = "config/defaults/domains.txt"
```

**3. 布尔值错误**
```toml
# 错误：字符串
enable_npm = "true"

# 正确：布尔值
enable_npm = true
```

## 配置示例

### 开发者工作站配置

```toml
# 开发者完整配置
interactive = false          # 自动化执行
enable_npm = true           # Node.js 开发
enable_pip_user = true      # Python 开发
enable_pipx = true          # Python 工具
enable_defaults = true      # 系统设置
enable_vscode = true        # 编辑器配置
enable_launchagents = true  # 开发服务
enable_mas = true           # 开发工具应用
enable_incremental = false  # 完整备份
```

### 服务器环境配置

```toml
# 服务器最小配置
interactive = false
enable_npm = false
enable_pip_user = true      # 只需要 Python
enable_pipx = false
enable_defaults = false     # 不需要 GUI 设置
enable_vscode = false       # 服务器不需要 GUI 编辑器
enable_launchagents = false
enable_mas = false          # 服务器没有 App Store
```

### 测试环境配置

```toml
# 测试环境配置
interactive = true          # 测试时需要确认
enable_npm = true
enable_pip_user = true
enable_pipx = false
enable_defaults = true
enable_vscode = false       # 测试环境不需要编辑器
enable_launchagents = false
enable_mas = false
enable_incremental = true   # 增量测试
base_backup_dir = "./backups/test-base"
```

---

更多配置细节请参阅源码中的配置类定义 (`src/utils.py` 中的 `AppConfig`)。
