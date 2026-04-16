# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent via `delegate_task`.

```python
delegate_task(
    task="Implement Task N: <task name>",
    context=(
        # --- Task description (paste full text, don't make subagent read plan) ---
        "## Task Description\n"
        "<FULL TEXT of Task N from the plan>\n\n"

        # --- Scene-setting ---
        "## Context\n"
        "<Where this fits; dependencies; architectural context; previous tasks "
        "already committed on this branch>\n\n"

        # --- Before starting ---
        "## Before You Begin\n"
        "If you have questions about requirements, approach, dependencies, or\n"
        "anything unclear, ASK THEM NOW before starting work. Don't guess.\n\n"

        # --- Job ---
        "## Your Job\n"
        "1. Implement exactly what the task specifies\n"
        "2. Follow /test-driven-development (RED before GREEN, no exceptions)\n"
        "3. Verify implementation works: bash('pytest -q') or project equivalent\n"
        "4. Commit: git add ... && git commit -m 'task N: <summary>'\n"
        "5. Self-review (see checklist below)\n"
        "6. Report back\n\n"

        # --- Work directory ---
        "Work from: <absolute path to worktree or project root>\n\n"

        # --- Code organization ---
        "## Code Organization\n"
        "- Follow the file structure defined in the plan\n"
        "- Each file should have one clear responsibility\n"
        "- If a file is growing beyond the plan's intent, STOP and report\n"
        "  as DONE_WITH_CONCERNS. Don't split files on your own.\n"
        "- Follow established patterns; don't restructure things outside your task.\n\n"

        # --- Escalation ---
        "## When You're in Over Your Head\n"
        "It is ALWAYS OK to stop and say 'this is too hard for me.'\n"
        "Bad work is worse than no work. You will NOT be penalized for escalating.\n\n"
        "**STOP and escalate when:**\n"
        "- The task requires architectural decisions with multiple valid approaches\n"
        "- You need to understand code beyond what was provided\n"
        "- You feel uncertain about whether your approach is correct\n"
        "- The task involves restructuring existing code the plan didn't anticipate\n"
        "- You've been reading file after file without progress\n\n"
        "**How to escalate:** Report back with status BLOCKED or NEEDS_CONTEXT.\n"
        "Describe what you're stuck on, what you've tried, and what help you need.\n\n"

        # --- Self-review ---
        "## Before Reporting Back: Self-Review\n"
        "Review your work with fresh eyes:\n\n"
        "**Completeness:** Fully implemented? Edge cases? Missed requirements?\n"
        "**Quality:** Clear names? Clean and maintainable? Your best work?\n"
        "**Discipline:** YAGNI respected? Followed existing patterns?\n"
        "**Testing:** Tests verify real behavior (not mocks)? TDD followed? Comprehensive?\n\n"
        "If you find issues during self-review, fix them NOW before reporting.\n\n"

        # --- Report format ---
        "## Report Format\n"
        "Conclude your response with:\n\n"
        "Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT\n"
        "Summary: <what you implemented or attempted>\n"
        "Tests: <what you tested and the result, e.g. '12 passed'>\n"
        "Files: <list of files changed>\n"
        "Self-review findings: <any issues found and fixed>\n"
        "Concerns: <doubts or observations>\n\n"
        "- DONE_WITH_CONCERNS: completed, but you have doubts\n"
        "- BLOCKED: cannot complete the task\n"
        "- NEEDS_CONTEXT: need info not provided\n"
        "Never silently produce work you're unsure about.\n"
    ),
    # agent_name omitted → generic subagent (small model, _SUBAGENT_TOOLS set)
    # OR specify a custom agent from .agents/agents/ if you have one
)
```

## Aru-specific reminders

- The subagent runs in a **forked RuntimeContext** — it has its own task store, fresh read cache, and independent permissions state.
- The subagent **shares the CWD** with the controller. If parallel subagents might conflict, start from a git worktree (`/using-git-worktrees`).
- `delegate_task` returns when the subagent finishes. The calling agent blocks, so you cannot interact during execution.
- Subagent tool set excludes `delegate_task` itself — they cannot spawn sub-subagents. If you need deeper delegation, restructure the plan.
