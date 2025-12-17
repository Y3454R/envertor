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


def generate_example_env(input_file, output_file):
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

            placeholder = detect_placeholder(value)

            if inline_comment:
                new_line = f"{key}={placeholder} {inline_comment}\n"
            else:
                new_line = f"{key}={placeholder}\n"

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(output_file, "w") as f:
        f.writelines(new_lines)

