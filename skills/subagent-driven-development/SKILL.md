---
name: subagent-driven-development
description: Use when executing an implementation plan by dispatching a fresh subagent per task with two-stage review (spec compliance then code quality) between tasks. Chosen by the user at the writing-plans handoff as the subagent-driven option.
argument-hint: "[path-to-plan.md]"
user-invocable: true
allowed-tools: read_file, read_files, bash, delegate_task, create_task_list, update_task, update_plan_step
---

# Subagent-Driven Development

Execute a plan by dispatching a fresh subagent per task (`delegate_task`), with two-stage review after each: spec compliance review first, then code quality review.

**Why subagents:** You delegate tasks to specialized agents with isolated context. By precisely crafting their instructions, you keep them focused. They do NOT inherit your session's context or history — you construct exactly what they need. This also preserves your own context for coordination work.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## Aru-Specific Notes

Aru's concurrency model is different from Claude Code's `Task` tool:

- Aru's `delegate_task` is **sequential** per call. The calling agent blocks until the subagent finishes.
- Multiple `delegate_task` calls **in a single assistant response** run concurrently (asyncio gather). Use this for independent subtasks.
- Each `delegate_task` call creates a **forked RuntimeContext** (isolated task store, permission state, read cache). Subagents cannot see each other's state, and you cannot see theirs until they return.
- Subagents **share the working directory**. If they edit the same files, the last write wins. For true isolation, start inside a git worktree (`/using-git-worktrees`) before dispatching.
- The `code-reviewer` agent shipped with this plugin is a subagent (`mode: subagent`) — dispatch with `delegate_task(task="...", agent_name="code-reviewer", context="...")`.

### One user turn = ALL tasks, not one task

The entire plan is executed in a **single user turn**. Each `delegate_task` call internally produces a tool_call/tool_result pair within that turn; after the result lands, the agentic loop continues to your next assistant message *in the same turn*, where you dispatch the next subagent. Do **NOT** end the turn between tasks. End the turn only when (a) every task in the list is marked completed/failed/skipped, (b) a real blocker needs the user, or (c) the final review workflow concludes.

The numbered "Response 1 / Response 2 / …" labels in the Typical dispatch shape section below refer to **consecutive assistant messages inside the same agentic turn** — not to separate user-agent turns. A handoff between you and the user is not implied.

## When to Use

```
Have implementation plan? ─── no ──> /brainstorming first; then /writing-plans
  │ yes
  ▼
Tasks mostly independent? ─── no ──> tightly coupled → stay in main session; /executing-plans
  │ yes
  ▼
Stay in this session? ─── no ──> /executing-plans (batched, with human checkpoints)
  │ yes
  ▼
/subagent-driven-development   ← you are here
```

**vs. `/executing-plans`:**
- Same session (no context switch)
- Fresh subagent per task (no context pollution across tasks)
- Two-stage review after each task: spec compliance first, then code quality
- Faster iteration (no human-in-the-loop between tasks)

## Entering This Skill (MANDATORY FIRST ACTIONS)

<CRITICAL-GATE>
When entering this skill (after `/writing-plans` or when the user says "implement" / "vamos para implementação" and a plan exists), your FIRST two actions are:

1. `read_file("<plan-path>")` — load the plan content
2. `create_task_list([...])` with **one entry per Task N in the plan** (NOT the /brainstorming checklist)

Any previous checklist from `/brainstorming` or `/writing-plans` is now **STALE** and must be replaced. Do not copy brainstorming items ("Explore project context", "Propose approaches", etc.) into the new list — those phases are done.
</CRITICAL-GATE>

**Concrete example** (if the plan has 4 tasks):

```python
create_task_list([
    "Task 1: <short summary from plan>",
    "Task 2: <short summary from plan>",
    "Task 3: <short summary from plan>",
    "Task 4: <short summary from plan>",
])
```

Per-task sub-tracking (implementer ran / spec review / code-quality review) lives in the subagent's own task_store via `fork_ctx()` — you do NOT need to enumerate those in the controller's checklist.

## The Process

The entire flow below executes in ONE user turn. Each downward arrow is your next assistant message after the previous tool returned — not a hand-back to the user.

