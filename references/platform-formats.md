# Platform Import Formats

The user picks one platform at intake (Phase 0). Phase 6 then delivers:
1. `<StoryID>_TestCases.xlsx` — the full workbook, plus an `Import - <Platform>` sheet in the platform layout.
2. `<StoryID>_TestCases_<platform>_import.csv` — the same layout as UTF-8 CSV, the file to upload.

Column names below are the ones the importers expect by default; Jira-family importers let you map
columns in their wizard, so if a team's instance uses custom fields, they map them there.

## Platform keys and intake fields

Any intake field left blank gets a placeholder the user replaces (Excel Find & Replace) before importing —
the importers reject paths, users or components that don't exist:
`area_path` → `<Project>\<Area>`, `iteration_path` → `<Project>\<Iteration>`, `assigned_to` → `<user@company.com>`,
`folder` → `/<Folder>`, `owner` → `<owner>`, `component` → `<Component>`, `issue_type` → `Test`.

| Key (`platform` in JSON) | Platform | Ask at intake (`platform_fields`) — all optional, blank → placeholder |
|---|---|---|
| `azure-devops` | Azure DevOps Test Plans | `area_path`, `iteration_path`, `assigned_to` |
| `xray` | Jira + Xray | — (project chosen in the import wizard) |
| `zephyr-scale` | Jira + Zephyr Scale | `folder` (e.g. `/Login`), `owner` |
| `zephyr-squad` | Jira + Zephyr Squad | — |
| `jira` | Plain Jira, no test plugin | `issue_type` (default `Test`), `component` |
| `none` | No upload, workbook only | — |

## Priority mapping
| Skill | Azure DevOps | Xray / Zephyr Squad / Jira | Zephyr Scale |
|---|---|---|---|
| P1 | 1 | High | High |
| P2 | 2 | Medium | Normal |
| P3 | 3 | Low | Low |

## Steps
Steps can be plain strings or objects `{"action", "data", "expected"}`. If the last step has no
`expected`, the TC's `expected_result` is placed there. If no step has `data`, the TC's `test_data`
goes on step 1.

## Layouts

### Azure DevOps — one row per step; test-case fields only on the first row
`ID, Work Item Type, Title, Test Step, Step Action, Step Expected, Area Path, Iteration Path, Assigned To, State, Priority`
- `ID` blank (new test cases), `Work Item Type` = `Test Case`, `State` = `Design`.
- No data column: step data is appended to the action as `Data: …`.
- Preconditions become step 1: `Preconditions: …` → `Preconditions are met`.
- Import: Test Plans → open a suite → **Import test cases** → choose the CSV.

### Xray — one row per step; `Test ID` repeated on every row (groups steps)
`Test ID, Summary, Description, Test Type, Priority, Labels, Action, Data, Expected Result`
- `Test Type` = `Manual`, `Labels` = story ID, `Description` = story, AC IDs, preconditions, remarks.
- Import: Xray → **Test Case Importer** → CSV → map columns; set "Test ID" as the grouping column.

### Zephyr Scale — one row per step; test-case fields only on the first row
`Name, Objective, Precondition, Folder, Status, Priority, Labels, Owner, Test Script (Step-by-Step) - Step, Test Script (Step-by-Step) - Test Data, Test Script (Step-by-Step) - Expected Result`
- `Status` = `Draft`, `Objective` = story ID + AC IDs.
- Import: Zephyr Scale → Tests → **Import** → CSV → map columns.

### Zephyr Squad — one row per step; `Test Case ID` repeated on every row
`Test Case ID, Summary, Description, Priority, Labels, Step, Test Data, Expected Result`
- Import: Zephyr → **Import Tests** → choose discriminator **"By ID change"** → map columns.

### Plain Jira — one row per test case
`Summary, Issue Type, Priority, Labels, Component, Description`
- `Description` holds story/AC IDs, preconditions, numbered steps with data and expected results.
- Import: Jira settings → System → **External system import → CSV** (or project → Import issues).
