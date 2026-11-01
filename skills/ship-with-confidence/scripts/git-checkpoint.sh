#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s "commit message" -- path [path ...]\n' "$0" >&2
  exit 2
}

[[ $# -ge 3 ]] || usage
message=$1
shift
[[ $1 == "--" ]] || usage
shift
[[ $# -ge 1 ]] || usage

git rev-parse --is-inside-work-tree >/dev/null

for path in "$@"; do
  [[ -n $path && $path != "." && $path != ".." && $path != "/" && $path != :* && $path != /* && $path != -* ]] || {
    printf 'checkpoint: refusing broad path: %s\n' "$path" >&2
    exit 2
  }
  [[ $path != *"*"* && $path != *"?"* && $path != *"["* && $path != *".."* ]] || {
    printf 'checkpoint: refusing glob-like path: %s\n' "$path" >&2
    exit 2
  }
done

git --literal-pathspecs add -- "$@"

if git diff --cached --quiet; then
  printf 'checkpoint: nothing staged\n' >&2
  exit 1
fi

printf 'checkpoint: staged files\n'
git diff --cached --name-status

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$script_dir/secret_guard.py"

git diff --cached --check
git commit -m "$message" -- "$@"
