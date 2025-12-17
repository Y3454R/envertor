# envertor/cli.py
import argparse
from .core import generate_example_env
from .scanner import scan_project
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

    args = parser.parse_args()

    if args.version:
        print(f"envertor v{__version__}")
        return

    # Project scanning mode
    if args.project:
        languages = ("python", "js") if args.lang == "both" else (args.lang,)
        env_vars = scan_project(args.project, languages)
        with open(args.output, "w") as f:
            for key in sorted(env_vars):
                f.write(f"{key}=\n")
        print(f"Generated {args.output} from project scan.")
    # Single .env file mode
    elif args.input:
        generate_example_env(args.input, args.output)
        print(f"Created {args.output} from {args.input}")
    else:
        print("Provide either --input or --project")

