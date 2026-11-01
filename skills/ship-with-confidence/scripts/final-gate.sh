#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 || $1 != "--delivery" || $3 != "--evidence" ]]; then
  printf 'Usage: %s --delivery DELIVERY_ID --evidence PATH\n' "$0" >&2
  printf 'Creates a tamper-evident attestation receipt; it does not authorize a push.\n' >&2
  exit 2
fi

delivery=$2
evidence=$4
[[ $delivery =~ ^[A-Za-z0-9._-]+$ ]] || {
  printf 'final-gate: invalid delivery id\n' >&2
  exit 2
}

git rev-parse --is-inside-work-tree >/dev/null
[[ -z $(git status --porcelain) ]] || {
  printf 'final-gate: BLOCKED; working tree is not clean\n' >&2
  exit 1
}

head=$(git rev-parse HEAD)
branch=$(git branch --show-current)
[[ -n $branch ]] || {
  printf 'final-gate: BLOCKED; detached HEAD\n' >&2
  exit 1
}

[[ -f $evidence ]] || {
  printf 'final-gate: BLOCKED; evidence manifest not found\n' >&2
  exit 1
}
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$script_dir/validate_evidence.py" "$evidence" --delivery "$delivery"
evidence=$(realpath "$evidence")
digest=$(sha256sum "$evidence" | cut -d ' ' -f 1)

git_dir=$(git rev-parse --git-dir)
receipt_dir="$git_dir/ship-with-confidence"
mkdir -p "$receipt_dir"
printf '%s\n%s\n%s\n%s\n' "$head" "$branch" "$evidence" "$digest" > "$receipt_dir/$delivery.attestation"
printf 'final-gate: attestation receipt created for %s at %s; not push authorization\n' "$delivery" "$head"
