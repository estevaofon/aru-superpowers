---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes. Enforces root-cause investigation before any patch attempt.
user-invocable: true
allowed-tools: read_file, read_files, grep_search, glob_search, bash, list_directory, edit_file, create_task_list, update_task
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next. Seed a checklist with
`create_task_list(["Phase 1: root cause", "Phase 2: pattern analysis", "Phase 3: hypothesis and test", "Phase 4: fix and verify"])` and mark each complete as you go.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Use `read_file` on the relevant file/log and read in full
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably? `bash` the failing command
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - `bash("git log --oneline -20")`, `bash("git diff HEAD~5")`
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN a system has multiple components** (CI → build → signing, API → service → database):

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters the component
     - Log what data exits the component
     - Verify environment / config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify the failing component
   THEN investigate that specific component
   ```

5. **Trace Data Flow**

   **WHEN the error is deep in the call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward-tracing technique.

   **Quick version:**
   - Where does the bad value originate? (`grep_search` for the symbol)
   - What called this with the bad value?
   - Keep tracing up until you find the source
   - Fix at the source, not at the symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples** — `glob_search`/`grep_search` for similar working code in the same codebase.
2. **Compare Against References** — if implementing a known pattern, read the reference implementation COMPLETELY. Don't skim.
3. **Identify Differences** — list every difference, however small. Don't assume "that can't matter."
4. **Understand Dependencies** — what other components, settings, env does this need?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form a Single Hypothesis** — "I think X is the root cause because Y." Write it down.
2. **Test Minimally** — smallest possible change to test the hypothesis. One variable at a time.
3. **Verify Before Continuing** — did it work? Yes → Phase 4. No → NEW hypothesis. Don't pile on fixes.
4. **When You Don't Know** — say so. Ask for help. Research more.

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create a Failing Test Case** — simplest possible reproduction. Automated if possible.
   Use `/test-driven-development` to author it properly.
2. **Implement a Single Fix** — address the root cause. ONE change at a time.
3. **Verify the Fix** — run the test; run the surrounding tests. Use `/verification-before-completion`.
4. **If the Fix Doesn't Work**
   - STOP
   - Count: how many fixes have you tried?
   - < 3: Return to Phase 1, re-analyze with new information
   - **≥ 3: STOP and question the architecture (step 5)**

5. **If 3+ Fixes Failed — Question the Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state / coupling / problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with your human partner before attempting more fixes.** This is not a failed hypothesis — this is a wrong architecture.

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5).

## User Signals You're Doing It Wrong

Watch for these redirections:

- "Is that not happening?" — you assumed without verifying
- "Will it show us...?" — you should have added evidence gathering
- "Stop guessing" — you're proposing fixes without understanding
- "Ultrathink this" — question fundamentals, not just symptoms
- "We're stuck?" (frustrated) — your approach isn't working

When you see these: STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

## When Process Reveals "No Root Cause"

If systematic investigation reveals the issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

Available as files adjacent to this SKILL.md:

- `root-cause-tracing.md` — Trace bugs backward through the call stack to find the original trigger
- `defense-in-depth.md` — Add validation at multiple layers after finding root cause
- `condition-based-waiting.md` — Replace arbitrary timeouts with condition polling

**Related skills:**
- `/test-driven-development` — For creating failing test case (Phase 4, Step 1)
- `/verification-before-completion` — Verify fix worked before claiming success

## Real-World Impact

From debugging sessions:
- Systematic approach: 15–30 minutes to fix
- Random fixes approach: 2–3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: near zero vs common
