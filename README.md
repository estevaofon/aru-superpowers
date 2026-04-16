# aru-superpowers

Engineering discipline skills for [Aru](https://github.com/estevaofon/aru): TDD,
systematic debugging, verification-before-completion, code review, and other
proven workflows. Adapted from the original
[obra/superpowers](https://github.com/obra/superpowers) Claude Code plugin.

## Installation

```bash
aru
# Inside the Aru REPL:
/plugin install github:estevaofon/aru-superpowers
# Or for local development:
/plugin install file:///path/to/aru-superpowers
```

After install, restart Aru. The plugin's skills become available as slash
commands (`/test-driven-development`, `/systematic-debugging`, etc.) and the
`using-superpowers` bootstrap is injected automatically into the main agent's
system prompt.

## What's Included

### Skills (12 total)

The **canonical 7-step workflow** (matches the upstream superpowers):

| Step | Skill | Purpose |
|------|-------|---------|
| 1 | `brainstorming` | **Entry point** — turn an idea into an approved design spec before any code |
| 2 | `using-git-worktrees` | Isolate work on its own branch + clean test baseline |
| 3 | `writing-plans` | Convert an approved spec into a bite-sized task checklist |
| 4 | `subagent-driven-development` | **Preferred executor** — fresh subagent per task, two-stage review |
|   | `executing-plans` | Fallback executor — batched, run in the main session |
| 5 | `requesting-code-review` | Dispatch the `code-reviewer` subagent |
| 6 | `receiving-code-review` | Handle review feedback without sycophancy |
| 7 | `finishing-a-development-branch` | Verify + 4-option close (merge/PR/keep/discard) |

Subroutines invoked **inside** step 4:

| Skill | Purpose |
|-------|---------|
| `test-driven-development` | RED-GREEN-REFACTOR discipline for every task |
| `systematic-debugging` | Root-cause investigation when something fails |
| `verification-before-completion` | Evidence-based completion claims |

Meta / bootstrap:

| Skill | Purpose |
|-------|---------|
| `using-superpowers` | Bootstrap: how to find and invoke other skills (auto-injected) |

### Flow diagram

```
/brainstorming → /using-git-worktrees → /writing-plans
   → /subagent-driven-development (or /executing-plans)
       └─ each task uses: /test-driven-development,
                          /systematic-debugging (on failure),
                          /verification-before-completion
   → /requesting-code-review → /receiving-code-review
   → /finishing-a-development-branch
```

### Agent

- `code-reviewer` — Senior reviewer dispatched via `delegate_task(agent_name="code-reviewer")`.

### Plugin (Bootstrap Hook)

- `plugins/main.py` — Injects the `using-superpowers` skill content into the
  primary agent's system prompt via `chat.system.transform`. Skips subagents
  (`explorer`, `plan`) to save tokens.

## Tool Name Mapping (from Claude Code → Aru)

| Claude Code | Aru |
|-------------|-----|
| `Skill` | `/skill-name` (slash command) |
| `TodoWrite` / `TodoUpdate` | `create_task_list` / `update_task` |
| `Task` (subagent) | `delegate_task` |
| `Read` | `read_file` / `read_files` |
| `Write` | `write_file` / `write_files` |
| `Edit` | `edit_file` / `edit_files` |
| `Glob` | `glob_search` |
| `Grep` | `grep_search` |
| `WebSearch` | `web_search` |
| `WebFetch` | `web_fetch` |
| `Bash` | `bash` |

## License

MIT — matches the upstream obra/superpowers license.
