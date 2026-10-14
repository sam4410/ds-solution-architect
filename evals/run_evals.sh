#!/usr/bin/env bash
# Run evaluation scenarios headless against the local plugin, then grade each plan with an
# independent reviewer pass.
#
# Usage:  bash evals/run_evals.sh [scenario-glob]      e.g.  bash evals/run_evals.sh "0[12]*"
# Output: evals/results/<run-id>/<scenario>/  (transcript.jsonl, solution-plans/*.md|*.docx, review.md)
#
# Requires: Claude Code CLI (`claude`) logged in; python-docx.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATTERN="${1:-*}"
RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/evals/results/$RUN_ID"
mkdir -p "$OUT"

run_one() {
  local scen="$1"
  local name; name="$(basename "$scen" .md)"
  local dir="$OUT/$name"
  mkdir -p "$dir"
  # Prompt = text between '## Prompt' and the next '## ' heading
  local prompt
  prompt="$(awk '/^## Prompt/{f=1;next}/^## /{f=0}f' "$scen")"
  prompt="$prompt

(Evaluation run: the client is not available for questions — proceed with clearly labelled assumptions.)"
  (cd "$dir" && timeout 3600 claude -p "$prompt" \
      --plugin-dir "$ROOT" \
      --dangerously-skip-permissions \
      --output-format stream-json --verbose > transcript.jsonl 2> stderr.log) || echo "[$name] generation exited non-zero"

  local plan
  plan="$(ls "$dir"/solution-plans/*.md 2>/dev/null | head -1 || true)"
  if [[ -z "$plan" ]]; then
    echo "[$name] NO PLAN PRODUCED" | tee "$dir/review.md"
    return
  fi
  local expected
  expected="$(awk '/^## Expected behaviours/{f=1}f' "$scen")"
  (cd "$dir" && timeout 1800 claude -p "You are an independent grader. Using the ds-plan-review skill, review the plan at '$plan'.
Then ALSO check it against these scenario-specific expected behaviours and mark each PASS/PARTIAL/FAIL with a one-line reason:

$expected

Output the review in Markdown only." \
      --plugin-dir "$ROOT" --dangerously-skip-permissions > review.md 2>> stderr.log) || echo "[$name] review exited non-zero"
  echo "[$name] done: $(ls "$dir"/solution-plans/ | tr '\n' ' ')"
}

for scen in "$ROOT"/evals/scenarios/$PATTERN.md; do
  run_one "$scen" &
done
wait
echo "Results in $OUT"
