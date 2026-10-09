import subprocess

from check_packages import find_unchecked_packages, main, split_ls_files_output

CHECKED = "python_checks(name = 'quality', srcs = glob(['*.py']))\n"
NO_FILES: dict[str, str] = {}


def test_directory_with_python_but_no_build_file_is_reported():
    paths = [
        "ame/python/src/ame/BUILD.bazel",
        "ame/python/src/ame/__init__.py",
        "ame/python/src/ame/hub/messages.py",
        "ame/python/spikes/s1_camera.py",
        "docs/example.py",
    ]
    problems = find_unchecked_packages(paths, {"ame/python/src/ame/BUILD.bazel": CHECKED}.get)
    assert problems == ["ame/python/src/ame/hub: no BUILD.bazel"]


def test_build_file_without_python_checks_is_reported():
    paths = ["pkg/BUILD.bazel", "pkg/module.py", "ok/BUILD.bazel", "ok/module.py"]
    texts = {"pkg/BUILD.bazel": "py_library(name = 'pkg')\n", "ok/BUILD.bazel": CHECKED}
    assert find_unchecked_packages(paths, texts.get) == ["pkg: BUILD.bazel has no python_checks("]


def test_only_the_top_level_docs_tree_is_exempt_but_spikes_are_exempt_anywhere():
    paths = ["docs/a.py", "ame/docs/b.py", "spikes/c.py", "ame/python/spikes/d.py"]
    assert find_unchecked_packages(paths, NO_FILES.get) == ["ame/docs: no BUILD.bazel"]


def test_non_ascii_directory_without_build_file_is_reported():
    paths = ["ame/python/src/ame/saudação/messages.py"]
    problems = find_unchecked_packages(paths, NO_FILES.get)
    assert problems == ["ame/python/src/ame/saudação: no BUILD.bazel"]


def test_file_merely_ending_in_build_bazel_does_not_count_as_a_build_file():
    paths = ["pkg/NOTBUILD.bazel", "pkg/module.py"]
    assert find_unchecked_packages(paths, NO_FILES.get) == ["pkg: no BUILD.bazel"]


def test_nul_separated_git_output_keeps_non_ascii_paths_intact():
    raw = "a\0ame/python/src/ame/saudação/x.py\0".encode()
    assert split_ls_files_output(raw) == ["a", "ame/python/src/ame/saudação/x.py"]


def test_main_reports_a_git_failure_without_a_traceback(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(128, ["git", "ls-files", "-z"])

    monkeypatch.setattr(subprocess, "run", fail)
    assert main() == 1
    assert "git ls-files failed" in capsys.readouterr().err


def test_main_reports_undecodable_git_output_without_a_traceback(monkeypatch, capsys):
    result = subprocess.CompletedProcess(["git"], 0, stdout=b"\xff\0")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: result)
    assert main() == 1
    assert "not valid UTF-8" in capsys.readouterr().err
