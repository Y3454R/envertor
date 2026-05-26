import os
import shutil
import sys
import argparse

from .core import generate_example_env
from .scanner import scan_project
from .gitignore import ensure_env_in_gitignore
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

    args = parser.parse_args()

    if args.version:
        print(f"envertor v{__version__}")
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
        return

    if args.project:
        languages = ("python", "js") if args.lang == "both" else (args.lang,)
        env_vars = scan_project(args.project, languages)
        placeholder = "''" if args.placeholder else ""
        with open(args.output, "w") as f:
            for key in sorted(env_vars):
                f.write(f"{key}={placeholder}\n")
        print(f"Generated {args.output} from project scan.")
        ensure_env_in_gitignore(args.project)
        env_path = os.path.join(args.project, ".env")
        if os.path.exists(env_path) and os.path.exists(args.output):
            check_key_parity(env_path, args.output)
        if os.path.exists(args.output):
            check_example_values(args.output)

    elif args.input:
        generate_example_env(args.input, args.output, use_placeholder=args.placeholder)
        print(f"Created {args.output} from {args.input}")
        project_dir = os.path.dirname(os.path.abspath(args.input))
        ensure_env_in_gitignore(project_dir)
        if os.path.exists(args.input) and os.path.exists(args.output):
            check_key_parity(args.input, args.output)
        if os.path.exists(args.output):
            check_example_values(args.output)

    else:
        print("Provide either --input or --project")
