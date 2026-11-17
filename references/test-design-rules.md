# Test Design Rules (Phase 4)

## Techniques — when to use each
| Technique | Use when | Produces |
|---|---|---|
| **Equivalence Partitioning (EP)** | Any input with valid/invalid classes | 1 TC per class (one valid class can share a TC) |
| **Boundary Value Analysis (BVA)** | Lengths, ranges, counts, dates, amounts | min−1, min, max, max+1 (plus min+1 / max−1 for money and dates) |
| **Decision Table** | 2+ conditions combine to decide an outcome | 1 TC per meaningful rule column |
| **State Transition** | Statuses / workflows | Every valid transition + key invalid ones |
| **Use-case / Scenario** | End-to-end flows across screens/services | Happy path + main alternate paths |
| **Error Guessing** | Always, last | Edge cases from the list below |

Put the technique name in the `Technique` column.

## Error-guessing list (pick what applies)
Empty / null · only spaces · leading/trailing spaces · very long text · special characters & emoji ·
SQL/script injection strings (`' OR 1=1 --`, `<script>alert(1)</script>`) · Unicode / RTL text ·
duplicate submit (double click) · back button after submit · refresh mid-flow · session expired ·
two users editing the same record · network loss / API timeout · zero, negative, decimal numbers ·
leap year, end of month, time-zone change · file: wrong type, 0 bytes, over size limit.

## Test case fields
| Field | Rule |
|---|---|
| ID | `TC-001`, sequential across the story |
| Title | `[Feature] – [condition] – [expected outcome]_P` or `…_N`, ≤ 100 chars. Suffix is mandatory on every TC: `_P` when the expected result is success / acceptance (valid input, allowed action), `_N` when it is an error / rejection / denial. Boundary, edge, permission and security TCs take `_P` or `_N` by the same rule. E.g. `Login – valid email and password – My Orders opens_P`, `Registration – password 7 chars (min−1) – validation error shown_N` |
| Story ID | `US-01` |
| AC IDs | Comma-separated, e.g. `AC-01, AC-03` (or `A-02` for assumption-based) |
| Type | `Positive` · `Negative` · `Boundary` · `Edge` · `Security` · `Permission` · `UI` · `Non-functional` |
| Technique | From the table above |
| Priority | `P1` core flow / data loss / security · `P2` important negative & boundary · `P3` cosmetic / rare edge |
| Preconditions | State before step 1 (logged-in role, existing data) |
| Steps | Numbered, one action each, starting with a verb |
| Test Data | Actual values (`john.doe@test.com`, `"A" × 51`) |
| Expected Result | Observable outcome; one TC = one verification goal |
| Remarks | `Blocked by G-xx`, `Based on assumption A-xx`, automation hint |

## Priority distribution sanity check
Typical story: P1 ≈ 30–40 %, P2 ≈ 40–50 %, P3 ≈ 10–20 %. If everything is P1, re-prioritise.

## Do not
- Combine several validations in one TC ("enter invalid email and short password").
- Write steps like "Verify the feature works".
- Add tests for behaviour not in the refined story (raise it as a gap instead).
