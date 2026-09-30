import pytest
from check_commit_msg import CommitMessageError, check_message, git_log_command


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
