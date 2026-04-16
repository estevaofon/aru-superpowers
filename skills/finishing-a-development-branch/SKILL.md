---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work. Guides completion by presenting structured options for merge, PR, keep, or discard.
user-invocable: true
allowed-tools: bash, read_file, grep_search
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling the chosen workflow.

**Core principle:** Verify tests → present options → execute choice → clean up.

**Announce at start:** "I'm using `/finishing-a-development-branch` to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass.** This is `/verification-before-completion` applied at the branch level.

```bash
# Project test command — use whatever applies
bash("pytest -q")               # Python
bash("npm test --silent")       # Node.js
bash("cargo test --quiet")      # Rust
bash("go test ./...")           # Go
```

**If tests fail:**

```
Tests failing (<N> failures). Must fix before completing:

<show failures>

Cannot proceed with merge/PR until tests pass.
```

Stop. Do not proceed to Step 2. Invoke `/systematic-debugging` if needed.

**If tests pass:** continue to Step 2.

### Step 2: Determine Base Branch

```bash
bash("git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null")
bash("git branch --show-current")
```

Or ask the user: "This branch split from `main` — is that correct?"

Also useful:

```bash
bash("git log --oneline main..HEAD")   # commits on this branch
bash("git diff --stat main...HEAD")    # files changed
```

### Step 3: Present Options

Present **exactly these 4 options, concisely:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add extra explanation** — keep the menu tight.

### Step 4: Execute Choice

#### Option 1: Merge Locally

```bash
bash("git checkout <base-branch>")
bash("git pull --ff-only")
bash("git merge <feature-branch>")
bash("<project test command>")   # verify tests on merged result
# If tests pass:
bash("git branch -d <feature-branch>")
```

If tests fail on the merged result, roll back: `bash("git reset --hard HEAD~1")` and report.

Then proceed to Step 5 (cleanup worktree).

#### Option 2: Push and Create PR

```bash
bash("git push -u origin <feature-branch>")
```

Then create the PR with the user's standard template. For this user, the template has 3 sections — Summary, Components, Test Plan with checkboxes in the body:

```bash
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
- <bullet 1>
- <bullet 2>

## Components
- `<path/to/file>` — <what changed>

## Test Plan
- [x] <implemented/verified item>
- [ ] <pending verification>
EOF
)"
```

**IMPORTANT (Aru bash tool gotcha):** On Windows / bash tool, heredocs can fail — if `gh pr create --body "$(cat <<'EOF'...`  misbehaves, write the body to a temp file first and pass `--body-file`:

```bash
bash("cat > /tmp/pr-body.md <<'EOF'
## Summary
- ...
EOF
gh pr create --title '<title>' --body-file /tmp/pr-body.md")
```

Then proceed to Step 5.

#### Option 3: Keep As-Is

Report: "Keeping branch `<name>`. Worktree preserved at `<path>`."

**Do NOT cleanup worktree.** Skip Step 5.

#### Option 4: Discard

**Confirm first — require the user to type `discard` exactly:**

```
This will permanently delete:
- Branch <name>
- All commits: <paste output of git log --oneline base..HEAD>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation. If the user types anything else, abort.

If confirmed:

```bash
bash("git checkout <base-branch>")
bash("git branch -D <feature-branch>")
```

Then proceed to Step 5.

### Step 5: Cleanup Worktree

**For Options 1, 2, 4:**

Check if in a worktree:

```bash
bash("git worktree list")
```

If one of the listed worktrees matches the feature branch, remove it:

```bash
bash("git worktree remove <worktree-path>")
```

**For Option 3:** keep the worktree. Skip cleanup.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | ✓ | — | — | ✓ |
| 2. Create PR | — | ✓ | ✓ | — |
| 3. Keep as-is | — | — | ✓ | — |
| 4. Discard | — | — | — | ✓ (force) |

## Common Mistakes

**Skipping test verification**
- Problem: merge broken code, create failing PR
- Fix: always verify tests before offering options

**Open-ended questions**
- Problem: "What should I do next?" → ambiguous
- Fix: present exactly 4 structured options

**Automatic worktree cleanup**
- Problem: remove worktree when user might need it (Option 2 or 3)
- Fix: only cleanup for Options 1 and 4

**No confirmation for discard**
- Problem: accidentally delete work
- Fix: require typed `discard` confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on the merged result
- Delete work without confirmation
- Force-push without explicit user request

**Always:**
- Verify tests before offering options
- Present exactly 4 options
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 and 4 only

## Integration

**Called by:**
- `/subagent-driven-development` (final step) — after all tasks complete
- `/executing-plans` (final step) — after all tasks complete

**Pairs with:**
- `/using-git-worktrees` — cleans up the worktree created by that skill
- `/requesting-code-review` — should have passed before finishing
- `/verification-before-completion` — the full-suite test run here is the final application of that skill
