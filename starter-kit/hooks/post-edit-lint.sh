#!/usr/bin/env bash
# post-edit-lint.sh
#
# PostToolUse hook for Write and Edit. Runs a linter matched to the file
# extension and prints its findings. This is advisory by design: it always
# exits 0, even when the linter finds problems. A hook that blocks the edit
# on every lint warning turns a two-line fix into an argument with a style
# rule, and an agent mid-task will route around a hard blocker rather than
# fix the underlying issue. Print the findings and let the agent decide.
#
# Every linter is gated on its own binary being installed, so on a machine
# without ruff, sqlfluff, or shellcheck this script is a silent no-op for
# that file type. Nothing here is required for the hook to run.
#
# settings.json wiring (merge into the "hooks" object):
#
#   "PostToolUse": [
#     {
#       "matcher": "Write|Edit",
#       "hooks": [
#         {"type": "command", "command": "bash ~/.claude/hooks/post-edit-lint.sh", "timeout": 30}
#       ]
#     }
#   ]
#
# LINT_SQL_DIALECT (env var) picks the sqlfluff dialect. Defaults to ansi.

set -uo pipefail

file_path="$(python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti, tr = data.get("tool_input", {}), data.get("tool_response", {})
print(ti.get("file_path") or ti.get("notebook_path") or tr.get("filePath") or "")
')"

[ -z "$file_path" ] && exit 0
[ -f "$file_path" ] || exit 0

case "$file_path" in
  */dbt_packages/*|*/node_modules/*|*/.venv/*|*/site-packages/*|*/__pycache__/*)
    exit 0
    ;;
esac

basename="$(basename "$file_path")"

run() {
  local label="$1"; shift
  local output
  output="$("$@" 2>&1)"
  if [ -n "$output" ]; then
    echo "$label findings for $basename:"
    echo "$output"
  fi
}

case "$file_path" in
  *.py)
    command -v ruff >/dev/null 2>&1 && run "ruff" ruff check --quiet "$file_path"
    ;;
  *.sql)
    if command -v sqlfluff >/dev/null 2>&1; then
      dialect="${LINT_SQL_DIALECT:-ansi}"
      run "sqlfluff" sqlfluff lint "$file_path" --dialect "$dialect" --templater raw
    fi
    ;;
  *.sh)
    command -v shellcheck >/dev/null 2>&1 && run "shellcheck" shellcheck "$file_path"
    ;;
esac

exit 0
