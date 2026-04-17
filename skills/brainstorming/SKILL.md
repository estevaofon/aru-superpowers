---
name: brainstorming
description: Use BEFORE any creative work — creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and design before implementation.
argument-hint: "[idea-or-feature-topic]"
user-invocable: true
allowed-tools: read_file, read_files, glob_search, grep_search, list_directory, bash, write_file, create_task_list, update_task
disallowed-tools: enter_plan_mode
---

<HARD-GATE>
Do NOT invoke any implementation skill, write code, scaffold any project, or take any implementation action until a design is presented and the user has approved it. This applies to EVERY project regardless of perceived simplicity.

`enter_plan_mode` is blocked by this skill at the tool level (see `disallowed-tools` in the frontmatter) and will return a `BLOCKED` error. The correct path is: brainstorm → write spec to `docs/aru/specs/` via `write_file` → `invoke_skill("writing-plans")`.
</HARD-GATE>

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural, collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you are building, present the design and get user approval.

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

Seed a task list mirroring these items and complete them in order. Each Step-4 sub-item must be marked complete ONLY after the user has given an explicit approval for that section.

```
create_task_list([
  "Explore project context",
  "Offer visual companion (if visual questions are anticipated)",
  "Ask clarifying questions (one at a time)",
  "Propose 2-3 approaches with tradeoffs; user picks one",
  "Step 4a: Present architecture section; get approval",
  "Step 4b: Present components section; get approval",
  "Step 4c: Present data flow section; get approval",
  "Step 4d: Present error handling section; get approval",
  "Step 4e: Present testing strategy section; get approval",
  "Write design doc to docs/aru/specs/",
  "Self-review spec inline",
  "User reviews written spec",
  "Transition to /writing-plans"
])
```

**Gate:** You cannot mark any Step 4 sub-item complete in the same message where you presented it. The user must respond first. A checklist with Step 4a–4e all completed in one turn is proof that Step 4 was skipped.

## Process Flow

```
Explore project context
  └─> Visual questions ahead?
        ├── yes → Offer Visual Companion (own message, no other content)
        └── no  → Ask clarifying questions (one per message)
                  │
                  ▼
                Propose 2-3 approaches (Step 3)
                  │
                  └─> User picks ONE approach  ← NOT approval of the design
                        │
                        ▼
                      Present ARCHITECTURE section (Step 4a)
                        └── wait for explicit approval ──> Present COMPONENTS (Step 4b)
                                                            └── wait ──> Present DATA FLOW (Step 4c)
                                                                          └── wait ──> Present ERROR HANDLING (Step 4d)
                                                                                        └── wait ──> Present TESTING (Step 4e)
                                                                                                      │
                                                                                                      ▼
                                                                                         Write design doc
                                                                                           └─> Self-review (fix inline)
                                                                                               └─> User reviews written spec
                                                                                                   ├── changes → revise + re-review
                                                                                                   └── approved → invoke /writing-plans
```

**The terminal state is invoking `/writing-plans`.** Do NOT invoke any other implementation skill after brainstorming. The only skill you call next is `/writing-plans`.

**Boundary between Step 3 and Step 4:** The user's answer at Step 3 is "I pick approach X." It is NOT "write the spec." Even if the user says "sim, pode seguir" after you propose approaches, you still go to Step 4a (architecture section), NOT to spec writing.

## The Process

### Understanding the idea

- **Check the project state first**: `list_directory`, `read_file("AGENTS.md")`, `read_file("README.md")`, `bash("git log --oneline -20")`
- Before asking detailed questions, **assess scope**: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then brainstorm the first sub-project through the normal design flow. Each sub-project gets its own spec → plan → implementation cycle.
- For appropriately-scoped projects, ask questions **one at a time**.
- Prefer multiple choice questions when possible; open-ended is fine too.
- **Only one question per message** — if a topic needs more exploration, break it into multiple questions.
- Focus on understanding: **purpose**, **constraints**, **success criteria**.

### Exploring approaches (Step 3)

- Propose **2–3 different approaches** with tradeoffs.
- Present options conversationally with your recommendation and reasoning.
- **Lead with your recommended option** and explain why.
- End with: "**Which approach do you prefer?**" (a choice question).

Do NOT end Step 3 with "Faz sentido?" / "Does this make sense?" / "Posso escrever a spec?" — those questions make the user approve the *approach* and the *spec* in a single yes, which skips the section-by-section design walk (Step 4) entirely. The user picking an approach is NOT permission to write the spec.

### Presenting the design (Step 4) — MANDATORY, CANNOT BE COMBINED WITH STEP 3

<CRITICAL-GATE>
After the user picks an approach, you MUST present the design **in sections**, ONE SECTION PER MESSAGE, and get explicit approval after EACH section before moving on.

Approving the approach in Step 3 is NOT approving the design. Step 4 is a separate, mandatory walk where each section gets its own yes/no.
</CRITICAL-GATE>

