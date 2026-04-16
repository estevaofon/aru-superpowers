# Code Quality Reviewer Prompt Template

Use this template when dispatching a **code quality reviewer** subagent via `delegate_task`.

**Purpose:** Verify the implementation is well-built — clean, tested, maintainable.

**Only dispatch after the spec compliance reviewer reports SPEC_COMPLIANT.**

```python
delegate_task(
    task="Code quality review for Task N (commit <head_sha>)",
    context=(
        "Spec compliance is already approved. Focus ONLY on quality.\n\n"

        "## What Was Implemented\n"
        "<Implementer's report summary>\n\n"

        "## Plan / Requirements\n"
        "Task N from docs/aru/plans/<plan-file>.md\n"
        "<Full text of Task N>\n\n"

        "## Commits to review\n"
        "Base: <git SHA before this task>\n"
        "Head: <git SHA after this task>\n"
        "Use bash('git diff <base>..<head>') and read_file on new/changed files.\n\n"

        "## Task Summary\n"
        "<One-line description of what Task N was>\n\n"

        "## Standard checks\n"
        "- Adherence to existing codebase patterns and conventions\n"
        "- Proper error handling and defensive programming at system boundaries\n"
        "- Naming: clear, accurate, reflect behavior (not implementation)\n"
        "- Test quality: do tests verify real behavior, not mock behavior?\n"
        "- Security: any secrets, unsafe subprocess, path traversal, injection?\n"
        "- Performance: obvious complexity or resource issues?\n\n"

        "## Structure checks (in addition to standard concerns)\n"
        "- Does each new/modified file have one clear responsibility with a well-\n"
        "  defined interface?\n"
        "- Are units decomposed so they can be understood and tested independently?\n"
        "- Does the implementation follow the file structure from the plan?\n"
        "- Did this implementation create files that are already large, or \n"
        "  significantly grow existing files? Don't flag pre-existing file sizes —\n"
        "  focus on what THIS change contributed.\n\n"

        "## Report Format\n"
        "Use the standard review format from /requesting-code-review:\n\n"
        "## Summary\n"
        "<one paragraph assessment>\n\n"
        "## Strengths\n"
        "- ...\n\n"
        "## Critical Issues\n"
        "<or: None.>\n\n"
        "## Important Issues\n"
        "<or: None.>\n\n"
        "## Suggestions\n"
        "<or: None.>\n\n"
        "## Plan Deviations\n"
        "<or: None.>\n\n"
        "## Recommended Actions\n"
        "1. ...\n"
    ),
    agent_name="code-reviewer",
)
```

## Handling the result

- **No Critical or Important issues** → mark Task N complete with `update_task`, move on to the next task
- **Critical or Important issues** → re-dispatch the implementer with the issue list → re-run this quality review → repeat until clean
- **Only Suggestions** → optional: apply if cheap, otherwise skip. Mark task complete.
