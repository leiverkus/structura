"""Command-line entry point: ``structura ...`` (see [project.scripts])."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import Settings
from .intake import discover_inputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="structura", description=__doc__)
    parser.add_argument("--version", action="version", version=f"structura {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("intake", help="Discover and list WebODM raster products")
    p_run = sub.add_parser("run", help="Run the vectorisation pipeline")
    p_run.add_argument("--dry-run", action="store_true", help="Do not write to the sink")

    args = parser.parse_args(argv)
    settings = Settings.from_env()

    if args.command == "intake":
        products = discover_inputs(settings.input_dir)
        if not products:
            print(f"No raster products found under {settings.input_dir}")
            return 0
        for prod in products:
            print(f"{prod.kind.value:6}  {prod.path}")
        return 0

    if args.command == "run":
        from .pipeline import run as run_pipeline  # lazy: avoids heavy imports for --help

        features = run_pipeline(settings, write=not args.dry_run)
        print(f"Produced {len(features)} feature(s); sink={settings.sink}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
