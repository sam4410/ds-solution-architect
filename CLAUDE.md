# Working on this repository

This repo is the **ds-solution-architect** Claude Code plugin. When changing it:

- Edit reference knowledge **only in `shared/references/`**, then run `python scripts/build.py`. Never edit the copies
  in `skills/*/references/` directly, except `skills/ds-solution-plan/references/routing-matrix.md`, which is skill-specific.
- Keep each `SKILL.md` focused on workflow (under about 300 lines). Put catalogs and detail in references.
- Frontmatter: `name` must equal the folder name; `description` must be third-person, rich in trigger phrases, and ≤ 1024 characters.
- Every specialist skill returns the shared output contract: section headings, then Facts / Assumptions / Open questions, then Decision rows.
- Never add example numbers that could be read as expected performance.
- Run `python scripts/validate.py` and `claude plugin validate .` before committing; run `bash evals/run_evals.sh` after behavioural changes.
- Bump the version in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and update `CHANGELOG.md`.
