<div align="center">

# Envertor 🔍

[![PyPI version](https://img.shields.io/pypi/v/envertor)](https://pypi.org/project/envertor/)
[![Python](https://img.shields.io/pypi/pyversions/envertor)](https://pypi.org/project/envertor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Y3454R/envertor/blob/main/LICENSE)

</div>

Envertor is a CLI tool that generates `.env.example` files by extracting environment variables from existing `.env` files or by scanning Python and JavaScript/TypeScript projects. It also helps keep your secrets safe with automatic `.gitignore` protection and CI/CD-ready parity checks.

## Install

```bash
pip install envertor
```

**Development install:**
```bash
pip install -e .
```

---

## Usage

### Generate `.env.example` from an existing `.env`

Strips real values and replaces them with type-appropriate placeholders:

```bash
envertor -i .env -o .env.example
```

| Original `.env` | Generated `.env.example` |
|---|---|
| `SECRET=mysecret` | `SECRET=''` |
| `PORT=8080` | `PORT=0` |
| `DEBUG=true` | `DEBUG=false` |
| `RATE=3.14` | `RATE=0.0` |

---

### Scan a project for environment variables

Detects env vars used in source code and generates `.env.example` from actual usage — no existing `.env` required:

```bash
envertor -p ./my-project -o .env.example
```

Limit scanning to a specific language:
```bash
envertor -p ./my-project --lang python
envertor -p ./my-project --lang js
```

Supports:
- **Python**: `os.getenv("VAR")`, `os.environ["VAR"]`, `os.environ.get("VAR")`
- **JS/TS**: `process.env.VAR` (`.js`, `.ts`, `.jsx`, `.tsx`)

---

### Create `.env` from `.env.example`

Bootstrap a local `.env` from the example file so teammates can fill in their own values:

```bash
envertor --create-env                        # reads .env.example by default
envertor --create-env staging.env.example    # reads a custom file
```

If `.env` already exists, writes `.env.envertor` instead to avoid overwriting.

---

### Check parity between `.env` and `.env.example`

Explicitly verify that both files have the same keys. Designed for CI/CD pipelines — exits `1` on mismatch:

```bash
envertor --check
envertor --check --env-file /deploy/.env --example-file /repo/.env.example
```

Example output on failure:
```
[envertor] FAIL: Keys mismatch between .env and .env.example
  Missing from .env:          NEW_KEY
  Missing from .env.example:  OLD_KEY
```

Use in a pipeline:
```yaml
# GitHub Actions example
- name: Check env parity
  run: envertor --check --env-file .env --example-file .env.example
```

---

### Show version

```bash
envertor -v
```

---

## Automatic safety checks

Every time envertor runs, it performs these checks automatically:

**`.gitignore` protection** — ensures `.env` is listed in `.gitignore`. Creates the file if it doesn't exist:
```
[envertor] Created .gitignore with .env
[envertor] Added .env to .gitignore
```

**Key parity warning** — warns if `.env` and `.env.example` have different keys:
```
[envertor] WARNING: Keys in .env not documented in .env.example: DB_URL
[envertor] WARNING: Keys in .env.example not found in .env: NEW_KEY
```

**Leftover values warning** — warns if `.env.example` contains non-placeholder values (real secrets accidentally left behind):
```
[envertor] WARNING: .env.example has a real value set for API_KEY
```

---

## Options

| Flag | Description |
|---|---|
| `-i, --input FILE` | Path to input `.env` file |
| `-o, --output FILE` | Path to output `.env.example` (default: `.env.example`) |
| `-p, --project DIR` | Project folder to scan for env variable usage |
| `--lang python\|js\|both` | Language filter for project scanning (default: `both`) |
| `--create-env [FILE]` | Create `.env` from `FILE` (default: `.env.example`) |
| `--check` | Check key parity and exit `1` on mismatch (CI/CD mode) |
| `--env-file FILE` | `.env` path for `--check` (default: `.env`) |
| `--example-file FILE` | `.env.example` path for `--check` (default: `.env.example`) |
| `-v, --version` | Show version |

---

## Notes

- Automatically skips `node_modules/`, `venv/`, `__pycache__/`, `.next/`, `.git/`, `.idea/`, `.vscode/`
- Regex-based scanning catches the most common patterns (`os.getenv`, `os.environ`, `process.env`)
- `.env.envertor` is a safe backup — rename it to `.env` or diff it against your existing one

---

## License

MIT © [Samin Yeasar](https://github.com/Y3454R)
