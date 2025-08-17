# 安全特性

## 📋 目录

- [安全原则](#安全原则)
- [敏感文件保护](#敏感文件保护)
- [备份安全](#备份安全)
- [恢复安全](#恢复安全)
- [最佳实践](#最佳实践)

## 安全原则

MyConfig 的设计遵循以下安全原则：

1. **最小权限**: 只备份必要的配置文件，避免过度收集
2. **敏感数据排除**: 自动识别和跳过敏感文件
3. **透明操作**: 详细记录所有操作，支持审计
4. **用户控制**: 提供预览和确认机制
5. **安全传输**: 支持加密打包和安全存储

## 敏感文件保护

### 自动检测机制

MyConfig 内置了智能的敏感文件检测机制，会自动跳过以下类型的文件：

#### SSH 相关文件
```
~/.ssh/id_rsa           # RSA 私钥
~/.ssh/id_dsa           # DSA 私钥
~/.ssh/id_ecdsa         # ECDSA 私钥
~/.ssh/id_ed25519       # Ed25519 私钥
~/.ssh/known_hosts      # 主机指纹
~/.ssh/authorized_keys  # 授权密钥
*.pem                   # PEM 格式密钥
*.key                   # 通用密钥文件
*.p12, *.pfx           # PKCS#12 证书
```

#### GPG 相关文件
```
~/.gnupg/               # 整个 GPG 目录
secring.gpg            # GPG 私钥环
pubring.gpg            # GPG 公钥环
```

#### 密码和认证信息
```
*password*             # 包含 password 的文件
*passwd*               # 包含 passwd 的文件
*secret*               # 包含 secret 的文件
*token*                # 包含 token 的文件
*api_key*              # API 密钥文件
*private_key*          # 私钥文件
*credential*           # 凭据文件
```

#### 历史和缓存文件
```
.bash_history          # Bash 历史
.zsh_history           # Zsh 历史
.history               # 通用历史文件
*cache*                # 缓存目录
.cache/                # 缓存目录
*tmp*                  # 临时文件
.tmp/                  # 临时目录
```

#### 数据库文件
```
*.db                   # 数据库文件
*.sqlite               # SQLite 数据库
*.sqlite3              # SQLite3 数据库
```

#### 应用特定敏感文件
```
~/.aws/credentials     # AWS 凭据
~/.docker/config.json  # Docker 配置（可能含密钥）
*keychain*             # macOS 钥匙串文件
.keychain/             # 钥匙串目录
```

### 检测函数实现

```python
def is_sensitive_file(file_path: str) -> bool:
    """检查文件是否为敏感文件"""
    file_path = file_path.lower()
    
    sensitive_patterns = [
        # SSH 相关
        "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
        ".pem", ".key", ".p12", ".pfx",
        "known_hosts", "authorized_keys",
        
        # GPG 相关
        ".gnupg", "secring.gpg", "pubring.gpg",
        
        # 密码和密钥
        "password", "passwd", "secret", "token",
        "api_key", "private_key", "credential",
        
        # 数据库文件
        ".db", ".sqlite", ".sqlite3",
        
        # 历史文件
        ".history", ".bash_history", ".zsh_history",
        
        # 缓存目录
        "cache", ".cache", "tmp", ".tmp",
        
        # 应用特定
        ".aws/credentials", ".docker/config.json",
        "keychain", ".keychain",
    ]
    
    return any(pattern in file_path for pattern in sensitive_patterns)
```

### 日志记录

当跳过敏感文件时，MyConfig 会记录详细日志：

```bash
# 在 verbose 模式下查看被跳过的文件
./bin/myconfig -v export

# 输出示例：
# ▸ 出于安全考虑跳过 3 个敏感文件
# ▸   跳过: ~/.ssh/id_rsa
# ▸   跳过: ~/.aws/credentials
# ▸   跳过: ~/.bash_history
```

## 备份安全

### 备份完整性验证

每次备份后自动验证：

```python
def verify_backup(backup_dir: str, log: Logger) -> bool:
    """验证备份目录的完整性"""
    # 1. 检查目录存在
    # 2. 验证必要文件
    # 3. 检查备份大小合理性
    # 4. 生成完整性报告
```

### 备份清单生成

自动生成详细的备份清单：

```txt
# MANIFEST.txt 示例
备份创建时间: 20241201-143022
主机名: MacBook-Pro
备份内容清单:
----------------------------------------
  ENVIRONMENT.txt (245 bytes)
  Brewfile (2156 bytes)
  mas.list (892 bytes)
  config/defaults/
    NSGlobalDomain.plist (15234 bytes)
    com.apple.finder.plist (3456 bytes)
  dotfiles.tar.gz (125678 bytes)
  LaunchAgents/
    com.example.service.plist (567 bytes)
```

### 加密支持

```bash
# GPG 对称加密备份
./bin/myconfig pack ./backup-dir backup.zip --gpg

# 这会创建：
# backup.zip      # 原始压缩包
# backup.zip.gpg  # GPG 加密文件
```

## 恢复安全

### 恢复前验证

```bash
# 恢复前自动验证备份
./bin/myconfig restore ./backup-dir

# 输出：
# ▸ 验证备份完整性...
# ✔ 备份验证通过
# 从备份恢复: ./backup-dir
```

### 现有文件保护

恢复时自动备份现有文件：

```bash
# 恢复过程中的文件保护
# 原文件: ~/.zshrc
# 备份为: ~/.zshrc.bak.20241201143022
```

### 分步确认

```bash
# 恢复过程中的用户确认
安装 Homebrew? [y/N]: y
覆盖同名文件（自动备份）? [y/N]: y
开始安装 VS Code 扩展? [y/N]: y
导入并刷新 Dock/Finder? [y/N]: y
```

### 回滚机制

如果恢复失败，可以使用备份的原文件进行回滚：

```bash
# 查找备份文件
find ~ -name "*.bak.20241201*"

# 手动回滚示例
mv ~/.zshrc.bak.20241201143022 ~/.zshrc
```

## 最佳实践

### 1. 定期安全审计

```bash
# 检查敏感文件是否被意外包含
./bin/myconfig --preview export | grep -E "(key|password|secret)"

# 查看详细的跳过列表
./bin/myconfig -v export 2>&1 | grep "跳过"
```

### 2. 备份加密存储

```bash
# 创建加密备份
./bin/myconfig export ./backup-temp
./bin/myconfig pack ./backup-temp encrypted-backup.zip --gpg

# 安全删除临时备份
rm -rf ./backup-temp
```

### 3. 网络传输安全

```bash
# 使用 scp 安全传输
scp encrypted-backup.zip.gpg user@remote-host:~/backups/

# 使用 rsync 增量同步
rsync -av --progress ./backups/ user@remote-host:~/backups/
```

### 4. 访问权限控制

```bash
# 设置备份目录权限（仅所有者可访问）
chmod 700 ./backups/

# 设置配置文件权限
chmod 600 ./config/config.toml
chmod 600 ./config/profiles/*.toml
```

### 5. 定期清理

```bash
# 清理旧备份（保留最近30天）
find ./backups/ -name "backup-*" -mtime +30 -exec rm -rf {} \;

# 清理日志文件（保留最近7天）
find ./logs/ -name "run-*.log" -mtime +7 -delete
```

### 6. 环境隔离

```bash
# 测试环境使用独立配置
cp config/config.toml config-test.toml
# 编辑测试配置...

# 使用测试配置
MYCONFIG_CONFIG=config-test.toml ./bin/myconfig export
```

### 7. 备份验证

```bash
# 定期验证备份完整性
for backup in ./backups/backup-*; do
    echo "验证: $backup"
    ./bin/myconfig --preview restore "$backup" >/dev/null && echo "✓ 正常" || echo "✗ 异常"
done
```

### 8. 敏感信息审查

```bash
# 创建敏感信息检查脚本
#!/bin/bash
check_sensitive() {
    local backup_dir="$1"
    echo "检查敏感信息: $backup_dir"
    
    # 检查是否包含常见敏感模式
    find "$backup_dir" -type f -exec grep -l -E "(password|secret|key|token)" {} \; 2>/dev/null
    
    # 检查是否包含 SSH 密钥
    find "$backup_dir" -name "*id_*" -o -name "*.pem" -o -name "*.key" 2>/dev/null
}

check_sensitive ./backups/backup-latest
```

## 安全配置建议

### 最小权限配置

```toml
# 最安全的配置（最小功能集）
interactive = true          # 确保用户控制
enable_npm = false         # 减少潜在风险
enable_pip_user = false    # 减少潜在风险
enable_pipx = false
enable_defaults = true     # 系统设置相对安全
enable_vscode = false      # 扩展可能包含敏感信息
enable_launchagents = false # 服务配置可能敏感
enable_mas = false         # 减少应用信息泄露
```

### 安全审计配置

```toml
# 启用详细日志用于审计
interactive = true
# ... 其他配置 ...

# 在命令中总是使用 verbose 模式
# ./bin/myconfig -v export
```

---

安全是一个持续的过程，建议定期审查配置和备份内容，确保没有敏感信息泄露。
