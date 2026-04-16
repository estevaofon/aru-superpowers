---
name: dispatching-parallel-agents
description: Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies. Dispatches multiple delegate_task calls in one response for concurrent execution.
user-invocable: true
allowed-tools: delegate_task, bash, read_file, grep_search, glob_search, list_directory, create_task_list, update_task
---

# Dispatching Parallel Agents

## Overview

You delegate tasks to specialized agents with isolated context. By precisely crafting their instructions, you keep them focused. They should NEVER inherit your session's context or history — you construct exactly what they need. This also preserves your own context for coordination work.

When you have multiple unrelated problems (different test files, different subsystems, different bugs), investigating them sequentially wastes wall-clock time. Each investigation is independent and can happen in parallel.

**Core principle:** Dispatch one subagent per independent problem domain. Let them work concurrently.

## Aru Concurrency Model

This is different from Claude Code's `Task` tool. **Read this before dispatching.**

- Aru's `delegate_task` is **sequential per-call**. A single `delegate_task(...)` call blocks until the subagent finishes.
- Multiple `delegate_task(...)` calls **in a single assistant response** run **concurrently** via `asyncio.gather`. This is how parallelism works in Aru.
- Each call creates a **forked `RuntimeContext`** — isolated task store, read cache, and permission state. Subagents cannot see each other's state.
- Subagents **share the working directory** (no worktree isolation built-in). If two parallel subagents edit the same file, last-write-wins. For truly isolated parallel work, start inside a git worktree (`/using-git-worktrees`) OR dispatch READ-ONLY investigations that don't edit files.
- Subagents **cannot spawn sub-subagents** (`delegate_task` is excluded from `_SUBAGENT_TOOLS`).

**Safest parallel pattern:** read-only investigations (debugging, code exploration, analysis) where no subagent writes to disk. Then integrate findings yourself and make edits sequentially.

**Writable parallel pattern:** each subagent scoped to a **disjoint set of files**. State this constraint explicitly in each subagent's prompt.

## When to Use

```
Multiple problems or investigations pending?
  └─ Are they independent (no shared state, no fix-one-affects-another)?
       ├── no  → single subagent investigates all; it sees the big picture
       └── yes → Would parallel file writes conflict?
                  ├── yes → sequential delegate_task calls, OR use worktrees
                  └── no  → PARALLEL DISPATCH (all delegate_task in one response)
```

**Use when:**
- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others
- No shared state between investigations
- Or: parallel read-only investigations (analyze 3 modules for the same pattern)

**Don't use when:**
- Failures are related (fix one might fix others) — investigate together first
- You don't yet know what's broken — exploratory debugging first
- Subagents would edit the same files — sequential or worktree-isolated

## The Pattern

### 1. Identify Independent Domains

Group the problems by what's broken. Example:

- `tests/test_auth.py` — failing authentication tests
- `tests/test_batch.py` — failing batch-completion tests
- `tests/test_abort.py` — failing abort-handling tests

Each domain is independent — fixing auth doesn't affect abort tests.

Seed a tracker:

```python
create_task_list([
    "Dispatch subagent: fix tests/test_auth.py",
    "Dispatch subagent: fix tests/test_batch.py",
    "Dispatch subagent: fix tests/test_abort.py",
    "Integrate fixes and run full test suite",
])
```

### 2. Craft Focused Subagent Prompts

Each prompt contains:

- **Specific scope** — one file or subsystem, explicit path
- **Clear goal** — "make these tests pass"
- **Constraints** — "do NOT touch files outside `auth/`"
- **Expected output** — "return a one-paragraph summary of root cause and the list of files you changed"

### 3. Dispatch in ONE Assistant Response

All parallel `delegate_task` calls must go in a **single response**. Aru batches these via `asyncio.gather`. If you dispatch in separate turns, they run sequentially.

```python
# All THREE of these in ONE assistant response:

delegate_task(
    task="Fix the 3 failing tests in tests/test_auth.py",
    context=(
        "Failures (from pytest -v):\n"
        "  - test_login_rejects_empty_password: expected 'Password required', got None\n"
        "  - test_token_refresh_before_expiry: assertion error on token equality\n"
        "  - test_logout_clears_session: session still present after logout\n\n"
        "Constraints:\n"
        "  - ONLY modify files in aru/auth/ and tests/test_auth.py\n"
        "  - Do NOT touch tests/test_batch.py or tests/test_abort.py\n"
        "  - Follow /test-driven-development for any new tests you add\n\n"
        "Use /systematic-debugging to find root cause before patching.\n\n"
        "Report: one-paragraph summary of root cause + list of files changed."
    ),
)

delegate_task(
    task="Fix the 2 failing tests in tests/test_batch.py",
    context=(
        "Failures: ...\n"
        "Constraints: ONLY modify files in aru/batch/ and tests/test_batch.py.\n"
        "Do NOT touch tests/test_auth.py or tests/test_abort.py.\n"
        "Report: root cause + files changed."
    ),
)

delegate_task(
    task="Fix the 1 failing test in tests/test_abort.py",
    context=(
        "Failure: ...\n"
        "Constraints: ONLY modify files in aru/abort/ and tests/test_abort.py.\n"
        "Do NOT touch other test files.\n"
        "Report: root cause + files changed."
    ),
)
```

