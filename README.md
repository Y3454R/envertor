# Envertor

Envertor is a CLI tool that generates a .env.example file by extracting environment variables from existing .env files or by scanning Python and JavaScript/TypeScript projects.

# Usage

### Install (development)
```bash
pip install -e .
```

### Generate .env.example from an existing .env
```bash
envertor -i .env -o .env.example
```

### Auto-scan a project for environment variables

Extract env variables used in Python and JavaScript/TypeScript code:

```bash
envertor -p ./my-project -o .env.example
```

Limit scanning to a specific language
```bash
envertor -p ./my-project --lang python
envertor -p ./my-project --lang js
```

Show version
```bash
envertor -v
```

# Notes

- Automatically skips `node_modules/`, `venv/`, `__pycache__/`, and `.next/`

- Works with Python (os.getenv, os.environ) and JS/TS (process.env)

- Output is a clean .env.example with placeholders
