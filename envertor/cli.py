import os
import shutil
import sys
import argparse

from .core import generate_example_env, complete_env
from .scanner import scan_project
from .gitignore import warn_if_env_unprotected, protect
from .checker import check_key_parity, check_example_values
from .version import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Envertor: Generate example .env files from existing .env or project"
    )

    parser.add_argument(
        "-i", "--input",
        default=None,
        help="Path to input .env file"
    )
    parser.add_argument(
        "-o", "--output",
        default=".env.example",
        help="Path to output example .env file"
    )
    parser.add_argument(
        "-p", "--project",
        default=None,
        help="Project folder to auto-scan for env variables"
    )
    parser.add_argument(
        "--lang",
        choices=["python", "js", "both"],
        default="both",
        help="Languages to scan in project (default: both)"
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show envertor version"
    )
    parser.add_argument(
        "--create-env",
        nargs="?",
        const=".env.example",
        default=None,
        metavar="FILE",
        help="Create .env from FILE (default: .env.example). Writes .env.envertor if .env already exists."
    )
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help="Use type-aware placeholders in output (e.g. 0, 0.0, false, '') instead of empty values"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that .env and .env.example have matching keys. Exits 1 on mismatch."
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file for --check (default: .env)"
    )
    parser.add_argument(
        "--example-file",
        default=".env.example",
        help="Path to .env.example file for --check (default: .env.example)"
    )
    parser.add_argument(
        "--protect",
        action="store_true",
        help="Interactively add .env to .gitignore at repo root."
    )
    parser.add_argument(
        "--complete",
        nargs="?",
        const=".env",
        default=None,
        metavar="TARGET",
        help="Fill empty values in TARGET .env (default: .env) from --from source."
    )
    parser.add_argument(
        "--from",
        dest="complete_from",
        default=None,
        metavar="SOURCE",
        help="Source .env file to read values from (used with --complete)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what --complete would fill without writing any changes."
    )

    args = parser.parse_args()

    if args.version:
        print(f"envertor v{__version__}")
        return

    if args.protect:
        env_path = os.path.abspath(args.env_file)
        protect(env_path)
        return

    if args.complete is not None:
        if not args.complete_from:
            print("[envertor] ERROR: --complete requires --from <source>")
            sys.exit(1)
        if not os.path.exists(args.complete):
            print(f"[envertor] ERROR: Target file '{args.complete}' not found.")
            sys.exit(1)
        if not os.path.exists(args.complete_from):
            print(f"[envertor] ERROR: Source file '{args.complete_from}' not found.")
            sys.exit(1)
        complete_env(args.complete, args.complete_from, dry_run=args.dry_run)
        return

    if args.check:
        ok = check_key_parity(args.env_file, args.example_file, strict=True)
        sys.exit(0 if ok else 1)

    if args.create_env is not None:
        source = args.create_env
        if not os.path.exists(source):
            print(f"[envertor] ERROR: Source file '{source}' not found.")
            sys.exit(1)
        dest = ".env" if not os.path.exists(".env") else ".env.envertor"
        shutil.copy(source, dest)
        print(f"[envertor] Created {dest} from {source}")
        warn_if_env_unprotected(os.path.abspath(dest))
        return

    if args.project:
        languages = ("python", "js") if args.lang == "both" else (args.lang,)
        env_vars = scan_project(args.project, languages)
        placeholder = "''" if args.placeholder else ""
        with open(args.output, "w") as f:
            for key in sorted(env_vars):
                f.write(f"{key}={placeholder}\n")
        print(f"Generated {args.output} from project scan.")
        env_path = os.path.join(args.project, ".env")
        warn_if_env_unprotected(os.path.abspath(env_path))
        if os.path.exists(env_path) and os.path.exists(args.output):
            check_key_parity(env_path, args.output)
        if os.path.exists(args.output):
            check_example_values(args.output)

    elif args.input:
        generate_example_env(args.input, args.output, use_placeholder=args.placeholder)
        print(f"Created {args.output} from {args.input}")
        warn_if_env_unprotected(os.path.abspath(args.input))
        if os.path.exists(args.input) and os.path.exists(args.output):
            check_key_parity(args.input, args.output)
        if os.path.exists(args.output):
            check_example_values(args.output)

    else:
        print("Provide either --input or --project")
