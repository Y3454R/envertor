import os
import tempfile
import pytest

from envertor.core import detect_placeholder
from envertor.gitignore import ensure_env_in_gitignore
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


# --- ensure_env_in_gitignore ---

def test_gitignore_created_when_missing():
    with tempfile.TemporaryDirectory() as d:
        ensure_env_in_gitignore(d)
        gitignore = os.path.join(d, ".gitignore")
        assert os.path.exists(gitignore)
        assert ".env" in open(gitignore).read()


def test_gitignore_appended_when_env_missing():
    with tempfile.TemporaryDirectory() as d:
        gitignore = os.path.join(d, ".gitignore")
        with open(gitignore, "w") as f:
            f.write("node_modules/\n")
        ensure_env_in_gitignore(d)
        content = open(gitignore).read()
        assert ".env" in content
        assert "node_modules/" in content


def test_gitignore_no_duplicate_when_env_present():
    with tempfile.TemporaryDirectory() as d:
        gitignore = os.path.join(d, ".gitignore")
        with open(gitignore, "w") as f:
            f.write(".env\nnode_modules/\n")
        ensure_env_in_gitignore(d)
        content = open(gitignore).read()
        assert content.count(".env") == 1


# --- check_key_parity ---

def _write(path, content):
    with open(path, "w") as f:
        f.write(content)


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
