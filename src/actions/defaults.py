from __future__ import annotations
import os
from ..utils import AppConfig, Logger, run, run_out

def _load_list(path:str)->list[str]:
    L=[]
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                s=line.strip()
                if not s or s.startswith("#"): continue
                L.append(s)
    return L

def defaults_export_all(cfg: AppConfig, log: Logger):
    log.sec("defaults full export"); log.hr()
    rc,out = run_out("defaults domains")
    if rc!=0: log.err("Cannot list defaults domains"); return
    excludes = _load_list("./"+cfg.defaults_exclude_file)
    outdir = f'./backups/defaults-all-{ts()}'
    os.makedirs(outdir, exist_ok=True)
    for d in out.split():
        if any(x in d for x in excludes): 
            log.info(f"Excluding: {d}"); continue
        run(f'defaults export "{d}" "{outdir}/{d}.plist" || true', log, check=False)
    log.ok(f"Exported to: {outdir}")

def defaults_import_dir(cfg: AppConfig, log: Logger, dirpath: str):
    if not dirpath or not os.path.isdir(dirpath):
        log.err(f"Directory does not exist: {dirpath}"); return
    log.sec(f"Import defaults: {dirpath}"); log.hr()
    run('for p in "'+dirpath+'"/*.plist; do [[ -e "$p" ]] || continue; '
        'd="$(basename "$p" .plist)"; '
        'defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${d}_$(date +%Y%m%d%H%M%S).plist" || true; '
        'defaults import "$d" "$p" || true; '
        'done; killall Dock 2>/dev/null || true; killall Finder 2>/dev/null || true', log, check=False)
    log.ok("defaults import completed")

from ..utils import ts
