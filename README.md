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

### Skills

| Skill | Purpose |
|-------|---------|
| `using-superpowers` | Bootstrap: how to find and invoke other skills |
| `test-driven-development` | RED-GREEN-REFACTOR discipline |
| `verification-before-completion` | Evidence-based completion claims |
| `systematic-debugging` | Root-cause investigation methodology |
| `writing-plans` | Implementation plan authoring |
| `executing-plans` | Sequential plan execution |
| `requesting-code-review` | Dispatch the code-reviewer agent |
| `receiving-code-review` | Handle review feedback constructively |

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
