#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' \
  'final-push: BLOCKED; automatic push is disabled because a local receipt cannot prove current user authorization or independent execution.' \
  'After reviewing live evidence and confirming explicit authorization in the current interaction, the active writer may run one ordinary git push directly.' >&2
exit 1
