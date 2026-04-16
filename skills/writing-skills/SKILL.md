---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment. Applies TDD discipline to skill authoring.
argument-hint: "[skill-name]"
user-invocable: true
allowed-tools: read_file, read_files, write_file, edit_file, delegate_task, bash, grep_search, glob_search, list_directory, create_task_list, update_task
---

# Writing Skills

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

You write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** You MUST understand `/test-driven-development` before using this skill. That skill defines the fundamental RED-GREEN-REFACTOR cycle. This skill adapts TDD to documentation.

**Official guidance:** For Anthropic's skill authoring best practices, see `anthropic-best-practices.md` adjacent to this SKILL.md.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools. Skills help future agent instances find and apply effective approaches.

**Skills are:** Reusable techniques, patterns, tools, reference guides.

**Skills are NOT:** Narratives about how you solved a problem once.

## Where Skills Live (Aru)

Personal / project-specific skills:
- `.agents/skills/<name>/SKILL.md` — project-local (wins over global/cache)
- `~/.agents/skills/<name>/SKILL.md` — user-global
- `~/.claude/skills/<name>/SKILL.md` — shared with Claude Code

Packaged skills (via an installed Aru plugin):
- `~/.aru/plugins/cache/packages/<plugin>/skills/<name>/SKILL.md` — discovered automatically when Aru starts