```
Read plan file ONCE
  └─> Extract all tasks with full text + context
      └─> create_task_list([task_1, task_2, ...])
          │
          ▼  (per task, in order — same turn, next assistant message)
      Dispatch implementer subagent (./implementer-prompt.md template)
          │
          ├── Subagent asks a question? → Answer, re-dispatch
          │
      Implementer: implements, tests, commits, self-reviews
          │
      Dispatch spec compliance reviewer (./spec-reviewer-prompt.md)
          │
          ├── Reviewer finds gaps? → Re-dispatch implementer with gap list → re-review
          │
      Spec reviewer: ✅ approved
          │
      Dispatch code quality reviewer (./code-quality-reviewer-prompt.md)
          │
          ├── Reviewer finds issues? → Re-dispatch implementer with issues → re-review
          │
      Code quality reviewer: ✅ approved
          │
      update_task(idx, "completed")
          │
          ▼  (next task — STILL the same user turn; do NOT yield)
  After all tasks:
    1. Dispatch FINAL code-reviewer over the whole diff via:
         delegate_task(task="...", agent_name="code-reviewer")
    2. Load requesting-code-review skill for the full workflow:
         invoke_skill(name="requesting-code-review")
    3. After fixes: invoke_skill(name="finishing-a-development-branch")
```

## Task Dependency Assessment

After extracting all tasks from the plan, classify each one **before dispatching**:

- **Sequential**: Task B imports types Task A creates, modifies files Task A wrote, or builds on Task A's output. Must wait for A to finish.
- **Independent**: Tasks touch disjoint files and share no output with siblings. Safe to run in parallel.

### How to dispatch parallel tasks

When tasks are independent, emit ALL their `delegate_task` calls in **one assistant response** — do NOT wait between them. Aru runs concurrent calls via `asyncio.gather`; calls spread across separate responses run sequentially even when the tasks don't depend on each other.

```python
# Tasks 3, 4, 5 touch different modules — dispatch ALL in one response → concurrent:
delegate_task(task="Task 3: Player class", context="Only touch src/player.py. ...")
delegate_task(task="Task 4: Obstacles",   context="Only touch src/obstacles.py. ...")
delegate_task(task="Task 5: UI",          context="Only touch src/ui.py. ...")
# ↑ You receive all three results before continuing. Do NOT split these across turns.
```

Sequential tasks dispatch one per response:

```python
# Task 1 must finish before Task 2 can use its output
delegate_task(task="Task 1: Scaffolding", context="...")
# ← wait for result; only then, in the NEXT response:
delegate_task(task="Task 2: Constants module", context="...")
```

### Safety check before batching

| Question | Answer | Action |
|---|---|---|
| Do any two tasks write the same file? | yes | sequential |
| Does task B read output task A produces? | yes | sequential |
| Both conditions false? | — | safe to batch in one response |

### Typical dispatch shape for a 10-task plan

All dispatches below happen **within the same user turn** — each numbered step is the next assistant message after the previous batch's tool_results have returned. There is no user input between steps.

```
Step 1 (assistant msg): delegate task 1 (scaffolding — everything depends on it)
        ← receive tool_result, continue in the same turn
Step 2 (assistant msg): delegate task 2 (constants — next layer of dependency)
        ← receive tool_result, continue in the same turn
Step 3 (assistant msg): delegate tasks 3 + 4 + 5 + 6 in ONE assistant message (independent modules)
        ← receive all four tool_results, continue in the same turn
Step 4 (assistant msg): review results from tasks 3–6, then delegate task 7 (integration)
...
Final step: when every task is completed/failed and the final code review is done, yield to the user.
```

**Anti-pattern (do not do this):** ending the turn after Step 1 with "Task 1 done. Next: Task 2" or "Se quiser, sigo para a Task 2" — this defeats the entire skill, because the user now has to type "continue" before each task and you've reintroduced the human-in-the-loop overhead this skill exists to eliminate.

### Reviews after a parallel group

After all tasks in a group return, run reviews **sequentially per task** — spec compliance first, then code quality for each. Only mark a task complete when both reviewers approve.

## Setup Before Starting

1. **Worktree** — run `/using-git-worktrees` first unless you've explicitly decided to work on main
2. **Plan file** — produced by `/writing-plans`; extract every task's full text now
3. **TodoWrite equivalent** — seed `create_task_list([...])` with one entry per task
4. **Model tier decision** — see Model Selection below

## Model Selection

Use the least powerful model that can handle each role, to conserve cost and improve throughput.

| Task complexity | Suggested tier |
|-----------------|---------------|
| Touches 1–2 files, complete spec, mechanical | cheap / small model |
| Multi-file integration, pattern matching, debugging | standard model |
| Architecture, design judgment, broad codebase reasoning | most capable model |

For reviewers: spec compliance can use a cheap model; code-quality review should use the standard or capable model.

In Aru, model selection happens at `delegate_task` dispatch via the `agent_name` parameter — custom agents in `.agents/agents/` can pin their own model via frontmatter `model:` field. For generic subagents, the small model is used by default.

