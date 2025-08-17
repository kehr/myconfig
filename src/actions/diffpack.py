from __future__ import annotations
import os
from ..utils import AppConfig, Logger, run

def do_diff(cfg: AppConfig, log: Logger, a: str, b: str):
    if not (os.path.isdir(a) and os.path.isdir(b)):
        log.err("Please provide two valid directories"); return
    log.sec(f"Compare: {a} ⇄ {b}"); log.hr()
    # 偏向可读的递归对比（忽略压缩二进制）
    run(f'diff -ruN --exclude="*.tar.gz" --exclude="*.zip" --exclude="*.log" {a} {b} || true', log, check=False)

def do_pack(cfg: AppConfig, log: Logger, srcdir: str, outfile: str|None, use_gpg: bool=False):
    if not os.path.isdir(srcdir):
        log.err(f"Directory does not exist: {srcdir}"); return
    base = outfile or (srcdir.rstrip("/").split("/")[-1] + ".zip")
    log.sec(f"Pack: {srcdir} → {base}"); log.hr()
    run(f'cd "{srcdir}/.." && zip -r "{base}" "{srcdir.split("/")[-1]}"', log, check=False)
    if use_gpg:
        if not which("gpg"):
            log.warn("gpg not detected, skipping encryption"); return
        run(f'gpg -c "{base}"', log, check=False)
        log.ok(f"Generated encrypted package: {base}.gpg")

def which(cmd: str)->bool:
    return os.system(f"command -v {cmd} >/dev/null 2>&1")==0
