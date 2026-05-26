import os


def ensure_env_in_gitignore(project_path: str) -> None:
    gitignore_path = os.path.join(project_path, ".gitignore")

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(".env\n")
        print("[envertor] Created .gitignore with .env")
        return

    with open(gitignore_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        if stripped in (".env", "*.env"):
            return

    with open(gitignore_path, "a") as f:
        if lines and not lines[-1].endswith("\n"):
            f.write("\n")
        f.write(".env\n")
    print("[envertor] Added .env to .gitignore")
