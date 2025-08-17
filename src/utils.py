from __future__ import annotations
import os, sys, subprocess, shlex, time, json, pathlib, typing

# 彩色
T1="\033[1m"; DIM="\033[2m"; RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; RST="\033[0m"
def color(c: str, s: str) -> str: return f"{c}{s}{RST}" if sys.stdout.isatty() else s

def which(cmd: str) -> bool:
    return subprocess.call(f"command -v {shlex.quote(cmd)} >/dev/null 2>&1", shell=True)==0

class AppConfig(typing.NamedTuple):
    interactive: bool
    dry_run: bool
    verbose: bool
    quiet: bool
    enable_npm: bool
    enable_pip_user: bool
    enable_pipx: bool
    enable_defaults: bool
    enable_vscode: bool
    enable_launchagents: bool
    enable_mas: bool
    enable_incremental: bool
    base_backup_dir: str
    defaults_domains_file: str
    defaults_exclude_file: str

def _parse_toml(path: str) -> dict:
    data: dict = {}
    if not os.path.exists(path): return data
    try:
        import tomllib  # py311+
        with open(path, "rb") as f: return typing.cast(dict, tomllib.load(f))
    except Exception:
        try:
            import tomli
            with open(path, "rb") as f: return typing.cast(dict, tomli.load(f))
        except Exception:
            # 退化解析：k = v，仅顶层键值
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s=line.strip()
                    if not s or s.startswith("#") or "=" not in s: continue
                    k,v = s.split("=",1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
            return data

def load_config(path: str) -> AppConfig:
    d = _parse_toml(path)
    def g(k, dv): return d.get(k, dv)
    return AppConfig(
        interactive = str(g("interactive", "true")).lower()=="true",
        dry_run      = False,
        verbose      = False,
        quiet        = False,
        enable_npm   = str(g("enable_npm","false")).lower()=="true",
        enable_pip_user = str(g("enable_pip_user","false")).lower()=="true",
        enable_pipx  = str(g("enable_pipx","false")).lower()=="true",
        enable_defaults = str(g("enable_defaults","true")).lower()=="true",
        enable_vscode   = str(g("enable_vscode","true")).lower()=="true",
        enable_launchagents = str(g("enable_launchagents","true")).lower()=="true",
        enable_mas     = str(g("enable_mas","true")).lower()=="true",
        enable_incremental = str(g("enable_incremental","false")).lower()=="true",
        base_backup_dir = str(g("base_backup_dir","")),
        defaults_domains_file = str(g("defaults_domains_file","config/defaults/domains.txt")),
        defaults_exclude_file = str(g("defaults_exclude_file","config/defaults/exclude.txt")),
    )

class Logger:
    def __init__(self, cfg: AppConfig):
        ts = time.strftime("%Y%m%d-%H%M%S")
        pathlib.Path("./logs").mkdir(parents=True, exist_ok=True)
        self.path = f"./logs/run-{ts}.log"
        self.cfg = cfg
    def _write(self, s: str, err: bool=False):
        mode = "a"
        with open(self.path, mode, encoding="utf-8") as f: f.write(s + ("\n" if not s.endswith("\n") else ""))
        if not self.cfg.quiet:
            (sys.stderr if err else sys.stdout).write(s + ("\n" if not s.endswith("\n") else ""))
    def info(self, s: str): self._write(color(BLUE, "▸ ")+s)
    def ok(self, s: str):   self._write(color(GREEN, "✔ ")+s)
    def warn(self, s: str): self._write(color(YELLOW,"⚠ ")+s)
    def err(self, s: str):  self._write(color(RED,   "✖ ")+s, err=True)
    def hr(self):           self._write(color(DIM, "─"*60))
    def sec(self, s: str):  self._write(color(T1, s))
    def confirm(self, prompt: str) -> bool:
        if not self.cfg.interactive: return True
        self._write(prompt + " [y/N]: ")
        try:
            ans = input().strip().lower()
        except EOFError:
            return False
        return ans in ("y","yes")

def run(cmd: str, log: Logger, check: bool=True, description: str=""):
    if log.cfg.dry_run:
        desc_text = f" ({description})" if description else ""
        log._write(f"[dry-run]{desc_text} {cmd}")
        return 0
    if log.cfg.verbose: log._write(color(DIM, f"$ {cmd}"))
    try:
        rc = subprocess.call(cmd, shell=True)
        if check and rc != 0:
            desc_text = f" ({description})" if description else ""
            log.err(f"Command failed{desc_text} (exit code: {rc}): {cmd}")
            raise SystemExit(rc)
        return rc
    except KeyboardInterrupt:
        log.warn("Operation interrupted by user")
        raise SystemExit(130)
    except Exception as e:
        log.err(f"Exception occurred while executing command: {e}")
        if check:
            raise SystemExit(1)
        return 1

def run_out(cmd: str) -> tuple[int,str]:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return 0, out.decode("utf-8","ignore")
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode("utf-8","ignore")

def ts() -> str: return time.strftime("%Y%m%d-%H%M%S")
def host() -> str:
    rc, out = run_out("scutil --get ComputerName 2>/dev/null || hostname")
    return out.strip() if rc==0 else "mac"

def verify_backup(backup_dir: str, log: Logger) -> bool:
    """验证备份目录的完整性"""
    if not os.path.isdir(backup_dir):
        log.err(f"Backup directory does not exist: {backup_dir}")
        return False
    
    # 检查必要文件
    required_files = ["ENVIRONMENT.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(backup_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        log.warn(f"Backup incomplete, missing files: {', '.join(missing_files)}")
        return False
    
    # 检查备份大小（基本健全性检查）
    try:
        total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(backup_dir)
                        for filename in filenames)
        if total_size < 1024:  # 小于1KB可能有问题
            log.warn(f"Backup size unusually small: {total_size} bytes")
            return False
    except Exception as e:
        log.warn(f"Cannot calculate backup size: {e}")
    
    log.ok("Backup verification passed")
    return True

def create_backup_manifest(backup_dir: str, log: Logger):
    """创建备份清单文件"""
    manifest_file = os.path.join(backup_dir, "MANIFEST.txt")
    try:
        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write(f"Backup created: {ts()}\n")
            f.write(f"Hostname: {host()}\n")
            f.write("Backup manifest:\n")
            f.write("-" * 40 + "\n")
            
            for root, dirs, files in os.walk(backup_dir):
                level = root.replace(backup_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                f.write(f"{indent}{os.path.basename(root)}/\n")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    if file != "MANIFEST.txt":  # 避免自引用
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        f.write(f"{subindent}{file} ({size} bytes)\n")
        log.ok("Backup manifest created")
    except Exception as e:
        log.warn(f"Failed to create backup manifest: {e}")

def is_sensitive_file(file_path: str) -> bool:
    """检查文件是否为敏感文件"""
    file_path = file_path.lower()
    
    # 敏感文件模式
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

def get_secure_dotfile_list(log: Logger) -> list[str]:
    """获取经过安全过滤的 dotfiles 列表"""
    from .actions.export import DOT_LIST
    
    safe_dotfiles = []
    skipped_files = []
    
    for pattern in DOT_LIST:
        expanded = os.path.expanduser(pattern)
        if os.path.exists(expanded):
            if is_sensitive_file(expanded):
                skipped_files.append(pattern)
            else:
                safe_dotfiles.append(pattern)
    
    if skipped_files:
        log.info(f"Skipped {len(skipped_files)} sensitive files for security")
        if log.cfg.verbose:
            for skip in skipped_files:
                log.info(f"  Skipped: {skip}")
    
    return safe_dotfiles

class ProgressTracker:
    """简单的进度跟踪器"""
    def __init__(self, total: int, log: Logger, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.log = log
        self.description = description
        self.log.info(f"{description}: 0/{total}")
    
    def update(self, step_description: str = ""):
        self.current += 1
        progress = f"{self.current}/{self.total}"
        if step_description:
            self.log.info(f"{self.description}: {progress} - {step_description}")
        else:
            self.log.info(f"{self.description}: {progress}")
    
    def finish(self):
        self.log.ok(f"{self.description} completed: {self.total}/{self.total}")