## Handling Implementer Status

Implementer subagents should conclude with one of four statuses. Handle each:

- **DONE** — proceed to spec compliance review.
- **DONE_WITH_CONCERNS** — read the concerns. If about correctness or scope, address before review. If observational ("this file is getting large"), note and proceed.
- **NEEDS_CONTEXT** — provide the missing info and re-dispatch.
- **BLOCKED** — assess the blocker:
  1. Context problem → provide context, re-dispatch with same model
  2. Needs more reasoning → re-dispatch with more capable model
  3. Task too large → break into smaller pieces
  4. Plan itself wrong → escalate to the human

**Never** ignore an escalation or force the same model to retry without changes. If the implementer is stuck, something needs to change.

## Prompt Templates

Shipped alongside this SKILL.md:

- `./implementer-prompt.md` — dispatch implementer subagent
- `./spec-reviewer-prompt.md` — dispatch spec compliance reviewer
- `./code-quality-reviewer-prompt.md` — dispatch code quality reviewer

Read the one you need with `read_file` before dispatching so you parameterize correctly.

## Dispatching (Aru syntax)

```python
# Implementer
delegate_task(
    task="<full Task N text from the plan>",
    context=(
        "Plan file: docs/aru/plans/2026-04-16-feature-x.md\n"
        "You are Task N of M. Previous tasks are committed on this branch.\n"
        "Follow /test-driven-development (RED before GREEN, no exceptions).\n"
        "Commit after tests pass; message: 'task N: <short summary>'.\n"
        "Report status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED."
    ),
    # agent_name omitted → generic subagent with full tools
)

# Spec compliance reviewer
delegate_task(
    task="Verify the last commit matches the spec for Task N exactly. Report gaps and extras.",
    context=(
        "Spec source: <paste task N verbatim>\n"
        "Commit to review: <git SHA>\n"
        "Use bash('git show <sha>') to inspect.\n"
    ),
    agent_name="code-reviewer",  # read-only; reviewer can be specialized
)

# Code quality reviewer
delegate_task(
    task="Code quality review of commit <sha>: naming, duplication, test quality, error handling.",
    context="Focus on quality only — spec compliance already approved.",
    agent_name="code-reviewer",
)
```

## Red Flags

**Never:**
- Start implementation on `main`/`master` without explicit user consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementer subagents that write the same files in parallel (last-write-wins conflict) — parallel dispatch is fine when tasks have disjoint files
- Make the subagent read the plan file (provide full text in `context` instead)
- Skip scene-setting context (subagent needs to understand where task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip re-review after a fix
- Let implementer self-review replace actual reviewer dispatches
- **Start code-quality review before spec compliance is ✅** (wrong order)
- Move to the next task while either review has open issues

**If subagent asks questions:** answer clearly and completely; provide additional context; don't rush into implementation.

**If reviewer finds issues:** implementer (re-dispatched) fixes them → reviewer reviews again → repeat until approved. Don't skip the re-review.

**If subagent fails task:** dispatch a fresh fix subagent with specific instructions. Don't patch manually in the controller (context pollution).

## Advantages

**vs. manual execution:**
- Subagents follow TDD naturally (it's in their prompt)
- Fresh context per task (no confusion)
- Isolation-safe (subagents don't interfere with each other's task state)
- Subagent can ask questions before work

**vs. `/executing-plans`:**
- Same session (no handoff)
- Continuous progress (no waiting)
- Review checkpoints automatic

**Efficiency:**
- No plan-file re-reading by subagents (controller provides full text)
- Controller curates exactly the context needed
- Questions surfaced before work, not after

**Quality gates:**
- Self-review catches issues before handoff
- Two-stage review: spec, then quality
- Loops ensure fixes actually work
- Prevents over/under-building

**Cost:**
- More subagent invocations (implementer + 2 reviewers per task)
- Controller does more prep (extracting all tasks upfront)
- Offset: catches issues early (cheaper than debugging later)

## Integration

**Required workflow skills:**
- `/using-git-worktrees` — REQUIRED: set up isolated workspace before starting
- `/writing-plans` — creates the plan this skill executes
- `/requesting-code-review` — template used for reviewer subagents at end of plan
- `/finishing-a-development-branch` — complete development after all tasks

**Subagents should follow:**
- `/test-driven-development` — RED-GREEN-REFACTOR for each task
- `/verification-before-completion` — gate before they report DONE

**Alternative workflow:**
- `/executing-plans` — batched, human-checkpointed execution in the main session
