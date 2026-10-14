# Data Science Solution Architect: Claude Code plugin

Give it a client use case. It returns a rigorous, implementation-ready data science / ML solution plan as a
**Word document**.

The plugin makes Claude work like a Principal Data Scientist / ML Architect. It frames the problem
(Exploratory / Predictive / Inferential / Causal), checks data feasibility, plans preprocessing, baselines,
algorithm trade-offs, metrics, experiments and hyperparameters, and designs train/test and walk-forward validation
with leakage controls. It also covers hypothesis tests and causal designs, deployment and monitoring, risks and a
phased roadmap. Every plan is reviewed against eight quality checks before it reaches you. **Healthcare, BFSI and
Retail** domain packs are built in.

---

## What's inside

| Component | Purpose |
|---|---|
| `ds-solution-plan` (skill) | **Entry point.** Handles intake, depth mode, routing to specialists, assembly, review and Word export |
| `ds-problem-framing` | Simple lens, ML domain, decision, prediction point, unit, target, horizon, estimand, success criteria |
| `ds-data-assessment` | Internal/external sources tagged *Confirmed / Assumed / To investigate*, feasibility, target construction, preprocessing plan |
| `ds-model-selection` | Baselines, then a prioritised list of candidate algorithms with trade-offs and reject-if criteria |
| `ds-experiment-design` | Experiment stages E0–E8, experiment cards, hyperparameter priorities, tuning strategy, reproducibility |
| `ds-validation-leakage` | Split strategy that mirrors deployment, walk-forward specification, case-specific leakage audit |
| `ds-statistical-inference` | Hypotheses, tests, effect sizes and CIs, power/MDE, multiple testing, A/B and causal designs |
| `ds-evaluation-deployment` | Metric tiers, thresholds, calibration, fairness, serving, monitoring, retraining, governance |
| `ds-plan-review` | Quality-check reviewer: scores the 8 checks plus fabrication and regulated-domain checks |
| `agents/ds-plan-reviewer` | Independent reviewer agent (Claude Code), so the drafter doesn't grade its own work |
| `skills/*/references/` | Catalogs: algorithms, metrics, validation, leakage, preprocessing, statistical tests, causal designs, experiments, deployment, plan template, quality checks, worked examples, domain packs |
| `skills/ds-solution-plan/scripts/md_to_docx.py` | Converts the Markdown plan into a styled Word document (cover page, TOC, headers/footers, styled tables, colour-coded status tags) |

### How routing works
Framing and data assessment always run. The other specialists run only when the use case needs them:

| Lens | Specialists invoked |
|---|---|
| Predictive (forecasting, classification, regression, ranking, anomaly, NLP, CV, survival) | model-selection, validation-leakage, experiment-design, evaluation-deployment |
| Inferential (is the difference real, and how big?) | statistical-inference (others light or skipped) |
| Causal ("did X cause Y?", "impact of the intervention") | statistical-inference (causal designs) plus light validation and evaluation |
| Exploratory / segmentation | light model-selection (clustering/EDA) and evaluation |
| Ambiguous / insufficient information | **Quick triage**: candidate framings, deciding questions, discovery plan |

Mixed requests are split into separate analyses, each with its own target and validation. Depth modes are
**Quick triage**, **Standard** (default) and **Full blueprint** (ask for a "detailed" or "full" plan).

---

## Installation

### Prerequisites
- Claude Code (CLI, desktop or IDE extension), or the Claude desktop app.
- Python 3.9+ with **python-docx** for the Word output: `pip install python-docx`.
  If that's not available, the plugin falls back to `pandoc`. If neither is available, you get the Markdown file.

### Option A: Claude Code, from GitHub (recommended)
```text
/plugin marketplace add sam4410/ds-solution-architect
/plugin install ds-solution-architect@ds-solution-architect-marketplace
```
The repository is private, so your machine needs git access to it (for example via `gh auth login` or a credential manager).
To update later: `/plugin marketplace update ds-solution-architect-marketplace`.

