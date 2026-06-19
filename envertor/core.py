# envertor/core.py

def detect_placeholder(value):
    value = value.strip()

    if value.lower() in ["true", "false"]:
        return "false"

    try:
        int(value)
        return "0"
    except ValueError:
        pass

    try:
        float(value)
        return "0.0"
    except ValueError:
        pass

    return "''"


def generate_example_env(input_file, output_file, use_placeholder=False):
    with open(input_file, "r") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#") or not stripped:
            new_lines.append(line)
            continue

        if "=" in line:
            key, value_part = line.split("=", 1)
            key = key.strip()

            if "#" in value_part:
                value, inline_comment = value_part.split("#", 1)
                value = value.strip()
                inline_comment = "# " + inline_comment.strip()
            else:
                value = value_part.strip()
                inline_comment = ""

            replacement = detect_placeholder(value) if use_placeholder else ""

            if inline_comment:
                new_line = f"{key}={replacement} {inline_comment}\n"
            else:
                new_line = f"{key}={replacement}\n"

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(output_file, "w") as f:
        f.writelines(new_lines)


def complete_env(target_path: str, source_path: str, dry_run: bool = False) -> None:
    with open(source_path, "r") as f:
        source = {}
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            source[key.strip()] = value.strip()

    with open(target_path, "r") as f:
        lines = f.readlines()

    filled = []
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value == "" and key in source and source[key] != "":
            new_lines.append(f"{key}={source[key]}\n")
            filled.append(key)
        else:
            new_lines.append(line)

    if dry_run:
        if filled:
            print(f"[envertor] dry-run: would fill {len(filled)} key(s): {', '.join(filled)}")
        else:
            print("[envertor] dry-run: no empty keys to fill.")
        return

    with open(target_path, "w") as f:
        f.writelines(new_lines)

    if filled:
        print(f"[envertor] Filled {len(filled)} key(s): {', '.join(filled)}")
    else:
        print("[envertor] No empty keys to fill.")

