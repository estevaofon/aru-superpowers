---
name: executing-plans
description: Use when implementing an existing plan file in a single session, step by step. Sequential fallback when subagent dispatch isn't in play.
argument-hint: "[path-to-plan.md]"
user-invocable: true
allowed-tools: read_file, read_files, write_file, edit_file, bash, grep_search, glob_search, list_directory, create_task_list, update_task, update_plan_step
---

# Executing Plans

## Overview

Run an implementation plan task-by-task in the current session. Each step checked off only after verification (`/verification-before-completion`). TDD enforced (`/test-driven-development`). After the final task, finalize with `/requesting-code-review` and `/finishing-a-development-branch`.

**Announce at start:** "I'm using `/executing-plans` to implement `<plan-path>`."

## Preconditions

1. A plan file exists (written by `/writing-plans`) with tasks as `### Task N` and steps as `- [ ] **Step M**`.
2. You have a clean working tree, or an intentionally dirty one for this work.
3. Tests currently pass (or the failing set is known).

## Entering This Skill (MANDATORY FIRST ACTIONS)

<CRITICAL-GATE>
When the user asks you to implement / "vamos para implementação" / equivalent, and a plan file exists, your FIRST two actions are:

1. `read_file("<plan-path>")` — load the plan content
2. `create_task_list([...])` with **one entry per Task N in the plan** (NOT the /brainstorming checklist, NOT the /writing-plans checklist, NOT this skill's "Loop" sub-steps)

Any previous checklist from `/brainstorming` or `/writing-plans` is now **STALE**. The new `create_task_list` call REPLACES it. Do not copy the brainstorming items ("Explore project context", "Ask clarifying questions", "Propose approaches", etc.) into the new list — those phases are already complete.
</CRITICAL-GATE>

**Concrete example** (if the plan has 4 tasks):

```python
create_task_list([
    "Task 1: <short description from plan>",
    "Task 2: <short description from plan>",
    "Task 3: <short description from plan>",
    "Task 4: <short description from plan>",
])
```

If the plan has 16 steps across 4 tasks, the checklist has **4 items** (one per Task), not 16. Sub-steps are tracked inside each task as you execute, not in the top-level checklist.

## Loop

For each task in order:

1. **Read the task and all its steps** with `read_file`. Understand all of them before touching code.
2. **Mark this task `in_progress`** via `update_task(index=N, status="in_progress")`. Do NOT call `create_task_list` again — the list was seeded during Entering This Skill.
3. **RED step** — write the failing test. `bash("pytest ... -q")` and confirm it fails with the expected error.
4. **GREEN step** — write minimal code. `bash("pytest ... -q")` until the failing test passes and no others break.
5. **REFACTOR step** — only after green. Don't add behavior.
6. **COMMIT step** — once all steps for the task pass. Use the project's commit conventions.
7. **Update plan file** — `edit_file` to flip `- [ ]` to `- [x]`. You may also call `update_plan_step(index, "completed")` if the plan is tracked in session state.

## Verification Gates

Between tasks, verify the cumulative state:

- `bash("pytest -q")` passes
- `bash("git status")` shows only intended changes
- `bash("git log --oneline -5")` shows clean task boundaries

If any gate fails, STOP and invoke `/systematic-debugging`. Do NOT continue to the next task.

## When a Step Fails

| Situation | Response |
|-----------|----------|
| Test won't fail (RED skipped) | Delete the test, rewrite it targeting the real gap |
| Test won't pass after implementation | Invoke `/systematic-debugging`; don't pile fixes |
| Unrelated tests broke | Stop. Fix regression before resuming plan |
| Plan step is wrong/ambiguous | Edit the plan file first; keep plan and code in sync |

## Red Flags — STOP

- Skipping the RED verification
- Committing without running tests
- Checking off a step without running its verification command
- Jumping ahead to a later task because "I'm already here"
- Piling multiple step fixes into a single commit
- Trusting "looks right" over `bash("pytest")` output

## Closing the Plan

After the last task:

1. Run the full test suite: `bash("pytest -q")`
2. Run any linting / type checks the project uses (`bash("ruff check")`, `bash("mypy")`, etc.)
3. `git log` to confirm commit history matches the plan's tasks
4. Invoke `/requesting-code-review` to dispatch the code-reviewer subagent
5. After review resolution, invoke `/finishing-a-development-branch`

## Related

- `/writing-plans` — how the plan was produced
- `/test-driven-development` — enforcement for every Task's RED-GREEN-REFACTOR
- `/systematic-debugging` — when a step fails
- `/verification-before-completion` — per-step verification gate
- `/requesting-code-review` — end-of-plan review
- `/finishing-a-development-branch` — merge/PR workflow
