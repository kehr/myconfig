from __future__ import annotations
import os, sys, subprocess, shlex, time, json, pathlib, typing, logging
from .logger import log_success

# Handle TOML library imports
try:
    import tomllib  # py311+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("tomli library required: pip install tomli")

# Colors
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
        with open(path, "rb") as f: return typing.cast(dict, tomllib.load(f))
    except Exception:
        # Fallback parsing: k = v, top-level key-value only
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



def run(cmd: str, cfg: AppConfig, check: bool=True, description: str=""):
    logger = logging.getLogger(__name__)
    
    if cfg.dry_run:
        desc_text = f" ({description})" if description else ""
        logger.info(f"[dry-run]{desc_text} {cmd}")
        return 0
    
    if cfg.verbose: 
        logger.debug(f"$ {cmd}")
    
    try:
        rc = subprocess.call(cmd, shell=True)
        if check and rc != 0:
            desc_text = f" ({description})" if description else ""
            logger.error(f"Command failed{desc_text} (exit code: {rc}): {cmd}")
            raise SystemExit(rc)
        return rc
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user")
        raise SystemExit(130)
    except Exception as e:
        logger.error(f"Exception occurred while executing command: {e}")
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

def verify_backup(backup_dir: str) -> bool:
    """Verify backup directory integrity"""
    if not os.path.isdir(backup_dir):
        logger = logging.getLogger(__name__)
        logger.error(f"Backup directory does not exist: {backup_dir}")
        return False
    
    # Check required files
    required_files = ["ENVIRONMENT.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(backup_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        logger = logging.getLogger(__name__)
        logger.warning(f"Backup incomplete, missing files: {', '.join(missing_files)}")
        return False
    
    # Check backup size (basic sanity check)
    try:
        total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(backup_dir)
                        for filename in filenames)
        if total_size < 1024:  # Less than 1KB might be problematic
            logger = logging.getLogger(__name__)
            logger.warning(f"Backup size unusually small: {total_size} bytes")
            return False
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Cannot calculate backup size: {e}")
    
    logger = logging.getLogger(__name__)
    log_success(logger, "Backup verification passed")
    return True

def create_backup_manifest(backup_dir: str):
    """Create backup manifest file"""
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
                    if file != "MANIFEST.txt":  # Avoid self-reference
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        f.write(f"{subindent}{file} ({size} bytes)\n")
        logger = logging.getLogger(__name__)
        log_success(logger, "Backup manifest created")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to create backup manifest: {e}")

def is_sensitive_file(file_path: str) -> bool:
    """Check if file is sensitive"""
    file_path = file_path.lower()
    
    # Sensitive file patterns
    sensitive_patterns = [
        # SSH related
        "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
        ".pem", ".key", ".p12", ".pfx",
        "known_hosts", "authorized_keys",
        
        # GPG related
        ".gnupg", "secring.gpg", "pubring.gpg",
        
        # Passwords and keys
        "password", "passwd", "secret", "token",
        "api_key", "private_key", "credential",
        
        # Database files
        ".db", ".sqlite", ".sqlite3",
        
        # History files
        ".history", ".bash_history", ".zsh_history",
        
        # Cache directories
        "cache", ".cache", "tmp", ".tmp",
        
        # Application specific
        ".aws/credentials", ".docker/config.json",
        "keychain", ".keychain",
    ]
    
    return any(pattern in file_path for pattern in sensitive_patterns)

def get_secure_dotfile_list() -> list[str]:
    """Get security-filtered dotfiles list"""
    # Import DOT_LIST here to avoid circular imports
    DOT_LIST = [
        "~/.zshrc","~/.zprofile","~/.bashrc","~/.bash_profile","~/.profile",
        "~/.gitconfig","~/.gitignore_global","~/.vimrc","~/.tmux.conf","~/.screenrc",
        "~/.ssh/config","~/.config/iterm2","~/.config/git","~/.config/ssh",
        "~/.config/zsh","~/.config/nvim","~/.config/vim","~/.config/tmux"
    ]
    
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
        logger = logging.getLogger(__name__)
        logger.info(f"Skipped {len(skipped_files)} sensitive files for security")
        for skip in skipped_files:
            logger.debug(f"  Skipped: {skip}")
    
    return safe_dotfiles

class ProgressTracker:
    """Simple progress tracker"""
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{description}: 0/{total}")
    
    def update(self, step_description: str = ""):
        self.current += 1
        progress = f"{self.current}/{self.total}"
        if step_description:
            self.logger.info(f"{self.description}: {progress} - {step_description}")
        else:
            self.logger.info(f"{self.description}: {progress}")
    
    def finish(self):
        log_success(self.logger, f"{self.description} completed: {self.total}/{self.total}")
