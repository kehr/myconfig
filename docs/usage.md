# MyConfig 使用指南

## 📋 目录

- [基本概念](#基本概念)
- [命令详解](#命令详解)
- [常用场景](#常用场景)
- [高级功能](#高级功能)
- [故障排除](#故障排除)

## 基本概念

MyConfig 是一个配置管理工具，主要功能包括：

- **导出 (Export)**: 将当前系统的配置和应用列表保存到备份目录
- **恢复 (Restore)**: 从备份目录恢复配置到新系统
- **预览 (Preview)**: 在执行前查看将要操作的内容
- **验证 (Verify)**: 检查备份的完整性

## 命令详解

### 导出命令

```bash
# 基本导出（自动生成目录名）
./bin/myconfig export

# 导出到指定目录
./bin/myconfig export ./backups/my-backup

# 预览导出内容
./bin/myconfig --preview export

# 非交互模式（自动确认所有操作）
./bin/myconfig -y export

# 试运行（不执行实际操作）
./bin/myconfig --dry-run export

# 详细模式（显示详细日志）
./bin/myconfig -v export
```

**导出内容包括：**
- 环境信息（系统版本、主机名等）
- Homebrew 配置（Brewfile）
- Mac App Store 应用列表
- VS Code 扩展列表
- npm/pip 全局包列表
- dotfiles 和配置文件
- 系统偏好设置 (defaults)
- LaunchAgents 服务

### 恢复命令

```bash
# 基本恢复
./bin/myconfig restore ./backups/backup-xxx

# 预览恢复内容
./bin/myconfig --preview restore ./backups/backup-xxx

# 跳过 Mac App Store 应用
./bin/myconfig --no-mas restore ./backups/backup-xxx
```

**恢复流程：**
1. 验证备份完整性
2. 安装 Homebrew（如未安装）
3. 恢复 brew 包和应用
4. 恢复 dotfiles（自动备份现有文件）
5. 恢复 VS Code 扩展
6. 恢复系统偏好设置
7. 恢复用户服务

### 其他命令

```bash
# 系统诊断
./bin/myconfig doctor

# defaults 相关操作
./bin/myconfig defaults export-all    # 导出所有 defaults 域
./bin/myconfig defaults import <dir>  # 导入 defaults

# 备份管理
./bin/myconfig diff <dir1> <dir2>     # 比较两个备份
./bin/myconfig pack <dir> [file]      # 打包备份

# 配置档案管理
./bin/myconfig profile list           # 列出可用配置
./bin/myconfig profile use <name>     # 使用指定配置
./bin/myconfig profile save <name>    # 保存当前配置
```

## 常用场景

### 场景1：新机器设置

```bash
# 1. 在旧机器上导出配置
./bin/myconfig export ./backup-$(date +%Y%m%d)

# 2. 将备份传输到新机器

# 3. 在新机器上恢复配置
./bin/myconfig restore ./backup-20240101
```

### 场景2：定期备份

```bash
# 创建定期备份脚本
#!/bin/bash
BACKUP_DIR="./backups/backup-$(date +%Y%m%d-%H%M%S)"
./bin/myconfig -y export "$BACKUP_DIR"
echo "备份已保存到: $BACKUP_DIR"
```

### 场景3：配置测试

```bash
# 1. 预览将要导出的内容
./bin/myconfig --preview export

# 2. 试运行模式测试
./bin/myconfig --dry-run export ./test-backup

# 3. 实际导出
./bin/myconfig export ./test-backup
```

### 场景4：最小化配置

```bash
# 1. 使用最小配置档案
./bin/myconfig profile use minimal

# 2. 导出（只包含基本配置）
./bin/myconfig export ./minimal-backup

# 3. 恢复完整配置档案
./bin/myconfig profile use dev-full
```

## 高级功能

### 自定义配置

编辑 `config/config.toml` 文件：

```toml
# 启用/禁用特定功能
enable_vscode = true
enable_mas = false
enable_npm = true

# 自定义 defaults 域
defaults_domains_file = "config/defaults/my-domains.txt"

# 交互模式
interactive = true
```

### 插件扩展

在 `src/plugins/` 目录下创建插件：

```python
# src/plugins/my_plugin.py
def register(subparsers):
    p = subparsers.add_parser("my-cmd", help="自定义命令")
    p.add_argument("arg1")
    # 实现命令逻辑
```

### 配置档案

创建不同用途的配置档案：

```bash
# 保存当前配置为开发环境配置
./bin/myconfig profile save dev-env

# 创建服务器环境配置
./bin/myconfig profile save server-env

# 切换配置
./bin/myconfig profile use server-env
```

## 故障排除

### 常见问题

**1. 权限错误**
```bash
# 确保脚本有执行权限
chmod +x ./bin/myconfig
```

**2. Python 未找到**
```bash
# 安装 Python
brew install python
```

**3. 备份验证失败**
```bash
# 检查备份目录权限和空间
ls -la ./backups/
df -h
```

**4. 恢复中断**
```bash
# 查看日志文件
cat ./logs/run-*.log
```

### 调试技巧

```bash
# 详细模式查看完整日志
./bin/myconfig -v export

# 试运行模式测试命令
./bin/myconfig --dry-run restore ./backup

# 检查系统环境
./bin/myconfig doctor
```

### 获取帮助

```bash
# 查看帮助信息
./bin/myconfig --help

# 查看子命令帮助
./bin/myconfig export --help
./bin/myconfig restore --help
```

## 最佳实践

1. **定期备份**: 建议每周或每月进行一次完整备份
2. **测试恢复**: 定期在测试环境验证备份可用性
3. **版本控制**: 重要配置文件建议额外使用 Git 管理
4. **安全存储**: 备份文件建议加密存储或使用安全的云存储
5. **文档记录**: 记录自定义配置和特殊设置的含义

---

更多信息请参阅其他文档文件或查看项目源码。
