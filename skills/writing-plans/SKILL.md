---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code. Produces a bite-sized checkbox plan a junior engineer could execute.
argument-hint: "[feature-description-or-path-to-spec]"
user-invocable: true
allowed-tools: read_file, read_files, write_file, grep_search, glob_search, list_directory, create_task_list, update_task
---

# Writing Plans

## Overview

Write implementation plans assuming the engineer has zero context for this codebase. Document what files to touch, what tests to write, and the order of operations. Each step should be 2–5 minutes. Favor DRY, YAGNI, TDD, frequent commits.

Assume a skilled but unfamiliar developer. Optimize the plan for someone reading top-to-bottom and executing step-by-step.

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

## Anti-Patterns to Avoid

- **Placeholders**: No `TODO`, `...`, "similar to Task N", "etc". Fill everything in.
- **Cross-task implicit deps**: if Task N depends on Task N-1, state the dependency explicitly.
- **Missing file paths**: every step names the file by absolute path in the repo.
- **Unrooted tests**: every test has a concrete file path and a concrete command to run it.

## Inline Self-Review

After drafting the plan, read it end-to-end and check:

- [ ] No `TODO`, `???`, or placeholders
- [ ] Every code block has a file path
- [ ] Every step has a verification command
- [ ] Type/imports are consistent across tasks
- [ ] Spec requirements are ALL covered
- [ ] No duplication across tasks

If any box fails, fix the plan before handing it off.

## Related

- `/test-driven-development` — how to write the failing test
- `/executing-plans` — how to execute the plan you just wrote
- `/verification-before-completion` — how to prove each task done

## Final Output

Write the plan to `docs/aru/plans/YYYY-MM-DD-<feature>.md` with `write_file` and announce the path to the user.

## Transition to Implementation

When the user approves the plan and signals readiness to implement:

```python
# Preferred (fresh subagent per task, two-stage review):
invoke_skill(name="subagent-driven-development", arguments="docs/aru/plans/<your-plan>.md")

# Fallback (sequential execution in main session):
invoke_skill(name="executing-plans", arguments="docs/aru/plans/<your-plan>.md")
```

**CRITICAL:** Use `invoke_skill`. Do NOT try to execute the plan from memory — the implementation skills have `<CRITICAL-GATE>` "Entering This Skill" sections that mandate reading the plan and rebuilding the task_list from plan tasks. Improvising reuses the stale brainstorming/writing-plans checklist.