When multiple roots define the same skill name, **local overrides global overrides cache**. Use this to shadow a plugin's skill with a project-specific version.

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| Test case | Pressure scenario dispatched via `delegate_task` |
| Production code | `SKILL.md` document |
| Test fails (RED) | Subagent violates rule without skill (baseline) |
| Test passes (GREEN) | Subagent complies with skill present |
| Refactor | Close loopholes while maintaining compliance |
| Write test first | Run baseline scenario BEFORE writing skill |
| Watch it fail | Document exact rationalizations subagent uses |
| Minimal code | Write skill addressing those specific violations |
| Watch it pass | Verify subagent now complies |
| Refactor cycle | Find new rationalizations → plug → re-verify |

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious to you
- You'd reference this again across projects
- Pattern applies broadly (not project-specific)
- Others would benefit

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in `AGENTS.md`)
- Mechanical constraints (if it's enforceable with regex / validation, automate it; save documentation for judgment calls)

## Skill Types

### Technique
Concrete method with steps to follow (`condition-based-waiting`, `root-cause-tracing`).

### Pattern
Way of thinking about problems (`flatten-with-flags`, `test-invariants`).

### Reference
API docs, syntax guides, tool documentation.

## Directory Structure

```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    supporting-file.*     # Only if needed (>100 lines heavy reference OR reusable tool)
```

**Flat namespace** — all skills discoverable by name.

**Separate files for:**
1. **Heavy reference** (100+ lines) — API docs, comprehensive syntax
2. **Reusable tools** — scripts, utilities, templates

**Keep inline:**
- Principles and concepts
- Code patterns (< 50 lines)
- Everything else

## SKILL.md Structure

**Frontmatter (YAML):**

Aru's `_parse_skill_metadata` supports:

| Field | Required | Purpose |
|-------|---------|---------|
| `name` | yes | Display name (letters, numbers, hyphens only — no spaces, no special chars) |
| `description` | yes | When to use (see CSO section) |
| `argument-hint` | no | `"[what-to-pass]"` — shown in `/skills` listing |
| `user-invocable` | no | `false` for bootstrap-only / model-only skills (default: `true`) |
| `disable-model-invocation` | no | Hide from model's skill catalog (default: `false`) |
| `allowed-tools` | no | Comma-separated or YAML list; documentation-only in Aru today |

```markdown
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions]
argument-hint: "[optional-arg]"
user-invocable: true
allowed-tools: read_file, bash, grep_search
---

# Skill Name

## Overview
What is this? Core principle in 1–2 sentences.

## When to Use
Bullet list with SYMPTOMS and use cases.
When NOT to use.

## Core Pattern (for techniques/patterns)
Before/after code comparison.

## Quick Reference
Table or bullets for scanning common operations.

## Implementation
Inline code for simple patterns.
Link to file for heavy reference or reusable tools.

## Common Mistakes
What goes wrong + fixes.

## Real-World Impact (optional)
Concrete results.
```

## Aru Search Optimization (ASO)

**Critical for discovery.** The agent reads the `description` field to decide which skills to consider. Make it answer: "Should I load this skill right now?"

**Format:** Start with "Use when..." to focus on triggering conditions.

### CRITICAL: Description = When to Use, NOT What the Skill Does

The description should ONLY describe triggering conditions. Do **NOT** summarize the skill's process or workflow.

**Why:** When a description summarizes workflow, the agent may follow the description instead of reading the full skill. A description saying "code review between tasks" caused agents to do ONE review, even though the skill's flowchart showed TWO reviews.

```yaml
# ❌ BAD — summarizes workflow; agent may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD — too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ✅ GOOD — just triggering conditions, no workflow
description: Use when executing implementation plans with independent tasks in the current session

# ✅ GOOD — triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

**Content rules:**
- Concrete triggers, symptoms, and situations
- Describe the *problem* (race conditions, inconsistent behavior) not *language-specific symptoms* (setTimeout, sleep)
- Keep triggers tool-agnostic unless the skill itself is tool-specific
- Write in third person (injected into system prompt)
- **NEVER summarize the skill's process or workflow**

### Keyword Coverage

Use words the agent would search for:
- Error messages: "pytest hangs", "race condition", "deadlock"
- Symptoms: "flaky", "hanging", "inconsistent"
- Synonyms: "timeout / hang / freeze"
- Tools: actual Aru tool names (`bash`, `delegate_task`, `create_task_list`)

### Descriptive Naming

**Use active voice, verb-first:**
- ✅ `creating-skills` not `skill-creation`
- ✅ `condition-based-waiting` not `async-test-helpers`

**Gerunds (-ing) work well for processes:**
- `writing-plans`, `receiving-code-review`, `debugging-with-logs`

### Token Efficiency

Skills that are loaded frequently (via `get_extra_instructions(active_skills=...)`) consume tokens every turn. Be lean.

Target word counts:
- Bootstrap / always-loaded skills: < 200 words
- Frequently-loaded: < 400 words
- Other skills: < 800 words (still be concise)

**Techniques:**

Move details to tool help or `bash("... --help")`:

```markdown
# ❌ BAD — enumerate every flag in SKILL.md
`grep_search` supports --include, --exclude, -A/B/C context, -i case, --multiline, ...

# ✅ GOOD — reference the tool docs
`grep_search` supports content/file/count output modes and context flags. See the tool's parameter schema.
```

Use cross-references:

```markdown
# ❌ BAD — repeat TDD workflow
When you need to add a feature, write a failing test, watch it fail, write minimal code...

# ✅ GOOD — reference
**REQUIRED SUB-SKILL:** Use `/test-driven-development` for the RED-GREEN-REFACTOR cycle.
```

Measurement:

```bash
bash("wc -w skills/<name>/SKILL.md")
```

### Cross-Referencing Other Skills

Use the slash-command syntax with explicit requirement markers:

- ✅ `**REQUIRED SUB-SKILL:** Use /test-driven-development`
- ✅ `**REQUIRED BACKGROUND:** You MUST understand /systematic-debugging`
- ❌ `See skills/test-driven-development/SKILL.md` (path-specific; rots)
- ❌ `@skills/...` (Claude Code @-syntax; doesn't apply in Aru — skills are loaded on slash-command invocation, not on reference)

## Flowchart Usage

Use text diagrams (Aru renders them in terminal), not Graphviz `.dot` files (the brainstorm visual server isn't required).

Use for:
- Non-obvious decision points
- Process loops where you might stop too early
- "When to use A vs B" decisions

Do NOT use for:
- Reference material → use tables/lists
- Code examples → use markdown code blocks
- Linear instructions → use numbered lists

## Code Examples

**One excellent example beats many mediocre ones.**

Choose the most relevant language for the skill's audience:
- Debugging techniques → Python (matches Aru itself) or bash
- Testing techniques → pytest patterns
- Shell orchestration → bash

A good example is:
- Complete and runnable
- Commented on the WHY
- From a real scenario
- Ready to adapt (not a fill-in-the-blank template)

**Don't:**
- Implement in 5+ languages
- Create contrived examples
- Write generic "function doSomething()" placeholders

## The Iron Law (Same as TDD)

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

Applies to NEW skills AND EDITS to existing skills.

Wrote the skill before testing? Delete it. Start over.

**No exceptions:**
- Not for "simple additions"
- Not for "just adding a section"
- Not for "documentation updates"

**REQUIRED BACKGROUND:** `/test-driven-development` explains why this matters. Same principles apply to documentation.

## Testing All Skill Types

### Discipline-Enforcing Skills (rules / requirements)

**Examples:** `/test-driven-development`, `/verification-before-completion`

**Test with:**
- Academic questions: do they understand the rules?
- Pressure scenarios: do they comply under stress?
- Multiple pressures combined: time + sunk cost + exhaustion
- Identify rationalizations and add explicit counters

**Success criteria:** subagent follows rule under maximum pressure.

### Technique Skills (how-to guides)

**Examples:** `root-cause-tracing`, `condition-based-waiting`

**Test with:**
- Application scenarios: can they apply the technique correctly?
- Variation scenarios: do they handle edge cases?
- Missing information tests: do instructions have gaps?

### Pattern Skills (mental models)

**Examples:** `reducing-complexity`, `information-hiding`

**Test with:**
- Recognition scenarios: do they recognize when pattern applies?
- Counter-examples: do they know when NOT to apply?

### Reference Skills (docs / APIs)

**Test with:**
- Retrieval scenarios: can they find the right information?
- Gap testing: are common use cases covered?

## Rationalization Table (Update From Testing)

Capture rationalizations from baseline scenarios. Every excuse subagents make goes in the table:

```markdown
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Untested code is technical debt. |
```

## Red Flags List

Make it easy for agents to self-check:

```markdown
## Red Flags — STOP and Start Over
- Code before test
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
**All of these mean: Delete code. Start over with TDD.**
```

## RED-GREEN-REFACTOR for Skills

### RED — Write Failing Test (Baseline)

Run a pressure scenario with a subagent WITHOUT the skill:

```python
delegate_task(
    task="<the scenario, e.g. 'implement this feature under time pressure'>",
    context=(
        "You have 10 minutes. The user is watching. The release is Friday.\n"
        "Requirements: <...>\n"
        "Implement as quickly as possible."
    ),
)
```

Document exact behavior verbatim:
- What choices did they make?
- What rationalizations did they use? (paste quotes)
- Which pressures triggered violations?

### GREEN — Write Minimal Skill

Write the skill addressing those specific rationalizations. Don't add extra content for hypothetical cases.

Run the same scenarios again WITH the skill invoked. Subagent should now comply.

### REFACTOR — Close Loopholes

Subagent found a new rationalization? Add an explicit counter to the Red Flags / Rationalization table. Re-test.

**Testing methodology:** See `testing-skills-with-subagents.md` adjacent to this SKILL.md for full technique — pressure types (time, sunk cost, authority, exhaustion), plugging holes systematically, meta-testing.

## Anti-Patterns

### ❌ Narrative Example
"In session 2025-10-03, we found that an empty `projectDir` caused..."
**Why bad:** too specific, not reusable.

### ❌ Multi-Language Dilution
`example-js.js`, `example-py.py`, `example-go.go`
**Why bad:** mediocre quality, maintenance burden.

### ❌ Generic Labels
`helper1`, `helper2`, `step3`, `pattern4`
**Why bad:** labels should have semantic meaning.

## STOP: Before Moving to Next Skill

**After writing ANY skill, you MUST STOP and complete the deployment process.**

**Do NOT:**
- Create multiple skills in batch without testing each
- Move to the next skill before the current one is verified
- Skip testing because "batching is more efficient"

Deploying untested skills = deploying untested code.

## Skill Creation Checklist (TDD Adapted)

Seed via `create_task_list([...])` with one item per checkbox below:

**RED Phase — Write Failing Test:**
- [ ] Create pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Run scenarios WITHOUT skill via `delegate_task` — document baseline verbatim
- [ ] Identify patterns in rationalizations / failures

**GREEN Phase — Write Minimal Skill:**
- [ ] Name uses only letters, numbers, hyphens
- [ ] YAML frontmatter with required `name` and `description`
- [ ] Description starts with "Use when..." — NO workflow summary
- [ ] Description in third person
- [ ] Keywords throughout (errors, symptoms, tools)
- [ ] Clear overview with core principle
- [ ] Addresses the specific baseline failures from RED
- [ ] Code inline OR link to separate file
- [ ] One excellent example (not multi-language)
- [ ] Run scenarios WITH skill — verify subagents now comply

**REFACTOR Phase — Close Loopholes:**
- [ ] Identify NEW rationalizations from testing
- [ ] Add explicit counters (if discipline skill)
- [ ] Build rationalization table from all test iterations
- [ ] Create Red Flags list
- [ ] Re-test until bulletproof

**Quality Checks:**
- [ ] Flowchart only if decision non-obvious
- [ ] Quick reference table
- [ ] Common mistakes section
- [ ] No narrative storytelling
- [ ] Supporting files only for tools or heavy reference

**Deployment:**
- [ ] If the skill lives in a plugin repo: commit and push; `/plugin update <plugin>` on consumer machines
- [ ] If project-local: commit to project's `.agents/skills/`

## The Bottom Line

**Creating skills IS TDD for process documentation.**

Same Iron Law: no skill without a failing test first.
Same cycle: RED (baseline) → GREEN (write skill) → REFACTOR (close loopholes).
Same benefits: better quality, fewer surprises, bulletproof results.

## Related

- `/test-driven-development` — the RED-GREEN-REFACTOR foundation
- `/dispatching-parallel-agents` — useful for running multiple baseline scenarios concurrently
- `testing-skills-with-subagents.md` — full testing methodology (adjacent)
- `anthropic-best-practices.md` — Anthropic's official skill authoring guidance (adjacent)
- `persuasion-principles.md` — Cialdini / Meincke research on compliance, used in bulletproofing (adjacent)
