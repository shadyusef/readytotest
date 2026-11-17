# Story Review Checklist (Phase 1)

Go through every section. Each failed item becomes a gap row. Quote the exact words from the story.

## 1. Structure
- [ ] Has a role, a goal and a benefit ("As a … I want … so that …").
- [ ] The role is a real user type, not "the user" / "the system" when several roles exist.
- [ ] The benefit states business value, not a restatement of the goal.
- [ ] Has acceptance criteria. No AC at all → **Blocker**.

## 2. INVEST
| Letter | Fails when |
|---|---|
| **I**ndependent | Depends on another unfinished story without saying so |
| **N**egotiable | Dictates implementation (e.g. "use a dropdown with Redux") instead of need |
| **V**aluable | No user or business value visible |
| **E**stimable | Too vague to size (unknown scope, unknown integrations) |
| **S**mall | More than one feature / more than ~8 ACs / "and" joins two goals → suggest a split |
| **T**estable | Any AC without an observable outcome |

## 3. Acceptance criteria quality
- [ ] Each AC describes **one** behaviour (split ACs joined by "and"/"or").
- [ ] Each AC has a precondition, a trigger and an observable result.
- [ ] No contradictions between ACs, or between ACs and the story text → **Blocker**.
- [ ] Happy path **and** failure path covered.

## 4. Ambiguous words (flag every occurrence)
fast, quickly, easy, user-friendly, intuitive, simple, appropriate, relevant, properly, correctly,
efficient, flexible, robust, secure (unspecified), etc., and/or, some, many, few, usually, normally,
as needed, if possible, should (when it means "must"?), TBD, similar to, support (what exactly?).
→ Ask for a measurable definition (number, list, rule).

## 5. Data & validation
For each input field / parameter:
- [ ] Mandatory or optional?
- [ ] Type and format (email, phone, date format, currency, decimals)?
- [ ] Min / max length or value?
- [ ] Allowed characters / allowed values list?
- [ ] Uniqueness (duplicates allowed?) and case sensitivity?
- [ ] Default value?
- [ ] Trimming of spaces, leading zeros?

## 6. Business rules
- [ ] Every calculation has a formula and rounding rule.
- [ ] Every condition has all branches (if X then Y — and if not X?).
- [ ] Limits, quotas, time windows, time zones defined.
- [ ] Status / workflow: all states and allowed transitions listed.

## 7. Roles & permissions
- [ ] Who can see / create / edit / delete?
- [ ] What happens when an unauthorised role tries?
- [ ] Data visibility rules (own records vs all records).

## 8. Error handling & messages
- [ ] Exact error message text (or a reference to a message catalogue).
- [ ] Where the message appears, and whether entered data is kept.
- [ ] Behaviour when an external system / API fails or times out.
- [ ] Retry, rollback, partial save?

## 9. UI / UX states (if UI is involved)
- [ ] Empty state, loading state, error state, success confirmation.
- [ ] Pagination / sorting / filtering defaults.
- [ ] Responsive / supported browsers / devices.
- [ ] Design or mock-up referenced?

## 10. Non-functional
- [ ] Performance target (e.g. response < 2 s at N users).
- [ ] Security: authentication, sensitive data masking, audit log.
- [ ] Accessibility level (e.g. WCAG 2.1 AA).
- [ ] Localisation / languages / RTL.
- [ ] Notifications (email, SMS, push): trigger, recipient, content.

## 11. Dependencies & scope
- [ ] Integrations / APIs named, with their contract.
- [ ] Migration or existing-data impact.
- [ ] Explicit out-of-scope list.
- [ ] Analytics / logging requirements.

Only raise items that apply to this story — e.g. skip UI states for a pure API story — but say which sections were skipped and why.
