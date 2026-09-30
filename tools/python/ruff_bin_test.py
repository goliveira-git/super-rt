from ruff_bin import ruff_executable_name


def test_windows_uses_the_exe_suffix_and_other_platforms_do_not():
    assert ruff_executable_name("win32") == "ruff.exe"
    assert ruff_executable_name("linux") == "ruff"
