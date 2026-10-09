import subprocess
from collections.abc import Callable

import pytest
from check_commit_msg import (
    CommitMessageError,
    check_message,
    git_log_command,
    main,
    messages_in_range,
)


def test_well_formed_message_passes():
    check_message("Add hub envelope\n\nValidating in one place keeps the hub alive.\n")


def test_portuguese_subject_and_body_pass():
    check_message("Corrigir saudação em português\n\nO usuário disse: você está ótimo.\n")


def test_subject_over_72_characters_is_rejected():
    with pytest.raises(CommitMessageError, match="72"):
        check_message("x" * 73)


def test_trailing_period_and_missing_blank_line_are_rejected():
    with pytest.raises(CommitMessageError, match="period"):
        check_message("Add thing.\n")
    with pytest.raises(CommitMessageError, match="blank"):
        check_message("Add thing\nbody starts right away\n")


def test_fixup_allowed_locally_but_rejected_for_merge():
    check_message("fixup! Add hub envelope\n", allow_fixup=True)
    with pytest.raises(CommitMessageError, match="fixup"):
        check_message("fixup! Add hub envelope\n", allow_fixup=False)


def test_range_log_skips_merge_commits_and_ends_with_the_range():
    command = git_log_command("origin/main..HEAD")
    assert "--no-merges" in command
    assert command[-1] == "origin/main..HEAD"


def test_comment_lines_are_dropped_only_when_asked():
    with pytest.raises(CommitMessageError, match="empty"):
        check_message("# Please enter the message\n")
    with pytest.raises(CommitMessageError, match="72"):
        check_message("#" + "x" * 72, strip_comments=False)
    check_message("#123 Fix the hub\n", strip_comments=False)


def _fake_git_log(stdout: bytes) -> Callable[..., subprocess.CompletedProcess[bytes]]:
    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(command, 0, stdout=stdout)

    return run


def test_messages_in_range_splits_on_the_record_separator(monkeypatch):
    stdout = b"First one\n\nbody\n\x1e\nSecond one\n\x1e"
    monkeypatch.setattr(subprocess, "run", _fake_git_log(stdout))
    assert messages_in_range("a..b") == ["First one\n\nbody\n", "\nSecond one\n"]


def test_bad_range_or_non_utf8_output_becomes_a_commit_message_error(monkeypatch):
    def failing_run(*args, **kwargs):
        raise subprocess.CalledProcessError(128, args[0])

    monkeypatch.setattr(subprocess, "run", failing_run)
    with pytest.raises(CommitMessageError, match=r"a..b"):
        messages_in_range("a..b")
    monkeypatch.setattr(subprocess, "run", _fake_git_log(b"\xff\xfe"))
    with pytest.raises(CommitMessageError, match="UTF-8"):
        messages_in_range("a..b")


def test_main_file_mode_exit_codes_and_bom(tmp_path):
    good = tmp_path / "good.txt"
    good.write_text("Saudar você\n\nO usuário disse olá.\n", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("Saudar você.\n", encoding="utf-8")
    bom = tmp_path / "bom.txt"
    bom.write_bytes(b"\xef\xbb\xbf" + b"x" * 72)
    assert main(["--file", str(good)]) == 0
    assert main(["--file", str(bad)]) == 1
    assert main(["--file", str(bom)]) == 0


def test_main_range_mode_reports_a_bad_range_and_checks_hash_subjects(monkeypatch):
    def failing_run(*args, **kwargs):
        raise subprocess.CalledProcessError(128, args[0])

    monkeypatch.setattr(subprocess, "run", failing_run)
    assert main(["--range", "nope..HEAD"]) == 1
    monkeypatch.setattr(subprocess, "run", _fake_git_log(b"#123 Fix x.\x1e"))
    assert main(["--range", "a..b"]) == 1