### Option B: Claude Code, from a local folder (for development)
```bash
claude --plugin-dir "/path/to/ds-solution-architect"
```
Or add the folder as a local marketplace: `/plugin marketplace add ./ds-solution-architect`.

### Option C: Claude desktop app (upload)
Run `python scripts/package.py`, then use the files in `dist/`:
- `ds-solution-architect-<version>.plugin` (identical to the `.zip` next to it): upload it as a plugin in the desktop app,
  or drop it into a chat, where it shows an install button.
- `dist/skills/<skill>.zip`: one zip per skill, for uploading individual skills under *Settings → Capabilities → Skills*.
  Upload **all nine** so the orchestrator can call the specialists.

---

## Usage

Describe the use case and ask for a plan. The skill triggers on its own:

> *"Here's the client brief: a hospital group wants to predict 30-day readmissions at discharge so care managers can
> call the riskiest 40 patients a day. They have 4 years of EHR data. Prepare the solution plan."*

Or invoke it explicitly:
```text
/ds-solution-architect:ds-solution-plan <paste the use case or point to a brief file>
```

You can also use the specialists on their own:
- "Design a walk-forward backtest for this weekly SKU forecast" → `ds-validation-leakage`
- "Is the difference in approval rates between these two branches significant?" → `ds-statistical-inference`
- "Review this ML plan my colleague wrote" → `ds-plan-review`

**Output:** `solution-plans/<slug>-<date>.docx` (plus the `.md` source) in your working directory.
When Word asks to update fields on opening, click **Yes** to build the table of contents.

Tips:
- Attach or paste the real brief. The more the plugin knows about the decision, target, timing, data and constraints, the fewer assumptions it has to make.
- Say "full blueprint" for regulated or high-stakes work, or "quick triage" for a first conversation.
- When information is missing, the plan lists open client questions instead of guessing. Use them in your discovery call.

---

## Customising

- **Edit knowledge in `shared/references/` only**, then run `python scripts/build.py` to copy the files into the skills that use them
  (the mapping is in `shared/skill-references.json`). Each skill keeps its own copy so it works when uploaded alone.
- **Add a domain pack:** create `shared/references/domain-<name>.md` (follow the structure of the existing packs), add it to the mapping,
  and add detection keywords to `skills/ds-solution-plan/references/routing-matrix.md`.
- **Change the document look:** edit the colours and fonts at the top of `md_to_docx.py`. To change the plan structure, edit `solution-plan-template.md`.
- **Validate:** `python scripts/validate.py` (structure, frontmatter, references, sync, converter) and `claude plugin validate .`.
- **Bump the version** in `.claude-plugin/plugin.json` and `marketplace.json`, and update `CHANGELOG.md`.

## Testing
`bash evals/run_evals.sh` runs the scenarios in `evals/scenarios/` headless through the plugin, then has an independent
reviewer pass grade each plan against the quality checks and the scenario's expected behaviours. Results are saved in `evals/results/<run-id>/`.
See `evals/README.md`.

## MCP and connectors (optional, not required)
The toolkit works fully without any MCP server. These integrations are planned for later versions:
1. Python/Jupyter execution for data profiling and leakage audits on real (de-identified) extracts.
2. Read-only database or warehouse schema inspection.
3. Experiment tracking (e.g., MLflow).
4. Delivery connectors you already use: Atlassian (roadmap as Jira epics, plan to Confluence), Google Drive (briefs), GitHub.
Use read-only, least-privilege access, and never send client data to external services without explicit approval.

## Limitations
- Plans are only as good as the brief. Data availability is never assumed: sources are tagged, and open questions are listed.
- Regulatory content gives orientation only and is not legal advice. Always confirm with the client's compliance team.
- No numeric performance estimates are produced. Targets are written as acceptance criteria to agree with the client.
- The Word table of contents builds when fields are updated on opening.

## Repository layout
```
.claude-plugin/        plugin.json, marketplace.json
skills/                9 skills (SKILL.md + references/ + scripts/)
agents/                ds-plan-reviewer.md
shared/references/     single source of truth for reference catalogs
scripts/               build.py, validate.py, package.py
evals/                 scenarios, fixtures, runner, results
```
