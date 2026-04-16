---
name: receiving-code-review
description: Use when you have received feedback from the code-reviewer agent (or a human reviewer) and need to handle it without sycophantic agreement or defensive pushback.
user-invocable: true
allowed-tools: read_file, edit_file, bash, grep_search
---

# Receiving Code Review

## Overview

When a reviewer — subagent or human — sends feedback, evaluate it technically, not performatively. Agree when they're right, disagree with evidence when they're wrong, and never respond with "you're absolutely right!" before you've verified.

**Core principle:** Feedback is data. You evaluate it the same way you'd evaluate a test failure.

## The Protocol

For each piece of feedback:

1. **READ** it literally. Don't paraphrase in your head.
2. **UNDERSTAND** what specifically is being claimed. Re-read the code at the cited line.
3. **VERIFY** the claim:
   - Is the reviewer correct? Use `read_file`, `grep_search`, `bash("pytest ...")` to check.
   - Could they have the wrong context? (They might have missed a function elsewhere.)
4. **EVALUATE**
   - Critical / Important / Suggestion — matches your own assessment?
   - Is the recommendation the best fix or just one option?
5. **RESPOND**
   - Correct → apply the fix (via `edit_file`), run tests, confirm
   - Correct but recommendation off → apply a better fix; explain why
   - Incorrect → disagree with evidence, cite file/line
   - Unclear → ask a clarifying question

## Forbidden Responses

| Do not say | Instead |
|-----------|---------|
| "You're absolutely right!" | "Verified — the claim at `file.py:42` is correct. Applying the fix." |
| "Great catch!" | "Confirmed; fixed in commit <hash>." |
| "I'll fix that right away" (before verifying) | Verify first. Then act. |
| "I completely agree" (before verifying) | Neutral acknowledgement only until verified. |
| Defensive pushback ("but I thought...") | Evidence-based disagreement: cite the line. |

## YAGNI Check for Review Suggestions

Before implementing a reviewer's "you should also..." suggestion:

- [ ] Is the suggested feature / guard actually used anywhere?
- [ ] Does adding it require touching code outside the review scope?
- [ ] Does the project's AGENTS.md say to avoid speculative generalization?

If any box is a clear "no" → push back: "Noted, but deferring — not in the current scope and YAGNI applies."

## Disagreeing Constructively

When you disagree with the reviewer:

```markdown
> Reviewer: `foo.py:17` — this function should handle None.

Reviewing: `foo.py:17` is only called from `bar.py:42` and `baz.py:88`,
and both sites guarantee a non-None argument (see `bar.py:38` assertion).
Adding None handling would be dead code. Keeping the current signature.
```

Cite:
- The exact file and line
- The actual constraint / invariant
- Why the reviewer's suggestion is redundant / incorrect in context

## Order of Operations

1. **Blocking (Critical) issues** first — fix, run tests, verify
2. **Simple (Important) fixes** next — batch where safe
3. **Complex fixes** last — they may need a separate task
4. **Suggestions** — apply only if cheap; otherwise skip with a note

## Red Flags

These thoughts mean STOP — you're drifting:

- "Easier to just agree and move on"
- "I'll fix it without verifying"
- "The reviewer is probably wrong but I'll change it anyway"
- "I'll implement that speculative feature because the reviewer asked"
- "You're absolutely right" forming as your opening sentence

## After Responding

Once all feedback is handled:

1. Re-run `bash("pytest -q")` and any other verification commands
2. Summarize to the user: what you applied, what you pushed back on, what you deferred
3. If the review loop is complete and all blocking issues are resolved, load the next skill:

   ```python
   invoke_skill(name="finishing-a-development-branch")
   ```

4. If changes were substantial, instead re-enter the review loop:

   ```python
   invoke_skill(name="requesting-code-review")
   ```

## Related

- `/requesting-code-review` — how the review was obtained
- `/verification-before-completion` — gate on "fix applied" claims
- `/systematic-debugging` — when a reviewer's finding points to a bug you didn't expect
