"""Checks commit messages against the repo commit format (CLAUDE.md, "Commit format").

Usage: check_commit_msg --file PATH   checks one message file (commit-msg hook)
       check_commit_msg --range A..B  checks every commit in a git revision range (CI)
Exits 1 and prints the reason when a message breaks the format.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

MAX_SUBJECT_LENGTH = 72
FIXUP_PREFIXES = ("fixup!", "squash!", "amend!")


class CommitMessageError(Exception):
    """A commit message breaks the commit format."""


def check_message(message: str, *, allow_fixup: bool = True) -> None:
    """Raises CommitMessageError when `message` breaks the format; returns None otherwise.

    Lines starting with `#` are git comments and are ignored. Fixup commits are accepted only
    when `allow_fixup` is true, because they must be folded before a branch merges.
    """
    lines = [line.rstrip() for line in message.splitlines() if not line.startswith("#")]
    while lines and not lines[0]:
        lines.pop(0)
    if not lines:
        raise CommitMessageError("empty commit message")
    subject = lines[0]
    if subject.startswith(FIXUP_PREFIXES):
        if allow_fixup:
            return
        raise CommitMessageError(f"fixup commit must be folded before merge: {subject!r}")
    if len(subject) > MAX_SUBJECT_LENGTH:
        raise CommitMessageError(f"subject is {len(subject)} characters, the limit is 72")
    if subject.endswith("."):
        raise CommitMessageError("subject must not end with a period")
    if len(lines) > 1 and lines[1]:
        raise CommitMessageError("second line must be blank")


def git_log_command(revision_range: str) -> list[str]:
    """Returns the git command listing the full messages in `revision_range`, merges excluded.

    Merge commits are skipped because CI checks out a generated merge commit on pull requests.
    """
    return ["git", "log", "--no-merges", "--format=%B%x1e", revision_range]


def messages_in_range(revision_range: str) -> list[str]:
    """Returns the full message of every commit in `revision_range` (for example origin/main..HEAD)."""
    output = subprocess.run(
        git_log_command(revision_range),
        capture_output=True,
        check=True,
        cwd=os.environ.get("BUILD_WORKSPACE_DIRECTORY"),
    ).stdout.decode("utf-8")
    return [message for message in output.split("\x1e") if message.strip()]


def main(argv: list[str]) -> int:
    """Runs the checker for the given command-line arguments; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file")
    group.add_argument("--range")
    args = parser.parse_args(argv)
    try:
        if args.file:
            base = os.environ.get("BUILD_WORKING_DIRECTORY", ".")
            text = Path(base, args.file).read_text(encoding="utf-8")
            check_message(text, allow_fixup=True)
        else:
            for message in messages_in_range(args.range):
                check_message(message, allow_fixup=False)
    except CommitMessageError as error:
        print(f"commit message rejected: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
