# Excel Output Format (Phase 6)

## Input JSON for `scripts/build_testcases_xlsx.py`

```json
{
  "project": "Online Shop",
  "platform": "azure-devops",
  "platform_fields": {"area_path": "Shop\\Web", "iteration_path": "Shop\\Sprint 12", "assigned_to": ""},
  "stories": [
    {
      "id": "US-01",
      "title": "Login with email",
      "text": "As a registered customer I want to log in with email and password so that I can see my orders.",
      "acceptance_criteria": [
        {"id": "AC-01", "text": "Given a registered customer, When valid email and password are submitted, Then the My Orders page opens."}
      ]
    }
  ],
  "gaps": [
    {"id": "G-01", "story_id": "US-01", "category": "Validation", "severity": "Major",
     "finding": "Password rules not defined", "question": "Min/max length?",
     "resolution": "8–64 chars", "status": "Resolved"}
  ],
  "assumptions": [
    {"id": "A-01", "story_id": "US-01", "text": "Lockout after 5 failed attempts", "source": "Assumed – not confirmed"}
  ],
  "test_cases": [
    {"id": "TC-001", "story_id": "US-01", "title": "Login – valid credentials – My Orders opens_P",
     "ac_ids": ["AC-01"], "type": "Positive", "technique": "EP", "priority": "P1",
     "preconditions": "Customer john.doe@test.com exists", "steps": ["Open /login", "Enter email", "Enter password", "Click Log in"],
     "test_data": "john.doe@test.com / Passw0rd!", "expected_result": "My Orders page is displayed", "remarks": ""}
  ]
}
```

Optional `"defaults": {"story_id": "US-01", "preconditions": "...", "technique": "EP"}` is merged into every test case
(a TC's own value wins) — use it instead of repeating shared values on each TC.
`steps` may be a list (numbered automatically) or a string; list items may be strings or
`{"action", "data", "expected"}` objects. `gaps`, `assumptions` and `remarks` are optional.
`platform` is one of `azure-devops`, `xray`, `zephyr-scale`, `zephyr-squad`, `jira`, `none` (default `none`);
`platform_fields` keys per platform are in [platform-formats.md](platform-formats.md).

## Workbook layout

| Sheet | Columns |
|---|---|
| **Test Cases** | TC ID · Story ID · Title · AC IDs · Type · Technique · Priority · Preconditions · Steps · Test Data · Expected Result · Actual Result · Status · Executed By · Date · Remarks |
| **Traceability** | Story ID · AC ID · Acceptance Criterion · TC IDs · TC Count · Covered |
| **Gaps & Assumptions** | ID · Story ID · Kind · Category · Severity · Finding · Question · Resolution · Status |
| **Stories** | Story ID · Title · Story · Acceptance Criteria |
| **Summary** | Totals by Type, by Priority, AC coverage % |
| **Import - &lt;Platform&gt;** | Only when a platform is picked — the platform layout from [platform-formats.md](platform-formats.md) |

`Actual Result`, `Executed By`, `Date` are left blank for the tester; `Status` has a dropdown
(Not Run, Pass, Fail, Blocked, N/A) defaulting to `Not Run`.
