"""Build the test-case workbook from the JSON described in references/excel-format.md.

Usage:  python build_testcases_xlsx.py input.json output.xlsx
        python build_testcases_xlsx.py --selftest
"""
import csv
import json
import sys
from collections import Counter

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")
STATUSES = ["Not Run", "Pass", "Fail", "Blocked", "N/A"]

TC_COLS = [  # (header, width)
    ("TC ID", 10), ("Story ID", 10), ("Title", 40), ("AC IDs", 14), ("Type", 13),
    ("Technique", 14), ("Priority", 9), ("Preconditions", 30), ("Steps", 45),
    ("Test Data", 28), ("Expected Result", 40), ("Actual Result", 30), ("Status", 11),
    ("Executed By", 14), ("Date", 12), ("Remarks", 25),
]


def add_sheet(wb, title, cols, rows):
    ws = wb.create_sheet(title)
    ws.append([c for c, _ in cols])
    for i, (_, width) in enumerate(cols, start=1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = width
        ws.cell(1, i).fill, ws.cell(1, i).font = HEADER_FILL, HEADER_FONT
    for row in rows:
        ws.append(row)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = WRAP
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def norm_steps(tc):
    """Steps as [(action, data, expected)]; TC-level expected/test data fill the last/first step."""
    raw = tc.get("steps") or []
    raw = raw if isinstance(raw, list) else [raw]
    steps = [(s, "", "") if isinstance(s, str) else (s["action"], s.get("data", ""), s.get("expected", ""))
             for s in raw] or [("", "", "")]
    if not steps[-1][2]:
        steps[-1] = (steps[-1][0], steps[-1][1], tc["expected_result"])
    if tc.get("test_data") and not any(d for _, d, _ in steps):
        steps[0] = (steps[0][0], tc["test_data"], steps[0][2])
    return steps


def fmt_steps(steps):
    if not isinstance(steps, list):
        return steps or ""
    return "\n".join(f"{i}. {s}" if isinstance(s, str) else
                     f"{i}. {s['action']}" + (f" (Data: {s['data']})" if s.get("data") else "")
                     + (f" -> {s['expected']}" if s.get("expected") else "")
                     for i, s in enumerate(steps, start=1))


JIRA_PRIO = {"P1": "High", "P2": "Medium", "P3": "Low"}
# Blank intake fields get these; the user replaces them (Find & Replace) before importing.
PLACEHOLDERS = {"area_path": "<Project>\\<Area>", "iteration_path": "<Project>\\<Iteration>",
                "assigned_to": "<user@company.com>", "folder": "/<Folder>", "owner": "<owner>",
                "issue_type": "Test", "component": "<Component>"}


def describe(tc):
    text = f"Story: {tc['story_id']} | AC: {', '.join(tc['ac_ids'])}"
    if tc.get("preconditions"):
        text += f"\nPreconditions: {tc['preconditions']}"
    if tc.get("remarks"):
        text += f"\nRemarks: {tc['remarks']}"
    return text


def azure(tc, f):
    steps = norm_steps(tc)
    if tc.get("preconditions"):
        steps.insert(0, (f"Preconditions: {tc['preconditions']}", "", "Preconditions are met"))
    head = ["", "Test Case", tc["title"]]
    tail = [f.get("area_path", ""), f.get("iteration_path", ""), f.get("assigned_to", ""), "Design",
            tc.get("priority", "P2")[-1]]
    return [(head if i == 1 else ["", "", ""])
            + [i, a + (f"\nData: {d}" if d else ""), e]
            + (tail if i == 1 else [""] * len(tail))
            for i, (a, d, e) in enumerate(steps, start=1)]


def xray(tc, f):
    head = [tc["title"], describe(tc), "Manual", JIRA_PRIO.get(tc.get("priority"), "Medium"), tc["story_id"]]
    return [[tc["id"]] + (head if i == 0 else [""] * len(head)) + [a, d, e]
            for i, (a, d, e) in enumerate(norm_steps(tc))]


def zephyr_scale(tc, f):
    prio = {"P1": "High", "P2": "Normal", "P3": "Low"}.get(tc.get("priority"), "Normal")
    head = [tc["title"], f"Story: {tc['story_id']} | AC: {', '.join(tc['ac_ids'])}", tc.get("preconditions", ""),
            f.get("folder", ""), "Draft", prio, tc["story_id"], f.get("owner", "")]
    return [(head if i == 0 else [""] * len(head)) + [a, d, e] for i, (a, d, e) in enumerate(norm_steps(tc))]


def zephyr_squad(tc, f):
    head = [tc["title"], describe(tc), JIRA_PRIO.get(tc.get("priority"), "Medium"), tc["story_id"]]
    return [[tc["id"]] + (head if i == 0 else [""] * len(head)) + [a, d, e]
            for i, (a, d, e) in enumerate(norm_steps(tc))]


def jira(tc, f):
    lines = [describe(tc), "", "Steps:"]
    lines += [f"{i}. {a}" + (f" (Data: {d})" if d else "") + (f"\n   Expected: {e}" if e else "")
              for i, (a, d, e) in enumerate(norm_steps(tc), start=1)]
    return [[tc["title"], f.get("issue_type") or "Test", JIRA_PRIO.get(tc.get("priority"), "Medium"),
             tc["story_id"], f.get("component", ""), "\n".join(lines)]]


PLATFORMS = {  # key: (sheet label, columns, row builder)
    "azure-devops": ("Azure DevOps", ["ID", "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected",
                                      "Area Path", "Iteration Path", "Assigned To", "State", "Priority"], azure),
    "xray": ("Xray", ["Test ID", "Summary", "Description", "Test Type", "Priority", "Labels",
                      "Action", "Data", "Expected Result"], xray),
    "zephyr-scale": ("Zephyr Scale", ["Name", "Objective", "Precondition", "Folder", "Status", "Priority", "Labels",
                                      "Owner", "Test Script (Step-by-Step) - Step",
                                      "Test Script (Step-by-Step) - Test Data",
                                      "Test Script (Step-by-Step) - Expected Result"], zephyr_scale),
    "zephyr-squad": ("Zephyr Squad", ["Test Case ID", "Summary", "Description", "Priority", "Labels",
                                      "Step", "Test Data", "Expected Result"], zephyr_squad),
    "jira": ("Jira", ["Summary", "Issue Type", "Priority", "Labels", "Component", "Description"], jira),
}


def build(data, out_path):
    stories = data.get("stories", [])
    # "defaults" holds fields shared by many TCs (story_id, preconditions, ...) so the JSON stays small
    tcs = [{**data.get("defaults", {}), **tc} for tc in data.get("test_cases", [])]
    platform = data.get("platform") or "none"
    if platform != "none" and platform not in PLATFORMS:
        raise ValueError(f"unknown platform {platform!r}; use one of: none, {', '.join(PLATFORMS)}")
    known_acs = {(s["id"], ac["id"]) for s in stories for ac in s.get("acceptance_criteria", [])}
    known_as = {a["id"] for a in data.get("assumptions", [])}
    for tc in tcs:  # traceability rule: every TC must point at a real AC or assumption
        refs = tc.get("ac_ids", [])
        if not refs or any((tc["story_id"], r) not in known_acs and r not in known_as for r in refs):
            raise ValueError(f"{tc['id']} references unknown or no AC/assumption: {refs}")
        suffix = tc["title"][-2:]
        expected = {"Positive": "_P", "Negative": "_N"}.get(tc.get("type"))
        if suffix not in ("_P", "_N") or (expected and suffix != expected):
            raise ValueError(f"{tc['id']} title must end with {expected or '_P or _N'}: {tc['title']!r}")

    wb = Workbook()
    wb.remove(wb.active)

    ws = add_sheet(wb, "Test Cases", TC_COLS, [[
        tc["id"], tc["story_id"], tc["title"], ", ".join(tc["ac_ids"]), tc.get("type", ""),
        tc.get("technique", ""), tc.get("priority", ""), tc.get("preconditions", ""),
        fmt_steps(tc.get("steps")), tc.get("test_data", ""), tc["expected_result"],
        "", "Not Run", "", "", tc.get("remarks", ""),
    ] for tc in tcs])
    if tcs:
        dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"M2:M{len(tcs) + 1}")

    trace_rows = []
    for s in stories:
        for ac in s.get("acceptance_criteria", []):
            ids = [tc["id"] for tc in tcs if tc["story_id"] == s["id"] and ac["id"] in tc["ac_ids"]]
            trace_rows.append([s["id"], ac["id"], ac["text"], ", ".join(ids), len(ids), "Yes" if ids else "NO"])
    add_sheet(wb, "Traceability", [("Story ID", 10), ("AC ID", 9), ("Acceptance Criterion", 60),
                                   ("TC IDs", 40), ("TC Count", 10), ("Covered", 10)], trace_rows)

    ga_rows = [[g["id"], g.get("story_id", ""), "Gap", g.get("category", ""), g.get("severity", ""),
                g.get("finding", ""), g.get("question", ""), g.get("resolution", ""), g.get("status", "")]
               for g in data.get("gaps", [])]
    ga_rows += [[a["id"], a.get("story_id", ""), "Assumption", "", "", a["text"], "", a.get("source", ""), "Assumed"]
                for a in data.get("assumptions", [])]
    add_sheet(wb, "Gaps & Assumptions", [("ID", 8), ("Story ID", 10), ("Kind", 12), ("Category", 16),
                                         ("Severity", 10), ("Finding", 40), ("Question", 40),
                                         ("Resolution", 40), ("Status", 11)], ga_rows)

    add_sheet(wb, "Stories", [("Story ID", 10), ("Title", 30), ("Story", 60), ("Acceptance Criteria", 80)], [
        [s["id"], s.get("title", ""), s.get("text", ""),
         "\n".join(f"{ac['id']}: {ac['text']}" for ac in s.get("acceptance_criteria", []))] for s in stories])

    covered = sum(1 for r in trace_rows if r[4])
    summary = [["Project", data.get("project", "")], ["Total test cases", len(tcs)],
               ["AC coverage", f"{covered}/{len(trace_rows)} ({covered * 100 // max(len(trace_rows), 1)}%)"]]
    summary += [[f"Type: {k}", v] for k, v in sorted(Counter(tc.get("type", "") for tc in tcs).items())]
    summary += [[f"Priority: {k}", v] for k, v in sorted(Counter(tc.get("priority", "") for tc in tcs).items())]
    add_sheet(wb, "Summary", [("Metric", 30), ("Value", 25)], summary)

    csv_path = None
    if platform != "none":
        label, cols, row_fn = PLATFORMS[platform]
        given = data.get("platform_fields", {})
        fields = {k: given.get(k) or v for k, v in PLACEHOLDERS.items()}
        rows = [r for tc in tcs for r in row_fn(tc, fields)]
        add_sheet(wb, f"Import - {label}", [(c, 30 if "Desc" in c or "Action" in c or "Step" in c else 16)
                                            for c in cols], rows)
        csv_path = out_path.rsplit(".", 1)[0] + f"_{platform}_import.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(cols)
            writer.writerows(rows)

    wb.save(out_path)
    return covered, len(trace_rows), csv_path


