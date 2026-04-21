---
name: using-superpowers
description: Bootstrap governing how to discover and invoke other skills. Always consult before responding or acting, even for clarifying questions.
user-invocable: false
---

<SUBAGENT-STOP>
If you were dispatched as a subagent via `delegate_task` to execute a specific task, skip this skill. Focus on your assigned task.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST consult that skill by running the corresponding slash command or by having the user invoke it.

If a skill applies to your task, you DO NOT HAVE A CHOICE. You must follow it.

This is not negotiable. This is not optional. You cannot rationalize your way out of it.
</EXTREMELY-IMPORTANT>

## Instruction Priority

Superpowers skills override default system behavior, but **user instructions always win**:

1. **User's explicit instructions** (AGENTS.md, CLAUDE.md, direct requests) — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default agent instructions** — lowest priority

If AGENTS.md says "don't use TDD" and a skill says "always use TDD," follow AGENTS.md. The user is in control.

## How to Access Skills

In Aru, skills are slash commands. When the user types `/test-driven-development`, the skill's content is rendered as the agent's next prompt. You can also suggest skills in your responses (e.g., "I'll follow `/systematic-debugging` for this bug"). Never read SKILL.md files with `read_file` — they're already loaded when invoked.

## Tool Mapping (Aru tools)

This plugin was ported from a Claude Code original. The skills use Aru tool names:

| Aru Tool | Purpose |
|----------|---------|
| `read_file` / `read_files` | Read file contents (single or batch) |
| `write_file` / `write_files` | Create or overwrite files |
| `edit_file` / `edit_files` | Targeted edits via old/new string replacement |
| `glob_search` | Find files by glob pattern |
| `grep_search` | Search content (ripgrep) |
| `list_directory` | List directory entries |
| `bash` | Run shell commands |
| `web_search` / `web_fetch` | Web queries and page fetching |
| `delegate_task` | Spawn a subagent (fresh isolated context) |
| `create_task_list` / `update_task` | Track subtasks in a checklist |
| `enter_plan_mode` / `exit_plan_mode` | Toggle plan-only mode (no mutating tools) |
| `update_plan_step` | Progress a multi-step plan |

## The Rule

**Consult relevant skills BEFORE any response or action.** Even a 1% chance a skill applies means invoke it. If an invoked skill turns out not to fit the situation, you don't need to follow it.

```
User message received
  └─> About to plan / scaffold / write code for a new feature or change?
        ├── yes → Is there an approved design for this work?
        │         ├── no  → /brainstorming (MANDATORY entry point)
        │         └── yes → continue
        └── no  → Might any other skill apply?
                  ├── yes (even 1%) → Run the skill → Announce "Following /<skill> to <purpose>"
                  │                   └── Has a checklist? → Mirror via `create_task_list`
                  │                                       → Follow the skill exactly
                  └── definitely not → Respond directly
```

## The Canonical Workflow (7 steps)

Every non-trivial change flows through these skills, in this order. This matches the superpowers reference workflow exactly:

```
1. /brainstorming               ← entry point for ANY creative work
      ↓ produces a spec doc in docs/aru/specs/
2. /using-git-worktrees         ← isolate work on its own branch + worktree
      ↓ clean baseline, tests passing
3. /writing-plans               ← convert spec into bite-sized task checklist
      ↓ produces a plan doc in docs/aru/plans/
4. /writing-plans asks the user to pick ONE:
   /subagent-driven-development (fresh subagent per task, two-stage review)
      — OR —
   /executing-plans             (sequential, in main session, checkpointed)
      ↓ per task, internally uses:
         /test-driven-development    (RED → GREEN → REFACTOR)
         /systematic-debugging       (when something fails)
         /verification-before-completion (gate before marking a step done)
5. /requesting-code-review      ← dispatches code-reviewer subagent
      ↓ reviewer findings
6. /receiving-code-review       ← handle feedback without sycophancy
      ↓ all blocking issues resolved
7. /finishing-a-development-branch  ← verify + present 4 options (merge/PR/keep/discard)
```

**Meta skills (not in the linear flow):**
- `/dispatching-parallel-agents` — concurrent subagents for independent investigation tasks (e.g. 3 subagents analyzing 3 separate problem areas in one response)
- `/writing-skills` — when you need to author a new skill

Skipping the entry point (`/brainstorming`) is the #1 reason agents build the wrong thing. Even for a "tiny" change, a 30-second design discussion prevents 30 minutes of rework.

