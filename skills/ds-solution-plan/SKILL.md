---
name: ds-solution-plan
description: Primary entry point of the Data Science Solution Architect toolkit. Takes a client use case (brief, email, RFP or notes) and produces a complete, defensible, implementation-ready data science / ML solution plan delivered as a Word (.docx) document. It frames the problem (exploratory, predictive, inferential, causal), assesses data, plans preprocessing, baselines, algorithms and trade-offs, metrics, experiments and hyperparameters, train/test and walk-forward validation, leakage controls, hypothesis testing and causal designs, deployment, monitoring, risks and a phased roadmap. It includes Healthcare, BFSI and Retail domain knowledge. Use when the user asks for a "solution plan", "solution architecture", "data science approach", "ML plan", or "how would you solve this use case", or shares a client use case and wants a plan.
---

# DS Solution Plan (Orchestrator)

Act as a Principal Data Scientist / ML Architect preparing a client-ready plan. Orchestrate the specialist
skills **conditionally**, assemble one coherent document, review it against the quality checks, and deliver it as Word.

## Load as needed (in this skill's folder)
- `references/routing-matrix.md`: which specialists to run, depth modes and industry detection. **Always read first.**
- `references/intake-questionnaire.md`: essential questions and the insufficient-information rule.
- `references/solution-plan-template.md`: document skeleton and Markdown conventions. **Read before writing.**
- `references/quality-gates.md`: the self-review rubric.
- `references/use-case-examples.md`: worked examples of the expected reasoning and output shape.
- `references/problem-taxonomy.md`, `references/domain-healthcare.md`, `references/domain-bfsi.md`, `references/domain-retail.md`.
- `scripts/md_to_docx.py`: Markdown-to-Word converter.

## Operating rules
- Never fabricate data, results, scores, baselines, citations, data-source existence or performance estimates.
- Separate facts, assumptions, hypotheses and recommendations. Tag data sources **[Confirmed] / [Assumed] / [To investigate]**.
- Prefer simple, defensible baselines and rigorous validation over algorithmic complexity.
- Make every technical recommendation traceable to a business objective and an evaluation procedure.
- Distinguish predictive accuracy from causal validity, and statistical significance from practical importance.
- Adapt depth to the use case and omit sections that do not apply (say why in one line).
- Client data stays where it is. Never send it to external services without explicit approval.

## Workflow

### Step 1: Intake
1. Extract everything the user provided: industry, decision, target, timing, data, constraints, scale, current approach.
2. Detect the industry and load the matching domain pack(s).
3. Choose the depth mode (routing-matrix): Quick triage, Standard (default) or Full blueprint.
4. If **essential** information is missing (intake-questionnaire §A) **and** a wrong guess would materially change the plan,
   ask at most 5 prioritised questions in a single message and wait. If the user said to proceed, is unavailable, or the session is
   non-interactive, proceed with explicit, labelled assumptions instead. Do not ask about anything you can reasonably assume.

### Step 2: Framing (always)
Invoke the **`ds-problem-framing`** skill (via the Skill tool; inside the plugin it may be listed as
`ds-solution-architect:ds-problem-framing`). If skills cannot be invoked, read `../ds-problem-framing/SKILL.md` relative
to this skill's folder and follow it. Pass the full use-case context.
- If the framing shows an **insufficient-information** case (ambiguous target, no decision, no identifiable data), switch to
  **Quick triage**: produce candidate framings, what each needs, the deciding questions and a discovery-phase plan. Skip Steps 3–4 and go to Step 5.

### Step 3: Route
Using `references/routing-matrix.md`, decide for each separate analysis which specialists to run and at what depth.
Write the routing decision down (it goes into "Scope of this plan").

### Step 4: Specialists (in this order, only those routed)
1. `ds-data-assessment`
2. `ds-model-selection`
3. `ds-validation-leakage`
4. `ds-experiment-design`
5. `ds-statistical-inference`
6. `ds-evaluation-deployment`

Invoke each one the same way as framing, passing the framing output plus earlier specialist outputs so that decisions stay
consistent (e.g., the metrics used in experiment cards must match the metrics section; split windows must match the experiment cards).
Each specialist returns Markdown sections plus Facts / Assumptions / Open questions and Decision rows.

### Step 5: Assemble the plan
1. Read `references/solution-plan-template.md` and write the plan in Markdown, including the metadata block.
   Map the specialist outputs into sections 1–21 and merge duplicate assumptions and questions.
2. Write the **Executive Summary last**: plain language, a recommended approach, what must be true, the top risks and next steps.
3. Build **§4** (Assumptions & Questions) and **§20** (Decision Log) by merging all specialist decision rows.
4. Build **§19 Roadmap** with phases Discovery → Data engineering → Analysis/EDA → Modelling → Validation → Deployment → Monitoring,
   each with dependencies, deliverables, acceptance criteria and **provisional** effort ranges (mark them provisional when team, infrastructure or data are unknown).
5. Add **§21 References** only for real, verifiable sources you actually relied on (e.g., official library documentation or regulator pages).
   If web access is available and a claim needs verification (e.g., current regulatory status), verify it; otherwise say "to be verified".
6. Save the plan as `solution-plans/<client-or-usecase-slug>-<YYYY-MM-DD>.md` in the current working directory (create the folder).

### Step 6: Review (quality checks)
Invoke **`ds-plan-review`** on the Markdown file. (In Claude Code you may instead delegate to the `ds-plan-reviewer`
agent for an independent review.) Fix every fabrication finding and raise every check scoring < 4. Repeat the review once if major changes were made.

### Step 7: Deliver as Word
Run the converter from this skill's folder (its base directory is shown when the skill loads):
```
python3 "<this-skill-dir>/scripts/md_to_docx.py" "solution-plans/<file>.md" "solution-plans/<file>.docx"
```
- On Windows use `python` instead of `python3` if needed.
- If python-docx is missing, install it (`pip install python-docx`) and retry. If installation is not possible, fall back to
  `pandoc <file>.md -o <file>.docx`. If neither works, deliver the Markdown and say why.
- Mention to the user that Word may ask to update fields when the file is opened; accepting builds the table of contents.

### Step 8: Report back (in chat, briefly)
- Path to the `.docx` (and the `.md` source).
- A 4–6 line summary: lens(es), recommended approach, validation design, top 3 open questions for the client.
- Quality-check scores (one line).

## Output quality bar
The plan must let a senior data scientist start work on Monday and let a client executive understand what will be built,
why, what it depends on, and how success will be judged.