- Pick up the approved approach and expand it into concrete design sections.
- Scale each section to its complexity: a few sentences if straightforward, up to 200–300 words if nuanced.
- Cover, in order, at minimum:
  1. **Architecture** — the overall shape: modules, layers, process boundaries
  2. **Components** — each unit, what it does, what it owns
  3. **Data flow** — how information moves between components
  4. **Error handling** — what fails, what recovers, what surfaces
  5. **Testing strategy** — how this will be verified
- After each section, ask something like: "**Does this architecture look right before I move on to components?**"
- WAIT for the user's explicit "yes" / "looks good" / equivalent before sending the next section.
- Be ready to go back and clarify if something doesn't make sense.

**Minimum:** 3 user approvals during Step 4 (one per section). If you finish Step 4 with zero section-level approvals, you skipped Step 4.

### Forbidden shortcuts in Step 4

| Shortcut | Why forbidden |
|----------|---------------|
| "Here's the design: [architecture + components + data flow + tests all at once]. OK?" | User can't digest or veto individual sections. This is just a longer Step 3. |
| "Design approved, writing the spec now" after a single "sim" at the end of Step 3 | Approving the approach ≠ approving the design. |
| Skipping a section because "it's obvious from the approach" | If it's obvious, the section takes one sentence. Still present it and still ask. |
| Combining architecture + components into one section to save messages | Those are the two highest-risk sections — exactly the ones that need separate approval. |

### Design for isolation and clarity

### Design for isolation and clarity

- Break the system into smaller units that each have **one clear purpose**, communicate through **well-defined interfaces**, and can be understood and tested independently.
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for the agent to work with — you reason better about code you can hold in context at once, and edits are more reliable when files are focused. When a file grows large, that is often a signal that it is doing too much.

### Working in existing codebases

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that has grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design — the way a good developer improves code they are working in.
- Do NOT propose unrelated refactoring. Stay focused on what serves the current goal.

## After the Design

### Documentation

- Write the validated design (spec) to `docs/aru/specs/YYYY-MM-DD-<topic>-design.md`
  - User preferences for spec location override this default
- Use `write_file` to persist
- Commit the design document to git: `bash("git add docs/aru/specs/... && git commit -m 'spec: <topic>'")`

### Spec Self-Review

After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan** — any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency** — do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check** — is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check** — could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

### User Review Gate

After the self-review passes, ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response. If they request changes, make them and re-run the self-review loop. Only proceed once the user approves.

### Implementation

Once the user has approved the written spec:

```python
invoke_skill(name="writing-plans", arguments="docs/aru/specs/<your-spec>.md")
```

**CRITICAL:** Use the `invoke_skill` tool. Do NOT try to write the plan from memory — the writing-plans SKILL.md has a `<CRITICAL-GATE>` Entering This Skill section and a checklist template that are **not in your context** until you call the tool. Improvising will skip those gates.

Do NOT invoke any other skill. `/writing-plans` is the next step.

## Key Principles

- **One question at a time** — don't overwhelm with multiple questions
- **Multiple choice preferred** — easier to answer than open-ended when possible
- **YAGNI ruthlessly** — remove unnecessary features from all designs
- **Explore alternatives** — always propose 2–3 approaches before settling
- **Incremental validation** — present design section by section, get approval before moving on
- **Be flexible** — go back and clarify when something doesn't make sense

## Red Flags — STOP and Restart Step 4

If you catch yourself doing or thinking any of these, you are about to skip Step 4. STOP, revisit the rules above, and start Step 4a properly.

- "User said sim, I'll write the spec now" — check: did they say yes to an approach, or to a design walk? Step 3 yes → Step 4a.
- "Faz sentido? Posso escrever a spec?" as your closing message to Step 3 — this question conflates two approvals. Replace with "Which approach do you prefer?"
- Presenting architecture + components + data flow + tests in a single bulleted list before Step 4 starts — that's Step 3 over-reach.
- Marking all Step 4 sub-items completed in a single assistant turn — impossible; each requires a user reply between.
- "The design is obvious from the approach; I'll just write the spec" — if it's obvious, Step 4 takes 5 short messages. Still do it. Hidden assumptions die in Step 4, not in spec review.
- "The user seems eager; I'll skip ahead" — eagerness is not consent. Ask.

Any of these = restart from Step 4a with the chosen approach.

## Visual Companion (Optional)

A browser-based companion for showing mockups, diagrams, and visual options during brainstorming exists in the original superpowers as a Node.js server. It is **not yet included in this Aru port** — all brainstorming uses text in the terminal.

If you anticipate questions that genuinely need visuals (mockups, wireframes, layout comparisons), tell the user and ask them to sketch / describe in text, or to share screenshots via `@file` references. Future versions of this plugin may wrap the Node.js brainstorm server as a tool.

## Related

- `/writing-plans` — the one and only follow-up skill after brainstorming
- `/test-driven-development` — enforced once implementation begins
- `/using-superpowers` — the overall workflow governance
