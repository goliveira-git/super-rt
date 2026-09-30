BAZELISK=$(command -v bazelisk || true)
if [ -z "$BAZELISK" ] && [ -x "${LOCALAPPDATA:-}/Microsoft/WinGet/Links/bazelisk.exe" ]; then
    BAZELISK="${LOCALAPPDATA:-}/Microsoft/WinGet/Links/bazelisk.exe"
fi
if [ -z "$BAZELISK" ]; then
    echo "hook failed: bazelisk not found on PATH. Install it with: winget install --id Bazel.Bazelisk -e" >&2
    exit 1
fi
