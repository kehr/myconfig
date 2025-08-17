from __future__ import annotations
from ..utils import Logger, run_out

def do_doctor(cfg, log: Logger):
    log.sec("System health check"); log.hr()
    # Xcode
    rc,_ = run_out("xcode-select -p"); log.ok("Xcode CLT installed") if rc==0 else log.warn("Xcode CLT not installed (xcode-select --install)")
    # brew
    if run_out("command -v brew >/dev/null 2>&1; echo $?")[0]==0:
        rc,v = run_out("brew --version | head -n1"); log.ok(v.strip())
        run_out("brew update >/dev/null 2>&1")
    else: log.warn("brew not installed")
    # code
    log.ok("code command available") if run_out("command -v code >/dev/null 2>&1; echo $?")[0]==0 else log.warn("VS Code command 'code' not detected")
    # mas
    if run_out("command -v mas >/dev/null 2>&1; echo $?")[0]==0:
        rc,acc = run_out("mas account || true"); log.ok(f"App Store logged in: {acc.strip()}") if acc.strip() else log.warn("App Store not logged in")
    else: log.warn("mas not installed")
    # defaults domain list
    import os
    dom_file = "./config/defaults/domains.txt"
    if os.path.exists(dom_file):
        missing=0
        with open(dom_file,"r",encoding="utf-8") as f:
            for line in f:
                d=line.strip()
                if not d or d.startswith("#"): continue
                if run_out(f'defaults domains | grep -q "{d}"; echo $?')[0]!=0:
                    log.warn(f"defaults domain not initialized: {d}"); missing+=1
        if missing==0: log.ok("defaults domain list check passed")
    log.hr(); log.ok("Health check completed")
