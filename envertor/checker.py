import os

SAFE_PLACEHOLDERS = {"", "''", '""', "0", "0.0", "false"}


def _parse_keys(filepath: str) -> set:
    keys = set()
    with open(filepath, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                keys.add(key)
    return keys


def _is_safe_placeholder(value: str) -> bool:
    value = value.strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    return value.lower() in SAFE_PLACEHOLDERS


def check_key_parity(env_path: str, example_path: str, strict: bool = False):
    env_keys = _parse_keys(env_path)
    example_keys = _parse_keys(example_path)

    missing_from_env = example_keys - env_keys
    missing_from_example = env_keys - example_keys

    if not missing_from_env and not missing_from_example:
        if strict:
            print(f"[envertor] OK: {env_path} and {example_path} keys match.")
            return True
        return None

    if strict:
        print(f"[envertor] FAIL: Keys mismatch between {env_path} and {example_path}")
        if missing_from_env:
            print(f"  Missing from {env_path}:      {', '.join(sorted(missing_from_env))}")
        if missing_from_example:
            print(f"  Missing from {example_path}: {', '.join(sorted(missing_from_example))}")
        return False

    if missing_from_env:
        print(f"[envertor] WARNING: Keys in {example_path} not found in {env_path}: {', '.join(sorted(missing_from_env))}")
    if missing_from_example:
        print(f"[envertor] WARNING: Keys in {env_path} not documented in {example_path}: {', '.join(sorted(missing_from_example))}")
    return None


def check_example_values(example_path: str) -> None:
    with open(example_path, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key, value = stripped.split("=", 1)
                key = key.strip()
                if not _is_safe_placeholder(value):
                    print(f"[envertor] WARNING: {example_path} has a real value set for {key}")
