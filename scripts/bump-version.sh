#!/usr/bin/env bash
#
# bump-version.sh - bump version numbers across declared files, with drift
# detection and repo-wide audit for missed version references.
#
# Usage:
#   scripts/bump-version.sh <new-version>
#   scripts/bump-version.sh --check
#   scripts/bump-version.sh --audit

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$REPO_ROOT/.version-bump.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "error: .version-bump.json not found at $CONFIG" >&2
  exit 1
fi

python_json() {
  python3 - "$@"
}

read_json_field() {
  local file="$1" field="$2"
  python_json "$file" "$field" <<'PY'
import json
import sys

path, field = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as handle:
    value = json.load(handle)
for part in field.split("."):
    value = value[int(part)] if part.isdigit() else value[part]
print(value)
PY
}

write_json_field() {
  local file="$1" field="$2" value="$3"
  python_json "$file" "$field" "$value" <<'PY'
import json
import sys

path, field, replacement = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)

target = data
parts = field.split(".")
for part in parts[:-1]:
    target = target[int(part)] if part.isdigit() else target[part]
last = parts[-1]
if last.isdigit():
    target[int(last)] = replacement
else:
    target[last] = replacement

with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
PY
}

declared_files() {
  python_json "$CONFIG" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    config = json.load(handle)
for item in config["files"]:
    print(f'{item["path"]}\t{item["field"]}')
PY
}

audit_excludes() {
  python_json "$CONFIG" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    config = json.load(handle)
for item in config.get("audit", {}).get("exclude", []):
    print(item)
PY
}

cmd_check() {
  local has_drift=0
  local versions=()

  echo "Version check:"
  echo

  while IFS=$'\t' read -r path field; do
    local fullpath="$REPO_ROOT/$path"
    if [[ ! -f "$fullpath" ]]; then
      printf "  %-45s  MISSING\n" "$path ($field)"
      has_drift=1
      continue
    fi
    local version
    version="$(read_json_field "$fullpath" "$field")"
    printf "  %-45s  %s\n" "$path ($field)" "$version"
    versions+=("$version")
  done < <(declared_files)

  echo

  local unique
  unique="$(printf '%s\n' "${versions[@]}" | sort -u | wc -l | tr -d ' ')"
  if [[ "$unique" -gt 1 ]]; then
    echo "DRIFT DETECTED - versions are not in sync:"
    printf '%s\n' "${versions[@]}" | sort | uniq -c | sort -rn
    has_drift=1
  else
    echo "All declared files are in sync at ${versions[0]}"
  fi

  return "$has_drift"
}

cmd_audit() {
  cmd_check || true
  echo

  local current_version
  current_version="$(
    while IFS=$'\t' read -r path field; do
      local fullpath="$REPO_ROOT/$path"
      [[ -f "$fullpath" ]] && read_json_field "$fullpath" "$field"
    done < <(declared_files) | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
  )"

  if [[ -z "$current_version" ]]; then
    echo "error: could not determine current version" >&2
    return 1
  fi

  echo "Audit: scanning repo for version string '$current_version'..."
  echo

  local -a exclude_args=()
  while IFS= read -r pattern; do
    exclude_args+=("--exclude=$pattern" "--exclude-dir=$pattern")
  done < <(audit_excludes)
  exclude_args+=("--exclude-dir=.git" "--exclude-dir=node_modules" "--binary-files=without-match")

  local -a declared_paths=()
  while IFS=$'\t' read -r path _field; do
    declared_paths+=("$path")
  done < <(declared_files)

  local found_undeclared=0
  while IFS= read -r match; do
    local match_file rel_path is_declared=0
    match_file="$(echo "$match" | cut -d: -f1)"
    rel_path="${match_file#$REPO_ROOT/}"

    for declared_path in "${declared_paths[@]}"; do
      if [[ "$rel_path" == "$declared_path" ]]; then
        is_declared=1
        break
      fi
    done

    if [[ "$is_declared" -eq 0 ]]; then
      if [[ "$found_undeclared" -eq 0 ]]; then
        echo "UNDECLARED files containing '$current_version':"
        found_undeclared=1
      fi
      echo "  $match"
    fi
  done < <(grep -rn "${exclude_args[@]}" -F "$current_version" "$REPO_ROOT" 2>/dev/null || true)

  if [[ "$found_undeclared" -eq 0 ]]; then
    echo "No undeclared files contain the version string. All clear."
  else
    echo
    echo "Review the above files. If they should be bumped, add them to .version-bump.json."
    return 1
  fi
}

cmd_bump() {
  local new_version="$1"

  if ! echo "$new_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+'; then
    echo "error: '$new_version' does not look like a version (expected X.Y.Z)" >&2
    exit 1
  fi

  echo "Bumping all declared files to $new_version..."
  echo

  while IFS=$'\t' read -r path field; do
    local fullpath="$REPO_ROOT/$path"
    if [[ ! -f "$fullpath" ]]; then
      echo "  SKIP (missing): $path"
      continue
    fi
    local old_version
    old_version="$(read_json_field "$fullpath" "$field")"
    write_json_field "$fullpath" "$field" "$new_version"
    printf "  %-45s  %s -> %s\n" "$path ($field)" "$old_version" "$new_version"
  done < <(declared_files)

  echo
  echo "Done. Running audit to check for missed files..."
  echo
  cmd_audit
}

case "${1:-}" in
  --check)
    cmd_check
    ;;
  --audit)
    cmd_audit
    ;;
  --help|-h|"")
    echo "Usage: scripts/bump-version.sh <new-version> | --check | --audit"
    ;;
  --*)
    echo "error: unknown flag '$1'" >&2
    exit 1
    ;;
  *)
    cmd_bump "$1"
    ;;
esac
