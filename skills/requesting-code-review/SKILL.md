---
name: requesting-code-review
description: Use when a task or phase is complete and should be reviewed before merging. Dispatches the code-reviewer agent via delegate_task.
argument-hint: "[plan-path-or-commit-range]"
user-invocable: true
allowed-tools: bash, read_file, delegate_task
---

# Requesting Code Review

## Overview

When a task or phase is complete, dispatch the `code-reviewer` subagent to validate the change against the plan and project standards. This skill is a thin orchestrator — it formats the review request and hands off to `delegate_task`.

**Before invoking:** ensure `/verification-before-completion` has been satisfied. Tests must pass locally.

## Procedure

1. **Identify the diff to review.**
   - If on a feature branch: `bash("git log --oneline main..HEAD")` and `bash("git diff main...HEAD --stat")`
   - If reviewing a specific commit range: note `<base>..<head>`

2. **Identify the plan / context document** (if one exists): the `docs/aru/plans/...` file written by `/writing-plans`, an issue description, or the user's request.

3. **Dispatch the reviewer** via `delegate_task`:

   ```python
   delegate_task(
       task=(
           "Review the changes on this branch against the plan. "
           "Report findings in the standard format (Summary, Strengths, "
           "Critical / Important / Suggestions, Plan Deviations, Recommended Actions)."
       ),
       context=(
           "Plan file: docs/aru/plans/2026-04-15-feature-x.md\n"
           "Diff base: main\n"
           "Diff head: HEAD\n"
           "Key files changed: <list from git diff --stat>\n"
       ),
       agent_name="code-reviewer",
   )
   ```

4. **Read the reviewer's report.** Do NOT just accept the summary — scan each issue.

5. **Triage the findings:**
   - **Critical**: must fix before merge. Create a follow-up subtask and fix now.
   - **Important**: should fix. Fix unless there's a concrete reason to defer (document it).
   - **Suggestion**: apply if cheap; otherwise note and move on.
   - **Plan Deviations**: discuss with the user if the plan needs updating.

6. **After fixes**: re-run tests (`/verification-before-completion`), then optionally re-dispatch review if the changes were substantial.

7. **Load the next skill** to handle feedback properly:

   ```python
   invoke_skill(name="receiving-code-review")
   ```

   Do NOT just "apply the feedback" from memory — the `receiving-code-review` skill has specific protocols for verifying claims, pushing back with evidence, and avoiding sycophantic agreement. Load it before responding.

## When NOT to Invoke

- In the middle of a task (wait until a logical unit is complete)
- When only docs / comments changed (review is overhead then)
- When the user has explicitly asked you to skip review

## Output to User

Present the reviewer's findings verbatim, followed by your triage plan:

```markdown
## Reviewer Findings
<copy the reviewer's markdown>

## My Triage
- Critical #1 — will fix now
- Important #2 — will fix now
- Important #3 — deferring because <reason>; tracked as <issue/note>
- Suggestion #4 — skipping

Proceeding with critical + important fixes.
```

## Related

- `/receiving-code-review` — how to handle the reviewer's feedback once received
- `/finishing-a-development-branch` — merge/PR workflow after review sign-off
- `/verification-before-completion` — precondition before any review request
