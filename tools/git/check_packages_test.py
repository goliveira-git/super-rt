from check_packages import find_unchecked_packages, split_ls_files_output


def test_directory_with_python_but_no_build_file_is_reported():
    paths = [
        "ame/python/src/ame/BUILD.bazel",
        "ame/python/src/ame/__init__.py",
        "ame/python/src/ame/hub/messages.py",
        "ame/python/spikes/s1_camera.py",
        "docs/example.py",
    ]
    assert find_unchecked_packages(paths) == ["ame/python/src/ame/hub"]


def test_non_ascii_directory_without_build_file_is_reported():
    paths = ["ame/python/src/ame/saudação/messages.py"]
    assert find_unchecked_packages(paths) == ["ame/python/src/ame/saudação"]


def test_file_merely_ending_in_build_bazel_does_not_count_as_a_build_file():
    paths = ["pkg/NOTBUILD.bazel", "pkg/module.py"]
    assert find_unchecked_packages(paths) == ["pkg"]


def test_nul_separated_git_output_keeps_non_ascii_paths_intact():
    raw = "a\0ame/python/src/ame/saudação/x.py\0".encode()
    assert split_ls_files_output(raw) == ["a", "ame/python/src/ame/saudação/x.py"]
