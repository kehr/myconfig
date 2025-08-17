from __future__ import annotations
import os
from ..utils import AppConfig, Logger, run, run_out, which, verify_backup

def do_restore(cfg: AppConfig, log: Logger, srcdir: str):
    if not srcdir or not os.path.isdir(srcdir):
        log.err(f"Backup directory does not exist: {srcdir}"); return
    
    # Verify backup integrity
    log.info("Verifying backup integrity...")
    if not verify_backup(srcdir, log):
        if not log.confirm("Backup verification failed, continue with restore?"):
            log.warn("Restore operation cancelled")
            return
    
    log.sec(f"Restoring from backup: {srcdir}"); log.hr()

    # brew
    if not which("brew"):
        log.sec("Install Homebrew")
        if log.confirm("Install Homebrew?"):
            run('NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', log, check=False)
    brewfile = os.path.join(srcdir, "Brewfile")
    if os.path.exists(brewfile):
        if log.confirm("Execute brew bundle install?"):
            run(f'brew bundle --file="{brewfile}"', log, check=False)

    # mas
    mlist = os.path.join(srcdir, "mas.list")
    if cfg.enable_mas and os.path.exists(mlist):
        if not which("mas"): run("brew install mas", log, check=False)
        log.sec("Restore Mac App Store apps"); log.warn("Please login to App Store first")
        if log.confirm("Install MAS list now?"):
            run(f'awk \'{{print $1}}\' "{mlist}" | while read -r id; do [[ -z "$id" ]] || mas install "$id" || true; done', log, check=False)

    # dotfiles
    dotball = os.path.join(srcdir, "dotfiles.tar.gz")
    if os.path.exists(dotball):
        log.sec("Restore dotfiles to $HOME")
        if log.confirm("Overwrite existing files (auto backup)?"):
            run('TMP_DOT="$(mktemp -d)" && '
                f'tar -xzf "{dotball}" -C "$TMP_DOT" && '
                '(cd "$TMP_DOT" && find . -type f -print0) | while IFS= read -r -d "" item; do '
                'dst="$HOME/${item#./}"; [[ -e "$dst" ]] && cp -a "$dst" "${dst}.bak.$(date +%Y%m%d%H%M%S)"; '
                'done && rsync -av "$TMP_DOT"/ "$HOME"/ && rm -rf "$TMP_DOT"', log, check=False)

    # vscode
    vxt = os.path.join(srcdir, "vscode_extensions.txt")
    if cfg.enable_vscode and os.path.exists(vxt) and which("code"):
        log.sec("Install VS Code extensions")
        if log.confirm("Start installing VS Code extensions?"):
            run(f'while read -r ext; do [[ -z "$ext" ]] || code --install-extension "$ext" || true; done < "{vxt}"', log, check=False)

    # npm/pip/pipx
    if cfg.enable_npm and os.path.exists(os.path.join(srcdir,"npm_globals.txt")) and which("npm"):
        log.sec("npm global packages")
        if log.confirm("Install npm global packages?"):
            run(f'xargs -I{{}} npm -g install {{}} < "{os.path.join(srcdir,"npm_globals.txt")}"', log, check=False)
    if cfg.enable_pip_user and os.path.exists(os.path.join(srcdir,"pip_user_freeze.txt")) and which("pip"):
        log.sec("pip --user packages")
        if log.confirm("pip --user install requirements?"):
            run(f'pip install --user -r "{os.path.join(srcdir,"pip_user_freeze.txt")}"', log, check=False)

    # defaults
    defdir = os.path.join(srcdir, "defaults")
    if cfg.enable_defaults and os.path.isdir(defdir):
        log.sec("Import defaults")
        if log.confirm("Import and refresh Dock/Finder?"):
            run('for p in "'+defdir+'"/*.plist; do [[ -e "$p" ]] || continue; '
                'd="$(basename "$p" .plist)"; '
                'defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${d}_$(date +%Y%m%d%H%M%S).plist" || true; '
                'defaults import "$d" "$p" || true; '
                'done; killall Dock 2>/dev/null || true; killall Finder 2>/dev/null || true', log, check=False)

    # LaunchAgents
    la = os.path.join(srcdir, "LaunchAgents")
    if cfg.enable_launchagents and os.path.isdir(la):
        log.sec("Restore LaunchAgents")
        run('mkdir -p "$HOME/Library/LaunchAgents"', log, check=False)
        run(f'cp -a "{la}"/*.plist "$HOME/Library/LaunchAgents/" 2>/dev/null || true', log, check=False)
        if log.confirm("Load LaunchAgents?"):
            run('find "$HOME/Library/LaunchAgents" -name "*.plist" -print0 | while IFS= read -r -d "" f; do launchctl load -w "$f" 2>/dev/null || true; done', log, check=False)

    log.hr(); log.ok("Restore completed")

def preview_restore(cfg: AppConfig, log: Logger, srcdir: str):
    """Preview what the restore operation will do"""
    if not srcdir or not os.path.isdir(srcdir):
        log.err(f"Backup directory does not exist: {srcdir}"); return
    
    log.sec(f"Preview restore operation ← {srcdir}"); log.hr()
    
    # Check backup content
    log.info("Backup content analysis:")
    
    # Check various files
    brewfile = os.path.join(srcdir, "Brewfile")
    if os.path.exists(brewfile):
        try:
            with open(brewfile, 'r') as f:
                lines = f.readlines()
            brew_count = len([l for l in lines if l.strip().startswith('brew ')])
            cask_count = len([l for l in lines if l.strip().startswith('cask ')])
            vscode_count = len([l for l in lines if l.strip().startswith('vscode ')])
            log.info(f"  ✓ Homebrew: {brew_count} packages, {cask_count} apps, {vscode_count} VS Code extensions")
        except:
            log.info("  ✓ Homebrew config file")
    else:
        log.warn("  ✗ No Homebrew config")
    
    mlist = os.path.join(srcdir, "mas.list")
    if os.path.exists(mlist):
        try:
            with open(mlist, 'r') as f:
                mas_apps = len(f.readlines())
            log.info(f"  ✓ Mac App Store: {mas_apps} apps")
        except:
            log.info("  ✓ Mac App Store app list")
    else:
        log.warn("  ✗ No MAS app list")
    
    dotball = os.path.join(srcdir, "dotfiles.tar.gz")
    if os.path.exists(dotball):
        size = os.path.getsize(dotball)
        log.info(f"  ✓ Dotfiles archive ({size} bytes)")
    else:
        log.warn("  ✗ No dotfiles backup")
    
    defdir = os.path.join(srcdir, "defaults")
    if os.path.isdir(defdir):
        plist_files = [f for f in os.listdir(defdir) if f.endswith('.plist')]
        log.info(f"  ✓ System preferences: {len(plist_files)} domains")
    else:
        log.warn("  ✗ No system preferences")
    
    la = os.path.join(srcdir, "LaunchAgents")
    if os.path.isdir(la):
        agent_files = [f for f in os.listdir(la) if f.endswith('.plist')]
        log.info(f"  ✓ LaunchAgents: {len(agent_files)} services")
    else:
        log.warn("  ✗ No LaunchAgents")
    
    # Show environment info
    env_file = os.path.join(srcdir, "ENVIRONMENT.txt")
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            log.info("  ✓ Source environment info:")
            for line in content.split('\n')[:3]:  # Show first 3 lines
                if line.strip():
                    log.info(f"    {line}")
        except:
            log.info("  ✓ Environment info file")
    
    log.hr()
    log.ok("Preview completed. Use 'myconfig restore' to perform actual restore")
