# /readytotest

A [Claude Code](https://claude.com/claude-code) skill that reviews user stories like a senior BA and QA team,
finds gaps and ambiguities, runs a clarification loop with you until the story is **Ready**, then designs
traceable test cases and delivers them as an **Excel (.xlsx)** file — plus a CSV ready to import into your test tool.

## How it works

The skill acts as a small delivery team. You are always the **Product Owner** — it never answers business questions for you.

| Role | Owns |
|---|---|
| Business Analyst | Phases 1–3 |
| Product Owner (**you**) | Answers in Phase 2 |
| QA Test Designer | Phase 4 |
| QA Reviewer | Phase 5 |

| Phase | What happens | Stops for you? |
|---|---|---|
| 0 – Intake | Story, acceptance criteria, context, upload platform | |
| 1 – Review | Readiness score, INVEST check, gap table (Blocker / Major / Minor) with a question and suggested answer per gap | ✅ Gate |
| 2 – Clarification loop | Up to 7 questions per round; shows only what changed; ends at the Definition of Ready | ✅ Gate each round |
| 3 – Refined story | Business rules `BR-xx`, acceptance criteria in Given / When / Then | ✅ Gate |
| 4 – Test design | EP, BVA, decision tables, state transitions, error guessing; every title ends in `_P` (expected success) or `_N` (expected error / rejection) | |
| 5 – QA review | Coverage, traceability, no duplicates, concrete data, observable results | |
| 6 – Deliver Excel | Workbook + platform import CSV | |

### Golden rules
- **Never invents requirements** — anything missing becomes a gap and you are asked.
- **Assumptions are explicit** — recorded as `A-01…` ("Assumed – not confirmed") and included in the Excel file.
- **Everything traces back** — `US-01` → `AC-01` → `G-01` / `A-01` → `TC-001`. A test case that traces to nothing is deleted.

## Output

`<StoryID>_TestCases.xlsx` with sheets: **Test Cases**, **Traceability**, **Gaps & Assumptions**, **Stories**, **Summary**,
and an **Import - &lt;Platform&gt;** sheet — plus `<StoryID>_TestCases_<platform>_import.csv`.

Supported upload platforms: Azure DevOps Test Plans · Jira + Xray · Jira + Zephyr Scale · Jira + Zephyr Squad · Plain Jira · None (Excel only).

## Install

Clone into your Claude Code skills folder:

```bash
git clone https://github.com/shadyusef/readytotest ~/.claude/skills/readytotest
```

On Windows (PowerShell):

```powershell
git clone https://github.com/shadyusef/readytotest "$env:USERPROFILE\.claude\skills\readytotest"
```

The Excel builder needs Python 3 with `openpyxl`:

```bash
pip install openpyxl
```

## Use

In Claude Code, type `/readytotest` and paste a user story (or a Jira / Azure DevOps ticket).
The skill also triggers when you ask Claude to review a story, find gaps, check if it is ready, or write test cases.

Shortcuts:

| Command | Effect |
|---|---|
| `quick` | Skip the clarification loop — gaps become assumptions using the suggested answers, risks listed |
| `review only` | Stop after Phase 1 |
| `tests only` | Story is already Ready — start at Phase 3 (still flags Blockers) |

## Files

```
SKILL.md                         # the skill: roles, rules, phases
references/review-checklist.md   # Phase 1 checklist
references/test-design-rules.md  # Phase 4 techniques and TC fields
references/excel-format.md       # JSON input + workbook layout
references/platform-formats.md   # import layouts per platform
scripts/build_testcases_xlsx.py  # builds the .xlsx and import .csv (run --selftest to check)
```

## License

[MIT](LICENSE)
