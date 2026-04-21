---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code. Produces a bite-sized checkbox plan a junior engineer could execute.
argument-hint: "[feature-description-or-path-to-spec]"
user-invocable: true
allowed-tools: read_file, read_files, write_file, grep_search, glob_search, list_directory, create_task_list, update_task
disallowed-tools: enter_plan_mode
---

# Writing Plans

## Overview

Write implementation plans assuming the engineer has zero context for this codebase. Document what files to touch, what tests to write, and the order of operations. Each step should be 2–5 minutes. Favor DRY, YAGNI, TDD, frequent commits.

Assume a skilled but unfamiliar developer. Optimize the plan for someone reading top-to-bottom and executing step-by-step.

**The plan is a roadmap, not the implementation.** The code is written by the engineer during `/executing-plans`, driven by failing tests (TDD). Do NOT pre-write full class bodies, full file contents, or full implementations in the plan. Show the *minimum snippet* the engineer needs to know *what* and *where* — the test defines the *how*.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/aru/plans/YYYY-MM-DD-<feature-name>.md` (or user-preferred location).

## Scope Check

If the spec covers multiple independent subsystems, suggest splitting into separate plans (one per subsystem). Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each is responsible for. Decomposition decisions get locked in here.

- Design units with clear boundaries and well-defined interfaces
- One clear responsibility per file
- Files that change together should live together
- In existing codebases, follow established patterns

## Bite-Sized Task Granularity

Each step is one action (2–5 minutes):

- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Use `/executing-plans` (sequential) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

Use this template per task:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run it; confirm it fails with the expected error**

```bash
pytest tests/exact/path/to/test.py::test_specific_behavior -q
```

- [ ] **Step 3: Implement minimal code to pass**

```python
def function(x):
    return expected
```

- [ ] **Step 4: Run tests; confirm pass + no regressions**

```bash
pytest -q
```

- [ ] **Step 5: Commit**
````

## Snippet Size Rule

**Every code block in a plan must be ≤20 lines.** If it's longer, you are writing the implementation instead of the plan. Break it into smaller targeted edits, or describe the change in prose and let the failing test drive the full shape of the code.

**Good** — shows the signature and the insertion point:

```markdown
- Modify: `entities.py:58` — in `Guard.__init__`, after `self.alive = True`, add:

    ```python
    self.alert = False
    self.alert_target = None
    ```
```

**Bad** — dumps a full class the engineer should derive from tests:

```markdown
- [ ] Step 1: Write the Camera class

    ```python
    class Camera:
        def __init__(self, pos, angle_range, sweep_speed):
            # ...60 more lines of implementation...
    ```
```

In the bad example, the plan has *become* the implementation. That defeats TDD and blows up the output size.

## Anti-Patterns to Avoid

- **Never call `enter_plan_mode`**: that tool stores plans in volatile session state and is blocked by this skill (the frontmatter declares `disallowed-tools: enter_plan_mode`). The plan MUST be a `.md` file written by `write_file` to `docs/aru/plans/YYYY-MM-DD-<feature>.md`. If you catch yourself wanting to call `enter_plan_mode`, re-read the "Execution Handoff" section below.
- **Writing the implementation instead of the plan**: no full class bodies, no full file rewrites, no >20-line code blocks. Show signatures, insertion points, and test assertions. The engineer writes the body during `/executing-plans`.
- **Placeholders**: No `TODO`, `...`, "similar to Task N", "etc". Describe the change concretely (file + line + intent) even when the code snippet itself is small.
- **Cross-task implicit deps**: if Task N depends on Task N-1, state the dependency explicitly.
- **Missing file paths**: every step names the file by absolute path in the repo.
- **Unrooted tests**: every test has a concrete file path and a concrete command to run it.

## Inline Self-Review

After drafting the plan, read it end-to-end and check:

- [ ] No `TODO`, `???`, or placeholders
- [ ] Every code block has a file path
- [ ] Every code block is ≤20 lines (longer ones = you wrote the implementation, not a plan)
- [ ] Every step has a verification command
- [ ] Type/imports are consistent across tasks
- [ ] Spec requirements are ALL covered
- [ ] No duplication across tasks

If any box fails, fix the plan before handing it off.

## Related

- `/test-driven-development` — how to write the failing test
- `/executing-plans` — how to execute the plan you just wrote
- `/verification-before-completion` — how to prove each task done

## Execution Handoff

Write the plan to `docs/aru/plans/YYYY-MM-DD-<feature>.md` with `write_file`, then offer the user a choice of execution path — do NOT pick one yourself.

<CRITICAL-GATE>
After saving the plan, present this exact block to the user and STOP. Do not call `invoke_skill` yet — wait for the user's reply.

> **Plan complete and self-reviewed.** `<one-line self-review summary: spec coverage / placeholders / type consistency>`.
>
> Plan saved to `docs/aru/plans/<filename>.md`.
>
> **Two execution options:**
>
> **1. Subagent-Driven (recommended)** — Fresh subagent per task, two-stage review between tasks, fast iteration.
>
> **2. Inline Execution** — Execute tasks in this session using `/executing-plans`, sequential with checkpoints.
>
> **Which approach?**

Permission clicks ("Yes" on a write dialog) are NOT a choice signal — they authorise file I/O, not an execution path.
</CRITICAL-GATE>

### Interpreting the user's reply

| User says | Invoke |
|-----------|--------|
| "1", "subagent", "subagent-driven", "recommended", "option 1" | `invoke_skill(name="subagent-driven-development", arguments="docs/aru/plans/<your-plan>.md")` |
| "2", "inline", "executing-plans", "in-session", "option 2" | `invoke_skill(name="executing-plans", arguments="docs/aru/plans/<your-plan>.md")` |
| "implement", "go", "vamos para implementação" without picking a number | Re-ask: "Which option — 1 (Subagent-Driven) or 2 (Inline)?" |
| Anything else | Ask for clarification before invoking. |

**CRITICAL:** Use `invoke_skill`. Do NOT execute the plan from memory — the implementation skills have `<CRITICAL-GATE>` "Entering This Skill" sections that mandate reading the plan and rebuilding the task_list from plan tasks. Improvising reuses the stale brainstorming/writing-plans checklist.
