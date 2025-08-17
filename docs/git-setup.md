# Git 配置说明

本项目已经配置了优化的 Git 设置，以下是配置的详细说明。

## 📁 Git 配置文件

### .gitignore
包含以下忽略规则：

**项目特定**
- `backups/` - 用户备份数据，不应该提交
- `logs/` - 运行日志，临时文件
- `*.log` - 所有日志文件

**Python 相关**
- `__pycache__/` - Python 缓存
- `*.py[cod]` - Python 编译文件
- `*.egg-info/` - Python 包信息

**IDE 和编辑器**
- `.vscode/` - VS Code 配置
- `.idea/` - JetBrains IDE 配置
- `*.swp`, `*.swo` - Vim 临时文件

**敏感文件**
- `config.local.toml` - 本地配置
- `.env*` - 环境变量文件
- `*.pem`, `*.key` - 证书和密钥文件

**系统文件**
- `.DS_Store` - macOS 系统文件
- `Thumbs.db` - Windows 缩略图

### .gitattributes
配置文件类型和行尾符处理：

**文本文件自动检测**
```
* text=auto
```

**明确标记的文本文件**
- Shell 脚本使用 LF 行尾符
- Python 文件启用 Python diff
- Markdown 文件启用 Markdown diff

**二进制文件标记**
- 图片、压缩包等标记为二进制

### .gitmessage
提交消息模板，包含：
- 标题行格式（50字符内）
- 正文格式（72字符换行）
- 提交类型参考
- 示例格式

## ⚙️ Git 本地配置

项目已设置以下本地配置：

```bash
# 行尾符处理
core.autocrlf=input          # 检出时保持LF，提交时转换CRLF为LF
core.safecrlf=warn           # 行尾符转换警告

# 编辑器
core.editor="code --wait"    # 使用 VS Code 作为默认编辑器

# 拉取策略
pull.rebase=false           # 使用 merge 而不是 rebase

# 默认分支
init.defaultbranch=main     # 新仓库默认使用 main 分支

# 提交模板
commit.template=.gitmessage # 使用自定义提交模板
```

## 🔗 Git 别名

项目配置了以下便捷别名：

```bash
git st        # 等同于 git status --short --branch
git co        # 等同于 git checkout
git br        # 等同于 git branch
git ci        # 等同于 git commit
git lg        # 美化的图形化日志
git unstage   # 等同于 git reset HEAD --
```

**使用示例：**
```bash
# 查看简洁状态
git st

# 查看美化日志
git lg

# 取消暂存文件
git unstage filename
```

## 🔒 Pre-commit Hook

自动执行的提交前检查：

**安全检查**
- 检测敏感文件模式（密钥、密码等）
- 阻止意外提交敏感信息

**代码质量检查**
- Python 语法检查
- 调试代码检测（警告）
- 大文件检测（1MB+）

**文件权限检查**
- 检查 Python 文件的可执行权限

## 📝 推荐的工作流程

### 1. 日常开发
```bash
# 查看状态
git st

# 添加文件
git add .

# 提交（会触发 pre-commit hook）
git ci

# 推送
git push
```

### 2. 提交消息规范
遵循提交模板格式：
```
feat: 添加新功能的简洁描述

详细说明为什么需要这个功能，如何实现的，
解决了什么问题。

Fixes #123
```

### 3. 分支管理
```bash
# 创建功能分支
git co -b feature/新功能

# 合并到主分支
git co main
git merge feature/新功能
```

## 🔧 自定义配置

如果需要修改配置，可以：

**修改忽略规则**
编辑 `.gitignore` 文件

**修改提交模板**
编辑 `.gitmessage` 文件

**添加新的别名**
```bash
git config alias.新别名 "完整命令"
```

**修改 pre-commit hook**
编辑 `.git/hooks/pre-commit` 文件

## ✅ 配置验证

检查配置是否正确：

```bash
# 查看本地配置
git config --list --local

# 测试别名
git st

# 测试提交模板
git ci --dry-run

# 测试 pre-commit hook
git add . && git ci -m "test"
```

---

这些配置旨在提高开发效率、保证代码质量和防止敏感信息泄露。如有需要，可以根据项目需求进行调整。
