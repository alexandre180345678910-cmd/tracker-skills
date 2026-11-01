#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

python3 "$skill_dir/scripts/validate_skill.py" "$skill_dir"

for required in workflow specify-design ui-ux tasks-execute debug-review security api-cost llm-efficiency contracts resilience supply-chain verify-operate evaluation specialist-routing memory sources; do
  test -s "$skill_dir/references/$required.md" || {
    printf 'missing reference: %s\n' "$required" >&2
    exit 1
  }
done

grep -q 'Never push checkpoints' "$skill_dir/SKILL.md"
grep -q 'Mandatory security gate' "$skill_dir/references/security.md"
grep -q 'cost per successful business outcome' "$skill_dir/references/api-cost.md"
grep -q 'Existing design system' "$skill_dir/references/ui-ux.md"
grep -q 'literal-pathspecs' "$skill_dir/scripts/git-checkpoint.sh"
grep -q 'automatic push is disabled' "$skill_dir/scripts/final-push.sh"
grep -q 'not push authorization' "$skill_dir/scripts/final-gate.sh"
python3 -m json.tool "$skill_dir/evals/evals.json" >/dev/null
python3 -m json.tool "$skill_dir/evals/implementation-scenarios.json" >/dev/null
python3 -m json.tool "$skill_dir/evals/specialist-routing-spec.json" >/dev/null
python3 -m json.tool "$skill_dir/evals/specialist-routing-baseline.json" >/dev/null
python3 -m json.tool "$skill_dir/evals/specialist-routing-treatment.json" >/dev/null
python3 "$skill_dir/scripts/evaluate_skill.py" \
  --spec "$skill_dir/evals/specialist-routing-spec.json" \
  --baseline "$skill_dir/evals/specialist-routing-baseline.json" \
  --with-skill "$skill_dir/evals/specialist-routing-treatment.json" \
  --min-pass-rate 1.0 --min-trigger-accuracy 1.0 >/dev/null
python3 -c 'import ast, pathlib, sys; [ast.parse(pathlib.Path(path).read_text(encoding="utf-8")) for path in sys.argv[1:]]' \
  "$skill_dir/scripts/secret_guard.py" "$skill_dir/scripts/evaluate_skill.py" \
  "$skill_dir/scripts/validate_skill.py" "$skill_dir/scripts/project_profile.py" \
  "$skill_dir/scripts/validate_evidence.py" "$skill_dir/scripts/audit_context.py" \
  "$skill_dir/scripts/test_project_profile.py" "$skill_dir/scripts/test_secret_guard.py" \
  "$skill_dir/scripts/test_evaluate_skill.py" "$skill_dir/scripts/test_validate_evidence.py"
python3 "$skill_dir/scripts/test_project_profile.py"
python3 "$skill_dir/scripts/test_secret_guard.py"
python3 "$skill_dir/scripts/test_evaluate_skill.py"
python3 "$skill_dir/scripts/test_validate_evidence.py"

printf 'ship-with-confidence: structure PASS\n'
