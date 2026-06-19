import os
import tempfile
import pytest

from envertor.core import detect_placeholder, complete_env
from envertor.gitignore import find_repo_root, warn_if_env_unprotected
from envertor.checker import check_key_parity, check_example_values


def test_placeholder_detection():
    assert detect_placeholder("123") == "0"
    assert detect_placeholder("3.14") == "0.0"
    assert detect_placeholder("true") == "false"
    assert detect_placeholder("hello") == "''"


def test_generate_example_env_empty_by_default():
    from envertor.core import generate_example_env
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        out = os.path.join(d, ".env.example")
        with open(env, "w") as f:
            f.write("SECRET=mysecret\nPORT=8080\nDEBUG=true\n")
        generate_example_env(env, out)
        content = open(out).read()
        assert "SECRET=\n" in content
        assert "PORT=\n" in content
        assert "DEBUG=\n" in content


def test_generate_example_env_with_placeholder():
    from envertor.core import generate_example_env
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        out = os.path.join(d, ".env.example")
        with open(env, "w") as f:
            f.write("SECRET=mysecret\nPORT=8080\nDEBUG=true\n")
        generate_example_env(env, out, use_placeholder=True)
        content = open(out).read()
        assert "SECRET=''\n" in content
        assert "PORT=0\n" in content
        assert "DEBUG=false\n" in content


# --- find_repo_root ---

def test_find_repo_root_finds_git():
    with tempfile.TemporaryDirectory() as d:
        git_dir = os.path.join(d, ".git")
        os.makedirs(git_dir)
        subdir = os.path.join(d, "backend", "src")
        os.makedirs(subdir)
        env = os.path.join(subdir, ".env")
        open(env, "w").close()
        assert find_repo_root(env) == d


def test_find_repo_root_returns_none_when_no_git():
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        open(env, "w").close()
        assert find_repo_root(env) is None


# --- warn_if_env_unprotected ---

def test_warn_prints_when_not_in_gitignore(capsys):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, ".git"))
        gitignore = os.path.join(d, ".gitignore")
        with open(gitignore, "w") as f:
            f.write("node_modules/\n")
        env = os.path.join(d, ".env")
        open(env, "w").close()
        warn_if_env_unprotected(env)
        assert "WARNING" in capsys.readouterr().out


def test_warn_silent_when_already_protected(capsys):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, ".git"))
        gitignore = os.path.join(d, ".gitignore")
        with open(gitignore, "w") as f:
            f.write(".env\n")
        env = os.path.join(d, ".env")
        open(env, "w").close()
        warn_if_env_unprotected(env)
        assert capsys.readouterr().out == ""


def test_warn_silent_when_no_git(capsys):
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        open(env, "w").close()
        warn_if_env_unprotected(env)
        assert capsys.readouterr().out == ""


# --- complete_env ---

def _write(path, content):
    with open(path, "w") as f:
        f.write(content)


def test_complete_fills_empty_keys():
    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, ".env")
        source = os.path.join(d, ".env.old")
        _write(target, "SECRET=\nPORT=\n")
        _write(source, "SECRET=abc123\nPORT=8080\n")
        complete_env(target, source)
        content = open(target).read()
        assert "SECRET=abc123" in content
        assert "PORT=8080" in content


def test_complete_skips_non_empty_keys():
    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, ".env")
        source = os.path.join(d, ".env.old")
        _write(target, "SECRET=already_set\nPORT=\n")
        _write(source, "SECRET=other\nPORT=9000\n")
        complete_env(target, source)
        content = open(target).read()
        assert "SECRET=already_set" in content
        assert "PORT=9000" in content


def test_complete_ignores_extra_source_keys():
    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, ".env")
        source = os.path.join(d, ".env.old")
        _write(target, "SECRET=\n")
        _write(source, "SECRET=abc\nEXTRA=should_not_appear\n")
        complete_env(target, source)
        content = open(target).read()
        assert "EXTRA" not in content


def test_complete_dry_run_does_not_write(capsys):
    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, ".env")
        source = os.path.join(d, ".env.old")
        _write(target, "SECRET=\n")
        _write(source, "SECRET=abc123\n")
        complete_env(target, source, dry_run=True)
        content = open(target).read()
        assert "SECRET=\n" in content
        assert "dry-run" in capsys.readouterr().out


# --- check_key_parity ---

def test_parity_match(capsys):
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        example = os.path.join(d, ".env.example")
        _write(env, "KEY_A=secret\nKEY_B=123\n")
        _write(example, "KEY_A=''\nKEY_B=0\n")
        result = check_key_parity(env, example, strict=True)
        assert result is True


def test_parity_mismatch_strict(capsys):
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        example = os.path.join(d, ".env.example")
        _write(env, "KEY_A=secret\nKEY_C=extra\n")
        _write(example, "KEY_A=''\nKEY_B=''\n")
        result = check_key_parity(env, example, strict=True)
        assert result is False
        out = capsys.readouterr().out
        assert "KEY_B" in out
        assert "KEY_C" in out


def test_parity_mismatch_warns(capsys):
    with tempfile.TemporaryDirectory() as d:
        env = os.path.join(d, ".env")
        example = os.path.join(d, ".env.example")
        _write(env, "KEY_A=secret\n")
        _write(example, "KEY_A=''\nUNDOCUMENTED=''\n")
        check_key_parity(env, example, strict=False)
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "UNDOCUMENTED" in out


# --- check_example_values ---

def test_example_values_safe(capsys):
    with tempfile.TemporaryDirectory() as d:
        example = os.path.join(d, ".env.example")
        _write(example, "KEY_A=''\nKEY_B=0\nKEY_C=false\nKEY_D=\n")
        check_example_values(example)
        out = capsys.readouterr().out
        assert "WARNING" not in out


def test_example_values_warns_on_real_value(capsys):
    with tempfile.TemporaryDirectory() as d:
        example = os.path.join(d, ".env.example")
        _write(example, "KEY_A=real_secret\nKEY_B=''\n")
        check_example_values(example)
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "KEY_A" in out
        assert "KEY_B" not in out
