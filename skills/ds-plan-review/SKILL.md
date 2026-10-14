---
name: ds-plan-review
description: Reviews a data science solution plan against eight quality checks (problem fit, data feasibility, baseline discipline, validation integrity, leakage awareness, statistical rigour, reproducibility, client communication) plus fabrication and regulated-domain checks, scores each 1–5 and lists required fixes. Use when asked to "review this DS plan", "QA the solution plan", "check this ML approach for leakage or flaws", or when ds-solution-plan reaches its review step. Works on plans produced by this toolkit or written by others (Markdown, Word or pasted text).
---

# DS Plan Review (Quality Checks)

Review the plan as a sceptical principal data scientist and model-risk validator who did not write it.
Your job is to find what is wrong or unsupported, not to praise.

## Load
- `references/quality-gates.md`: rubric, fabrication checks and regulated-domain checks. **Always read.**
- `references/leakage-checklist.md`: to test the plan's leakage section for case-specificity.
- `references/solution-plan-template.md`: to check structure and Markdown conventions.

## Workflow
1. Read the entire plan. For a .docx file, extract its text first (e.g., with python-docx or pandoc).
2. Identify the use case's lens(es), industry, prediction point and data structure **independently**, then compare them with what the plan says.
3. Score checks G1–G8 (1–5) with a one-line justification each, citing the plan section.
4. Run the **fabrication checks**: quote each offending sentence.
5. Run the **regulated-domain checks** for Healthcare and BFSI.
6. Check internal **consistency**: metrics in §10 vs experiment cards; split windows in §12 vs walk-forward description;
   data sources in §5 vs features in §7; risks in §18 vs mitigations; roadmap vs open questions (blocking questions must be in Discovery).
7. Check **relevance**: flag sections included mechanically, and missing sections that the lens requires.

## Output
```
## Plan Review: <plan title>
| Check | Score (1–5) | Justification | Required fix |
### Fabrication findings        (quote + fix, or "None found")
### Consistency issues
### Missing / irrelevant sections
### Verdict: Client-ready | Needs revision (list the blocking fixes in priority order)
```
A plan is **Client-ready** only if every check scores ≥ 4 and there are no fabrication findings.

## Guardrails
- Be specific: cite sections and quote text. Generic advice is not useful.
- Do not rewrite the whole plan. List the fixes; the orchestrator applies them.