def selftest():
    import os
    import tempfile
    data = {
        "project": "Demo",
        "stories": [{"id": "US-01", "title": "Login", "text": "As a customer I want to log in.",
                     "acceptance_criteria": [{"id": "AC-01", "text": "Valid login opens My Orders"},
                                             {"id": "AC-02", "text": "Wrong password shows error"}]}],
        "gaps": [{"id": "G-01", "story_id": "US-01", "severity": "Major", "finding": "No lockout rule",
                  "status": "Assumed"}],
        "assumptions": [{"id": "A-01", "story_id": "US-01", "text": "Lock after 5 tries"}],
        "test_cases": [
            {"id": "TC-001", "story_id": "US-01", "title": "Login – valid – opens_P", "ac_ids": ["AC-01"], "type": "Positive",
             "priority": "P1", "steps": ["Open login", "Submit"], "expected_result": "My Orders shown"},
            {"id": "TC-002", "story_id": "US-01", "title": "Login – 5 failures – locked_N", "ac_ids": ["A-01"], "type": "Negative",
             "priority": "P2", "steps": "Fail 5 times", "expected_result": "Account locked"},
        ],
    }
    path = os.path.join(tempfile.mkdtemp(), "t.xlsx")
    assert build(data, path) == (1, 2, None)  # AC-02 uncovered, no platform
    wb = load_workbook(path)
    assert wb.sheetnames == ["Test Cases", "Traceability", "Gaps & Assumptions", "Stories", "Summary"]
    assert wb["Test Cases"]["I2"].value == "1. Open login\n2. Submit"
    assert wb["Traceability"]["F3"].value == "NO"

    data["test_cases"][0].update(preconditions="User exists", test_data="a@b.com")
    expected_rows = {"azure-devops": 4, "xray": 3, "zephyr-scale": 3, "zephyr-squad": 3, "jira": 2}  # + preconditions step
    for key, n in expected_rows.items():
        data["platform"], data["platform_fields"] = key, {"area_path": "Shop\\Web"}
        csv_path = build(data, path)[2]
        with open(csv_path, encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == PLATFORMS[key][1] and len(rows) == 1 + n, (key, rows)
        assert load_workbook(path).sheetnames[-1] == f"Import - {PLATFORMS[key][0]}"
        if key == "azure-devops":
            assert rows[1][:4] == ["", "Test Case", "Login – valid – opens_P", "1"] and rows[1][6] == "Shop\\Web"
            assert rows[1][7:9] == ["<Project>\\<Iteration>", "<user@company.com>"]  # blanks -> placeholders
            assert rows[2][2] == "" and rows[2][4] == "Open login\nData: a@b.com" and rows[3][5] == "My Orders shown"
        if key == "xray":
            assert rows[2][0] == "TC-001" and rows[2][1] == "" and rows[2][8] == "My Orders shown"
    lean = json.loads(json.dumps(data))  # defaults fill missing fields; a TC's own value wins
    lean.update(platform="none", defaults={"story_id": "US-01", "preconditions": "Shared pre"})
    for tc in lean["test_cases"]:
        tc.pop("story_id")
    lean["test_cases"][1]["preconditions"] = "Own pre"
    build(lean, path)
    ws = load_workbook(path)["Test Cases"]
    assert [ws["B2"].value, ws["H2"].value, ws["H3"].value] == ["US-01", "User exists", "Own pre"], [c.value for c in ws[2]]
    lean["test_cases"][0].pop("preconditions")
    build(lean, path)
    assert load_workbook(path)["Test Cases"]["H2"].value == "Shared pre"

    data["platform"] = "testrail"
    try:
        build(data, path)
        raise AssertionError("unknown platform should fail")
    except ValueError:
        pass
    data["platform"] = "none"
    for field, bad in [("title", "Login – valid – opens_N"), ("title", "Login – valid – opens"), ("ac_ids", ["AC-99"])]:
        broken = json.loads(json.dumps(data))
        broken["test_cases"][0][field] = bad
        try:
            build(broken, path)
            raise AssertionError(f"{field}={bad!r} should fail")
        except ValueError:
            pass
    print("selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 3:
        with open(sys.argv[1], encoding="utf-8") as f:
            covered, total, csv_path = build(json.load(f), sys.argv[2])
        print(f"Wrote {sys.argv[2]} - AC coverage {covered}/{total}")
        if csv_path:
            print(f"Wrote import file {csv_path}")
        if covered < total:
            print("WARNING: some ACs have no test case - see the Traceability sheet")
    else:
        sys.exit(__doc__)
