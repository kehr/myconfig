from __future__ import annotations
import os, shutil
from ..utils import Logger

def profile_list(log: Logger):
    log.sec("Available profiles"); log.hr()
    for p in sorted(os.listdir("./config/profiles")):
        if p.endswith(".toml"): log.info(p)

def profile_use(log: Logger, name: str):
    src = f"./config/profiles/{name}.toml"
    if not os.path.exists(src): log.err(f"Not found: {src}"); return
    shutil.copyfile(src, "./config/config.toml"); log.ok(f"Applied: {src} → ./config/config.toml")

def profile_save(log: Logger, name: str):
    dst = f"./config/profiles/{name}.toml"
    shutil.copyfile("./config/config.toml", dst); log.ok(f"Saved current config as: {dst}")
