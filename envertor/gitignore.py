import os


def find_repo_root(start_path: str):
    path = os.path.abspath(start_path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    while True:
        if os.path.exists(os.path.join(path, ".git")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def _env_in_gitignore(gitignore_path: str) -> bool:
    with open(gitignore_path, "r") as f:
        for line in f:
            if line.strip() in (".env", "*.env"):
                return True
    return False


def warn_if_env_unprotected(env_path: str) -> None:
    repo_root = find_repo_root(env_path)
    if repo_root is None:
        return
    gitignore_path = os.path.join(repo_root, ".gitignore")
    if not os.path.exists(gitignore_path) or not _env_in_gitignore(gitignore_path):
        print("[envertor] WARNING: .env is not listed in .gitignore. Run --protect to fix.")


def protect(env_path: str) -> None:
    repo_root = find_repo_root(env_path)
    if repo_root is None:
        print("[envertor] WARNING: No git repository found. --protect has no effect.")
        return

    gitignore_path = os.path.join(repo_root, ".gitignore")

    if os.path.exists(gitignore_path) and _env_in_gitignore(gitignore_path):
        print("[envertor] .env is already protected in .gitignore")
        return

    answer = input("[envertor] .env is not listed in .gitignore. Add it now? [y/N]: ").strip().lower()
    if answer != "y":
        print("[envertor] Skipped.")
        return

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(".env\n")
        print(f"[envertor] Created .gitignore at {gitignore_path}")
    else:
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        with open(gitignore_path, "a") as f:
            if lines and not lines[-1].endswith("\n"):
                f.write("\n")
            f.write(".env\n")
        print(f"[envertor] Added .env to .gitignore at {gitignore_path}")

    print("[envertor] If .env was previously committed, remove it from git cache:")
    print("           git rm --cached .env")
