import argparse, importlib, pkgutil, os
from .utils import load_config, Logger
from .actions.export import do_export
from .actions.restore import do_restore
from .actions.doctor import do_doctor
from .actions.defaults import defaults_export_all, defaults_import_dir
from .actions.diffpack import do_diff, do_pack
from .actions.profile import profile_list, profile_use, profile_save

from ._version import VERSION

def build_parser():
    p = argparse.ArgumentParser(prog="myconfig", description="macOS configuration export/restore tool - readable and extensible")
    p.add_argument("-y","--yes", action="store_true")
    p.add_argument("-n","--dry-run", action="store_true")
    p.add_argument("-v","--verbose", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--no-mas", action="store_true")
    p.add_argument("--preview", action="store_true", help="Preview mode, show what will be processed")
    p.add_argument("--version", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("export", help="Export to backup directory")
    sp.add_argument("outdir", nargs="?")

    sp = sub.add_parser("restore", help="Restore from backup directory")
    sp.add_argument("srcdir")

    sub.add_parser("doctor", help="Health check and diagnosis")

    sp = sub.add_parser("defaults", help="System defaults extended operations")
    s2 = sp.add_subparsers(dest="sub")
    s2.add_parser("export-all", help="Export all defaults domains (with exclusion list)")
    spi = s2.add_parser("import", help="Import defaults from directory (batch plist)")
    spi.add_argument("dir")

    sp = sub.add_parser("diff", help="Compare differences between two backup directories")
    sp.add_argument("a"); sp.add_argument("b")

    sp = sub.add_parser("pack", help="Pack and encrypt backup (zip/gpg optional)")
    sp.add_argument("srcdir"); sp.add_argument("outfile", nargs="?")
    sp.add_argument("--gpg", action="store_true", help="Use gpg symmetric encryption")

    sp = sub.add_parser("profile", help="Configuration profiles (profiles/*.toml)")
    s3 = sp.add_subparsers(dest="sub")
    s3.add_parser("list", help="List available profiles")
    spu = s3.add_parser("use", help="Apply profile to config.toml")
    spu.add_argument("name")
    s3s = s3.add_parser("save", help="Save current config.toml as new profile")
    s3s.add_argument("name")

    # Auto-register plugins (requires register(subparsers) in src/plugins/*.py)
    plug_dir = os.path.join(os.path.dirname(__file__), "plugins")
    for m in pkgutil.iter_modules([plug_dir]):
        mod = importlib.import_module(f"src.plugins.{m.name}")
        if hasattr(mod, "register"):
            mod.register(sub)

    return p

def main():
    p = build_parser()
    args = p.parse_args()
    if args.version:
        print(f"myconfig {VERSION}"); return
    cfg = load_config("./config/config.toml")
    cfg = cfg._replace(
        interactive = (not args.yes) if args.yes else cfg.interactive,
        dry_run = True if args.dry_run else cfg.dry_run,
        verbose = True if args.verbose else cfg.verbose,
        quiet   = True if args.quiet else cfg.quiet,
        enable_mas = False if args.no_mas else cfg.enable_mas,
    )
    
    # Preview mode handling
    preview_mode = getattr(args, 'preview', False)
    log = Logger(cfg)

    if args.cmd == "export":
        if preview_mode:
            from .actions.export import preview_export
            preview_export(cfg, log, args.outdir)
        else:
            do_export(cfg, log, args.outdir)
    elif args.cmd == "restore":
        if preview_mode:
            from .actions.restore import preview_restore
            preview_restore(cfg, log, args.srcdir)
        else:
            do_restore(cfg, log, args.srcdir)
    elif args.cmd == "doctor":
        do_doctor(cfg, log)
    elif args.cmd == "defaults":
        if args.sub == "export-all": defaults_export_all(cfg, log)
        elif args.sub == "import":   defaults_import_dir(cfg, log, args.dir)
        else: p.print_help()
    elif args.cmd == "diff":
        do_diff(cfg, log, args.a, args.b)
    elif args.cmd == "pack":
        do_pack(cfg, log, args.srcdir, args.outfile, use_gpg=args.gpg)
    elif args.cmd == "profile":
        if args.sub == "list": profile_list(log)
        elif args.sub == "use": profile_use(log, args.name)
        elif args.sub == "save": profile_save(log, args.name)
        else: p.print_help()
    else:
        p.print_help()
