---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace, or before executing implementation plans. Creates isolated git worktrees with smart directory selection and safety verification.
argument-hint: "[branch-name]"
user-invocable: true
allowed-tools: bash, read_file, list_directory, grep_search
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

**Announce at start:** "I'm using `/using-git-worktrees` to set up an isolated workspace."

> **Aru note:** Aru does not have built-in worktree isolation (Claude Code's `Agent(isolation: "worktree")` has no equivalent). All worktree management in Aru is explicit `bash` + `git worktree` commands. Subagents dispatched via `delegate_task` share the parent's CWD — switch into the worktree yourself before delegating if you want the subagent to operate there.

## Directory Selection Process

Follow this priority order:

### 1. Check Existing Directories

```bash
bash("ls -d .worktrees 2>/dev/null; ls -d worktrees 2>/dev/null")
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

### 2. Check AGENTS.md / CLAUDE.md

```bash
bash("grep -i 'worktree.*director' AGENTS.md CLAUDE.md 2>/dev/null")
```

**If a preference is specified:** Use it without asking.

### 3. Ask User

If no directory exists and no config preference:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden, recommended)
2. worktrees/ (project-local, visible)
3. ~/.aru/worktrees/<project-name>/ (global location, outside the repo)

Which would you prefer?
```

## Safety Verification

### For Project-Local Directories (`.worktrees` or `worktrees`)

**MUST verify the directory is gitignored before creating the worktree:**

```bash
bash("git check-ignore -q .worktrees 2>/dev/null && echo IGNORED || echo NOT_IGNORED")
```

**If NOT ignored:**

1. Append the directory name to `.gitignore` (use `edit_file` or `bash("echo .worktrees/ >> .gitignore")`)
2. Commit: `bash("git add .gitignore && git commit -m 'chore: ignore worktrees directory'")`
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to the main repository.

### For Global Directory (`~/.aru/worktrees`)

No `.gitignore` verification needed — outside the project entirely.

## Creation Steps

### 1. Detect Project Name

```bash
bash("basename \"$(git rev-parse --show-toplevel)\"")
```

### 2. Create Worktree

```bash
# Project-local example:
bash("git worktree add .worktrees/<branch-name> -b <branch-name>")

# Global example:
bash("git worktree add ~/.aru/worktrees/<project>/<branch-name> -b <branch-name>")
```

**IMPORTANT:** After creating the worktree, the Aru process is still in the original CWD. You need to `cd` into the worktree for subsequent operations:

```bash
bash("cd .worktrees/<branch-name> && git status")
```

Because Aru's `bash` tool runs each command in a fresh shell, you have two options:

1. Chain commands in a single `bash` call with `cd`:
   ```bash
   bash("cd .worktrees/auth && pytest -q")
   ```
2. Restart Aru from the worktree directory for a fully isolated session.

### 3. Run Project Setup

Auto-detect and run appropriate setup **inside the worktree**:

```bash
# Python (pip)
bash("cd .worktrees/<branch> && python -m pip install -r requirements.txt")

# Python (uv or poetry, if present)
bash("cd .worktrees/<branch> && uv sync") # or: poetry install

# Node.js
bash("cd .worktrees/<branch> && npm install")

# Rust
bash("cd .worktrees/<branch> && cargo build")

# Go
bash("cd .worktrees/<branch> && go mod download")
```

Only run what applies; check for the respective manifest files first with `list_directory` or `glob_search`.

### 4. Verify Clean Baseline

Run the project's test command inside the worktree to ensure it starts clean:

```bash
bash("cd .worktrees/<branch> && pytest -q")      # or: npm test, cargo test, go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate. Do not start new work on top of a broken baseline.

**If tests pass:** Report ready.

### 5. Report Location

Format the report as:

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check AGENTS.md → ask user |
| Directory not ignored | Add to `.gitignore` + commit |
| Tests fail during baseline | Report failures + ask |
| No manifest found | Skip dependency install |

## Common Mistakes

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute `git status`
- **Fix:** Always `git check-ignore` before creating project-local worktree

### Assuming directory location

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: existing > AGENTS.md > ask

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Forgetting the CWD caveat

- **Problem:** Subsequent `bash`/`pytest`/`edit_file` calls operate on the main tree, not the worktree
- **Fix:** Always `cd <worktree-path> && <command>` in `bash`, or restart Aru from inside the worktree

## Example Workflow

```
> I'm using /using-git-worktrees to set up an isolated workspace for the auth feature.

[bash("ls -d .worktrees 2>/dev/null") → exists]
[bash("git check-ignore -q .worktrees && echo IGNORED") → IGNORED]
[bash("git worktree add .worktrees/auth -b feature/auth")]
[bash("cd .worktrees/auth && python -m pip install -r requirements.txt")]
[bash("cd .worktrees/auth && pytest -q") → 47 passed]

Worktree ready at /Users/you/myproject/.worktrees/auth
Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## Red Flags

**Never:**
- Create a worktree without verifying it's ignored (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Skip the AGENTS.md / config check

**Always:**
- Follow directory priority: existing > config > ask
- Verify directory is ignored for project-local worktrees
- Auto-detect and run project setup
- Verify a clean test baseline
- Remember Aru's `bash` is stateless — `cd` inside each invocation

## Integration

**Called by:**
- `/brainstorming` (after design approval, before `/writing-plans`) — REQUIRED for non-trivial work
- `/subagent-driven-development` — REQUIRED before executing any tasks
- `/executing-plans` — REQUIRED before executing any tasks (unless working on the main tree intentionally)
- Any skill needing an isolated workspace

**Pairs with:**
- `/finishing-a-development-branch` — REQUIRED for cleanup after work complete
