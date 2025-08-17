# 插件开发指南

## 📋 目录

- [插件系统概述](#插件系统概述)
- [创建插件](#创建插件)
- [插件API](#插件api)
- [示例插件](#示例插件)
- [最佳实践](#最佳实践)

## 插件系统概述

MyConfig 支持通过插件扩展功能。插件系统的特点：

- **自动发现**: 放在 `src/plugins/` 目录下的 Python 文件会被自动加载
- **命令注册**: 插件可以注册新的子命令
- **配置访问**: 插件可以访问全局配置和日志系统
- **工具函数**: 可以使用 MyConfig 提供的工具函数

## 创建插件

### 基本结构

在 `src/plugins/` 目录下创建 Python 文件：

```python
# src/plugins/my_plugin.py

def register(subparsers):
    """
    插件注册函数 - 必须实现
    
    Args:
        subparsers: argparse 的子解析器对象
    """
    # 创建子命令
    parser = subparsers.add_parser("my-command", help="我的自定义命令")
    
    # 添加参数
    parser.add_argument("target", help="目标参数")
    parser.add_argument("--option", help="可选参数")
    
    # 设置执行函数
    parser.set_defaults(func=execute)

def execute(args):
    """
    命令执行函数
    
    Args:
        args: 解析后的命令行参数
    """
    print(f"执行自定义命令: {args.target}")
    if args.option:
        print(f"选项: {args.option}")
```

### 高级插件结构

```python
# src/plugins/advanced_plugin.py

import os
from ..utils import AppConfig, Logger, run, run_out

def register(subparsers):
    """注册插件命令"""
    parser = subparsers.add_parser("sync", help="同步配置到远程服务器")
    parser.add_argument("remote", help="远程服务器地址")
    parser.add_argument("--port", type=int, default=22, help="SSH 端口")
    parser.add_argument("--dry-run", action="store_true", help="试运行")
    parser.set_defaults(func=sync_command)

def sync_command(args):
    """同步命令实现"""
    # 获取配置和日志对象
    from ..utils import load_config, Logger
    
    cfg = load_config("./config/config.toml")
    log = Logger(cfg)
    
    log.sec(f"同步配置到 {args.remote}")
    
    if args.dry_run:
        log.info("[试运行] 将执行以下操作:")
        log.info(f"  - 连接到 {args.remote}:{args.port}")
        log.info(f"  - 上传配置文件")
        return
    
    # 实际同步逻辑
    try:
        sync_configs(args.remote, args.port, log)
        log.ok("同步完成")
    except Exception as e:
        log.err(f"同步失败: {e}")

def sync_configs(remote, port, log):
    """实际同步逻辑"""
    # 创建临时备份
    log.info("创建临时备份...")
    run("./bin/myconfig export /tmp/sync-backup", log)
    
    # 上传到远程服务器
    log.info(f"上传到 {remote}...")
    run(f"scp -P {port} -r /tmp/sync-backup {remote}:~/myconfig-sync/", log)
    
    # 清理临时文件
    run("rm -rf /tmp/sync-backup", log)
```

## 插件API

### 可用的工具函数

```python
from ..utils import (
    AppConfig,          # 配置类
    Logger,             # 日志类
    run,                # 执行命令
    run_out,            # 执行命令并获取输出
    which,              # 检查命令是否存在
    ts,                 # 获取时间戳
    host,               # 获取主机名
    verify_backup,      # 验证备份
    create_backup_manifest,  # 创建备份清单
    is_sensitive_file,  # 检查敏感文件
    ProgressTracker,    # 进度跟踪器
)
```

### 配置访问

```python
def my_function():
    # 加载配置
    from ..utils import load_config
    cfg = load_config("./config/config.toml")
    
    # 访问配置项
    if cfg.enable_vscode:
        print("VS Code 功能已启用")
    
    # 创建日志对象
    log = Logger(cfg)
    log.info("插件开始执行")
```

### 命令执行

```python
def execute_command(log):
    # 执行命令（会记录到日志）
    run("brew list", log)
    
    # 执行命令并获取输出
    rc, output = run_out("git status")
    if rc == 0:
        log.info(f"Git 状态: {output}")
    else:
        log.warn("不是 Git 仓库")
```

### 进度跟踪

```python
def long_operation(log):
    # 创建进度跟踪器
    progress = ProgressTracker(5, log, "处理进度")
    
    # 更新进度
    progress.update("准备工作")
    time.sleep(1)
    
    progress.update("下载文件")
    time.sleep(2)
    
    progress.update("处理数据")
    time.sleep(1)
    
    progress.update("上传结果")
    time.sleep(1)
    
    progress.update("清理工作")
    time.sleep(0.5)
    
    progress.finish()
```

## 示例插件

### 1. Git 仓库管理插件

```python
# src/plugins/git_manager.py

import os
import json
from ..utils import AppConfig, Logger, run, run_out

def register(subparsers):
    parser = subparsers.add_parser("git", help="Git 仓库管理")
    git_sub = parser.add_subparsers(dest="git_cmd")
    
    # 列出所有 Git 仓库
    list_parser = git_sub.add_parser("list", help="列出所有 Git 仓库")
    list_parser.add_argument("--path", default="~", help="搜索路径")
    
    # 备份 Git 仓库信息
    backup_parser = git_sub.add_parser("backup", help="备份 Git 仓库信息")
    backup_parser.add_argument("output", help="输出文件")
    
    # 恢复 Git 仓库
    restore_parser = git_sub.add_parser("restore", help="恢复 Git 仓库")
    restore_parser.add_argument("input", help="备份文件")
    
    parser.set_defaults(func=git_command)

def git_command(args):
    from ..utils import load_config, Logger
    
    cfg = load_config("./config/config.toml")
    log = Logger(cfg)
    
    if args.git_cmd == "list":
        list_repositories(args.path, log)
    elif args.git_cmd == "backup":
        backup_repositories(args.output, log)
    elif args.git_cmd == "restore":
        restore_repositories(args.input, log)
    else:
        log.err("未知的 git 子命令")

def list_repositories(search_path, log):
    """列出所有 Git 仓库"""
    log.sec("搜索 Git 仓库")
    
    search_path = os.path.expanduser(search_path)
    repos = []
    
    for root, dirs, files in os.walk(search_path):
        if '.git' in dirs:
            repos.append(root)
            # 不再进入 .git 目录
            dirs.remove('.git')
    
    log.info(f"找到 {len(repos)} 个 Git 仓库:")
    for repo in repos:
        # 获取仓库信息
        rc, remote = run_out(f"cd '{repo}' && git remote get-url origin 2>/dev/null")
        if rc == 0:
            log.info(f"  {repo} -> {remote.strip()}")
        else:
            log.info(f"  {repo} (无远程仓库)")

def backup_repositories(output_file, log):
    """备份 Git 仓库信息"""
    log.sec("备份 Git 仓库信息")
    
    repos_info = []
    
    # 搜索仓库
    for root, dirs, files in os.walk(os.path.expanduser("~")):
        if '.git' in dirs:
            repo_info = {"path": root}
            
            # 获取远程仓库信息
            rc, remote = run_out(f"cd '{root}' && git remote get-url origin 2>/dev/null")
            if rc == 0:
                repo_info["remote"] = remote.strip()
            
            # 获取当前分支
            rc, branch = run_out(f"cd '{root}' && git branch --show-current 2>/dev/null")
            if rc == 0:
                repo_info["branch"] = branch.strip()
            
            # 检查是否有未提交的更改
            rc, status = run_out(f"cd '{root}' && git status --porcelain 2>/dev/null")
            repo_info["has_changes"] = (rc == 0 and status.strip() != "")
            
            repos_info.append(repo_info)
            dirs.remove('.git')
    
    # 保存到文件
    with open(output_file, 'w') as f:
        json.dump(repos_info, f, indent=2)
    
    log.ok(f"已保存 {len(repos_info)} 个仓库信息到 {output_file}")

def restore_repositories(input_file, log):
    """恢复 Git 仓库"""
    log.sec("恢复 Git 仓库")
    
    with open(input_file, 'r') as f:
        repos_info = json.load(f)
    
    for repo in repos_info:
        if 'remote' in repo:
            path = repo['path']
            remote = repo['remote']
            
            if not os.path.exists(path):
                log.info(f"克隆 {remote} 到 {path}")
                parent_dir = os.path.dirname(path)
                repo_name = os.path.basename(path)
                
                os.makedirs(parent_dir, exist_ok=True)
                run(f"cd '{parent_dir}' && git clone '{remote}' '{repo_name}'", log, check=False)
            else:
                log.info(f"仓库已存在: {path}")
    
    log.ok("仓库恢复完成")
```

### 2. 系统信息收集插件

```python
# src/plugins/sysinfo.py

import platform
import subprocess
from datetime import datetime
from ..utils import run_out

def register(subparsers):
    parser = subparsers.add_parser("sysinfo", help="系统信息收集")
    parser.add_argument("--output", help="输出文件")
    parser.add_argument("--format", choices=["txt", "json"], default="txt", help="输出格式")
    parser.set_defaults(func=collect_sysinfo)

def collect_sysinfo(args):
    from ..utils import load_config, Logger
    
    cfg = load_config("./config/config.toml")
    log = Logger(cfg)
    
    log.sec("收集系统信息")
    
    info = {}
    
    # 基本系统信息
    info['timestamp'] = datetime.now().isoformat()
    info['platform'] = platform.platform()
    info['python_version'] = platform.python_version()
    info['architecture'] = platform.architecture()
    
    # macOS 特定信息
    rc, sw_vers = run_out("sw_vers")
    if rc == 0:
        info['macos_version'] = sw_vers.strip()
    
    # 硬件信息
    rc, system_profiler = run_out("system_profiler SPHardwareDataType")
    if rc == 0:
        info['hardware'] = system_profiler.strip()
    
    # 安装的开发工具
    tools = {}
    for tool in ['brew', 'git', 'python3', 'node', 'npm', 'docker']:
        rc, version = run_out(f"{tool} --version 2>/dev/null | head -1")
        if rc == 0:
            tools[tool] = version.strip()
    info['dev_tools'] = tools
    
    # 输出结果
    if args.format == "json":
        import json
        output = json.dumps(info, indent=2)
    else:
        output = format_text_output(info)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        log.ok(f"系统信息已保存到 {args.output}")
    else:
        print(output)

def format_text_output(info):
    """格式化文本输出"""
    lines = []
    lines.append("=== 系统信息 ===")
    lines.append(f"收集时间: {info['timestamp']}")
    lines.append(f"平台: {info['platform']}")
    lines.append(f"Python: {info['python_version']}")
    lines.append(f"架构: {info['architecture']}")
    
    if 'macos_version' in info:
        lines.append("\n=== macOS 版本 ===")
        lines.append(info['macos_version'])
    
    if 'dev_tools' in info:
        lines.append("\n=== 开发工具 ===")
        for tool, version in info['dev_tools'].items():
            lines.append(f"{tool}: {version}")
    
    return "\n".join(lines)
```

### 3. 云同步插件

```python
# src/plugins/cloud_sync.py

import os
import tempfile
from ..utils import AppConfig, Logger, run, ProgressTracker

def register(subparsers):
    parser = subparsers.add_parser("cloud", help="云同步功能")
    cloud_sub = parser.add_subparsers(dest="cloud_cmd")
    
    # 上传到云存储
    upload_parser = cloud_sub.add_parser("upload", help="上传备份到云存储")
    upload_parser.add_argument("backup_dir", help="备份目录")
    upload_parser.add_argument("--provider", choices=["s3", "gdrive"], default="s3")
    upload_parser.add_argument("--encrypt", action="store_true", help="加密上传")
    
    # 从云存储下载
    download_parser = cloud_sub.add_parser("download", help="从云存储下载备份")
    download_parser.add_argument("backup_name", help="备份名称")
    download_parser.add_argument("--provider", choices=["s3", "gdrive"], default="s3")
    
    parser.set_defaults(func=cloud_command)

def cloud_command(args):
    from ..utils import load_config, Logger
    
    cfg = load_config("./config/config.toml")
    log = Logger(cfg)
    
    if args.cloud_cmd == "upload":
        upload_backup(args.backup_dir, args.provider, args.encrypt, log)
    elif args.cloud_cmd == "download":
        download_backup(args.backup_name, args.provider, log)
    else:
        log.err("未知的 cloud 子命令")

def upload_backup(backup_dir, provider, encrypt, log):
    """上传备份到云存储"""
    log.sec(f"上传备份到 {provider}")
    
    progress = ProgressTracker(4, log, "上传进度")
    
    # 1. 验证备份
    from ..utils import verify_backup
    if not verify_backup(backup_dir, log):
        log.err("备份验证失败，停止上传")
        return
    progress.update("备份验证完成")
    
    # 2. 打包备份
    backup_name = os.path.basename(backup_dir.rstrip('/'))
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, f"{backup_name}.tar.gz")
        run(f"tar -czf '{archive_path}' -C '{os.path.dirname(backup_dir)}' '{backup_name}'", log)
        progress.update("备份打包完成")
        
        # 3. 加密（如果需要）
        if encrypt:
            run(f"gpg -c '{archive_path}'", log)
            archive_path += ".gpg"
            progress.update("备份加密完成")
        else:
            progress.update("跳过加密")
        
        # 4. 上传
        if provider == "s3":
            upload_to_s3(archive_path, backup_name, log)
        elif provider == "gdrive":
            upload_to_gdrive(archive_path, backup_name, log)
        
        progress.update("上传完成")
    
    progress.finish()

def upload_to_s3(file_path, backup_name, log):
    """上传到 AWS S3"""
    bucket = os.getenv("MYCONFIG_S3_BUCKET", "myconfig-backups")
    run(f"aws s3 cp '{file_path}' s3://{bucket}/{backup_name}/", log)

def upload_to_gdrive(file_path, backup_name, log):
    """上传到 Google Drive"""
    # 需要安装 gdrive 工具
    run(f"gdrive upload '{file_path}'", log)

def download_backup(backup_name, provider, log):
    """从云存储下载备份"""
    log.sec(f"从 {provider} 下载备份")
    
    # 实现下载逻辑...
    pass
```

## 最佳实践

### 1. 错误处理

```python
def safe_execute(func, log, *args, **kwargs):
    """安全执行函数，处理异常"""
    try:
        return func(*args, **kwargs)
    except KeyboardInterrupt:
        log.warn("操作被用户中断")
        return False
    except Exception as e:
        log.err(f"执行失败: {e}")
        return False
```

### 2. 配置验证

```python
def validate_config(cfg, log):
    """验证插件所需的配置"""
    required_settings = ['api_key', 'endpoint']
    
    for setting in required_settings:
        if not hasattr(cfg, setting) or not getattr(cfg, setting):
            log.err(f"缺少必需的配置: {setting}")
            return False
    
    return True
```

### 3. 日志最佳实践

```python
def my_plugin_function(log):
    log.sec("开始插件操作")
    
    try:
        log.info("执行步骤 1")
        # ... 代码 ...
        
        log.info("执行步骤 2")
        # ... 代码 ...
        
        log.ok("插件操作完成")
    except Exception as e:
        log.err(f"插件操作失败: {e}")
        raise
```

### 4. 依赖检查

```python
def check_dependencies(log):
    """检查插件依赖"""
    required_commands = ['git', 'aws', 'gpg']
    
    for cmd in required_commands:
        from ..utils import which
        if not which(cmd):
            log.err(f"缺少必需的命令: {cmd}")
            return False
    
    return True
```

### 5. 插件文档

```python
"""
MyConfig Git 管理插件

提供 Git 仓库的备份和恢复功能。

命令:
    myconfig git list [--path PATH]     # 列出 Git 仓库
    myconfig git backup OUTPUT          # 备份仓库信息
    myconfig git restore INPUT          # 恢复仓库

依赖:
    - git 命令行工具
    - 网络连接（用于克隆）

配置:
    无特殊配置要求

示例:
    ./bin/myconfig git list --path ~/Projects
    ./bin/myconfig git backup git-repos.json
    ./bin/myconfig git restore git-repos.json
"""
```

---

通过插件系统，你可以轻松扩展 MyConfig 的功能，满足特定的配置管理需求。插件与核心系统共享相同的日志、配置和工具函数，确保一致的用户体验。