All three execute concurrently. Your response returns when ALL three complete.

### 4. Review and Integrate

When the subagents return, Aru surfaces all three responses back to you. Then:

1. **Read each summary** — understand root cause and what was changed
2. **Check for file conflicts** — `bash("git status")`, `bash("git diff --stat")`
3. **Run the full test suite** — `bash("pytest -q")` — verify no cross-interference
4. **Spot-check changes** — subagents can make systematic mistakes; `read_file` key touched lines
5. **Commit** — one commit per domain is cleanest; or one combined commit if they're part of the same bugfix sweep

## Subagent Prompt Structure

Good parallel prompts are:

1. **Focused** — one clear problem domain
2. **Self-contained** — all context the subagent needs (paste error output, list failing test names)
3. **Bounded** — explicit "do NOT touch" list to prevent file conflicts
4. **Specific about output** — what format should the summary take?

Example (read-only investigation):

```
Investigate whether the pattern `asyncio.create_task(...)` in aru/runner.py:234
has the same bug as the one we just fixed in aru/tools/delegate.py:156
(forgetting to store a reference, leading to garbage collection of the task).

Scope: read-only. Use read_file, grep_search. Do NOT edit any files.

Report:
- Does the bug apply? (yes / no / similar-but-different)
- Cite the relevant lines
- If similar-but-different, describe the difference
```

## Common Mistakes

| Mistake | Why it fails | Fix |
|---------|-------------|-----|
| "Fix all the tests" | Subagent gets lost, no scope | "Fix tests/test_auth.py failures, specifically tests X, Y, Z" |
| No context (error messages) | Subagent doesn't know where | Paste the failing command output verbatim |
| No constraints | Subagent refactors everything | "Do NOT modify files outside `<dir>`" |
| Vague output request | You don't know what changed | "Return root cause + list of files changed" |
| Dispatched across turns | Runs sequentially | All `delegate_task` calls in ONE assistant response |
| Parallel writes to same files | Last-write-wins races | Disjoint file sets OR use worktrees OR sequential |

## When NOT to Use

- **Related failures** — fixing one might fix others. Investigate together first.
- **Need full system context** — understanding requires seeing everything.
- **Exploratory debugging** — you don't yet know what's broken.
- **Shared state / shared files** — subagents would collide. Fall back to sequential or worktree isolation.

## Example from Practice

**Scenario:** 6 test failures across 3 files after a refactor.

```
tests/test_abort.py     — 3 failures (timing/race conditions)
tests/test_batch.py     — 2 failures (tools not executing)
tests/test_auth.py      — 1 failure (token refresh)
```

**Assessment:** Independent domains. Abort ≠ batch ≠ auth. Each file has different code paths.

**Dispatch (one assistant response, three calls):**

```
delegate_task(task="Fix tests/test_abort.py", context="<scoped>")
delegate_task(task="Fix tests/test_batch.py", context="<scoped>")
delegate_task(task="Fix tests/test_auth.py", context="<scoped>")
```

**Results (all concurrent):**
- Subagent A: Replaced `time.sleep()` with event-based waiting
- Subagent B: Fixed wrong dict key in batch-completion event
- Subagent C: Added missing await on async token refresh

**Integration:** `bash("git status")` → no conflicts. `bash("pytest -q")` → all 6 now green.

**Wall-clock gain:** ~3x vs sequential dispatch.

## Key Benefits

1. **Parallelization** — multiple investigations truly concurrent (asyncio.gather)
2. **Focus** — each subagent has narrow scope, less context to track
3. **Independence** — separated task stores prevent state pollution
4. **Speed** — 3 problems solved in the wall-clock time of 1

## Verification (after subagents return)

```python
create_task_list([
    "Read each subagent's summary",
    "bash('git status') — check for unexpected edits",
    "bash('git diff --stat') — confirm disjoint file sets",
    "bash('pytest -q') — verify all domains green together",
    "Spot-check: read_file on a random changed file per subagent",
])
```

Only mark the overall task complete once the full suite passes AND you've read each summary.

## Integration

- `/systematic-debugging` — each subagent should follow this inside its scope
- `/verification-before-completion` — verify BEFORE claiming "all subagents succeeded"
- `/using-git-worktrees` — when parallel subagents must write to overlapping paths
- `/subagent-driven-development` — different pattern: sequential tasks with two-stage review, for executing a plan (not for independent investigations)