## Transitioning Between Skills (CRITICAL)

<CRITICAL-GATE>
A skill is **completed** once its terminal state is reached (spec written and approved for brainstorming; plan file written for writing-plans; all plan tasks merged for executing-plans; etc.). Completed skills are NOT re-invoked in the same session.

When the user gives a signal advancing to the next phase — "vamos para implementação", "implement", "go ahead", "próximo passo", "let's code" — and earlier skills are already completed, you MOVE FORWARD in the canonical workflow. You do NOT restart from step 1.
</CRITICAL-GATE>

### Transition rules

Use the `invoke_skill` tool to load the next skill. Do NOT wait for the user to re-type the slash command.

| Just completed | User signal | How to transition |
|----------------|-------------|-------------------|
| `/brainstorming` (spec approved) | "let's plan" / "write the plan" | `invoke_skill(name="writing-plans", arguments="<spec-path>")` |
| `/writing-plans` (plan written) | "let's implement" / "vamos para implementação" / "go" | `/writing-plans` itself asks the user to pick 1 (Subagent-Driven) or 2 (Inline/Executing-plans) before invoking. Do NOT transition silently. |
| `/executing-plans` or `/subagent-driven-development` (all tasks green) | "review it" / "check the code" | `invoke_skill(name="requesting-code-review")` |
| `/requesting-code-review` (findings returned) | any acknowledgement | `invoke_skill(name="receiving-code-review")` |
| `/receiving-code-review` (blockers resolved) | "merge" / "ship it" / "finish" | `invoke_skill(name="finishing-a-development-branch")` |

### Why `invoke_skill` and not memory

The skills' bodies are NOT in your context until loaded. They contain `<CRITICAL-GATE>` sections, checklist templates, and red-flag tables that you have not memorized — and WILL NOT correctly reproduce from memory. When you "just do the next phase" without calling `invoke_skill`, you reliably:

- Recreate the previous skill's checklist instead of the new skill's entering actions
- Skip gates the new skill enforces (e.g. Step 4 section walk, TDD RED verification)
- Drift from the skill's explicit wording on red flags

The `invoke_skill` tool call returns the target skill's full body as a tool_result in your next turn. That next turn THEN executes the skill correctly.

### Checklist hygiene on transition

When you enter a new skill, **any previous skill's task_list is STALE**. The new skill's own "Entering This Skill" section tells you what the new checklist should contain. Common pitfall:

- ❌ User says "vamos para implementação" → agent recreates the `/brainstorming` 8-item checklist (Explore project context, Ask clarifying questions, etc.)
- ✅ User says "vamos para implementação" → agent reads the plan file, calls `create_task_list` with **one entry per Task in the plan**, then enters the per-task loop

If you find yourself about to call `create_task_list(["Explore project context", "Ask clarifying questions", "Propose approaches", ...])` when brainstorming is already done: STOP. That is the previous skill's checklist. Read the NEXT skill's "Entering This Skill" section first.

### "I forgot where we are" recovery

If you genuinely lost track of where in the workflow you are:

1. Check the conversation for produced artifacts:
   - `bash("ls docs/aru/specs/")` — if files exist, brainstorming is done for something
   - `bash("ls docs/aru/plans/")` — if files exist, writing-plans is done for something
   - `bash("git log --oneline main..HEAD")` — shows what has been implemented
2. Match against the table above to find the next step.
3. Do NOT default to `/brainstorming` when artifacts from later phases already exist.

Skipping step 2 (`/using-git-worktrees`) is the #1 reason "experiments" pollute main. Always isolate before writing code.

Skipping step 7 (`/finishing-a-development-branch`) leaves orphaned worktrees, un-merged branches, and uncommitted work the user forgets about.

## Red Flags

These thoughts mean STOP — you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Re-read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Skill Priority

When multiple skills could apply:

1. **Process skills first** (`/brainstorming`, `/systematic-debugging`) — determine HOW to approach the task
2. **Implementation skills second** (`/test-driven-development`, `/executing-plans`) — guide execution

"Let's build X" → brainstorming first, then implementation skills.
"Fix this bug" → debugging first, then domain-specific skills.

## Skill Types

- **Rigid** (TDD, debugging, verification): Follow exactly. Don't adapt away discipline.
- **Flexible** (patterns, review): Adapt principles to context.

The skill itself tells you which.

## User Instructions

Instructions say WHAT, not HOW. "Add X" or "Fix Y" does not mean skip workflows.
