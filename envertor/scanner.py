# envertor/scanner.py
import os
import re

# Directories that should NEVER be scanned
SKIP_DIRS = {
    "node_modules",
    "venv",
    "__pycache__",
    ".next",
    ".git",
    ".idea",
    ".vscode"
}

# Regex patterns
PY_GETENV_PATTERN = re.compile(r'os\.getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)')
PY_ENVIRON_PATTERN = re.compile(
    r'os\.environ(?:\.get|\[)\s*[\'"]([A-Z0-9_]+)[\'"]\s*[\]\)]'
)
JS_ENV_PATTERN = re.compile(r'process\.env\.([A-Z0-9_]+)')

def scan_python_file(path: str) -> set[str]:
    """Extract env vars from a Python file."""
    env_vars = set()
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        env_vars.update(PY_GETENV_PATTERN.findall(code))
        env_vars.update(PY_ENVIRON_PATTERN.findall(code))
    except Exception:
        pass

    return env_vars

def scan_js_file(path: str) -> set[str]:
    """Extract env vars from a JS/TS file."""
    env_vars = set()
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        env_vars.update(JS_ENV_PATTERN.findall(code))
    except Exception:
        pass

    return env_vars

def scan_project(project_path: str, languages=("python", "js")) -> set[str]:
    """
    Scan a project directory for environment variable usage.

    :param project_path: Root directory of project
    :param languages: ("python", "js") or ("python",) or ("js",)
    :return: Set of environment variable names
    """
    env_vars = set()

    for root, dirs, files in os.walk(project_path):
        # 🚫 Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            full_path = os.path.join(root, file)

            if "python" in languages and file.endswith(".py"):
                env_vars.update(scan_python_file(full_path))

            if "js" in languages and file.endswith((".js", ".ts", ".jsx", ".tsx")):
                env_vars.update(scan_js_file(full_path))

    return env_vars

