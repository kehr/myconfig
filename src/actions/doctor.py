from __future__ import annotations
import logging, os
from ..utils import run_out
from ..logger import log_section, log_separator, log_success

def do_doctor(cfg):
    logger = logging.getLogger(__name__)
    log_section(logger, "System health check")
    log_separator(logger)
    # Xcode
    rc,_ = run_out("xcode-select -p")
    if rc==0:
        log_success(logger, "Xcode CLT installed")
    else:
        logger.warning("Xcode CLT not installed (xcode-select --install)")
    # brew
    if run_out("command -v brew >/dev/null 2>&1; echo $?")[0]==0:
        rc,v = run_out("brew --version | head -n1")
        log_success(logger, v.strip())
    else: 
        logger.warning("brew not installed")
    # code
    if run_out("command -v code >/dev/null 2>&1; echo $?")[0]==0:
        log_success(logger, "code command available")
    else:
        logger.warning("VS Code command 'code' not detected")
    # mas
    if run_out("command -v mas >/dev/null 2>&1; echo $?")[0]==0:
        rc,acc = run_out("mas account 2>/dev/null || echo 'Not logged in'")
        if "Not logged in" not in acc and acc.strip():
            log_success(logger, f"App Store logged in: {acc.strip()}")
        else:
            logger.warning("App Store not logged in")
    else: 
        logger.warning("mas not installed")
    # defaults domain list
    dom_file = "./config/defaults/domains.txt"
    if os.path.exists(dom_file):
        missing=0
        with open(dom_file,"r",encoding="utf-8") as f:
            for line in f:
                d=line.strip()
                if not d or d.startswith("#"): continue
                if run_out(f'defaults domains | grep -q "{d}"; echo $?')[0]!=0:
                    logger.warning(f"defaults domain not initialized: {d}")
                    missing+=1
        if missing==0: 
            log_success(logger, "defaults domain list check passed")
    log_separator(logger)
    log_success(logger, "Health check completed")
