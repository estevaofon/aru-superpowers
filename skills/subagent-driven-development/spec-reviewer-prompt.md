# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a **spec compliance reviewer** subagent via `delegate_task`.

**Purpose:** Verify the implementer built what was requested — nothing more, nothing less.

```python
delegate_task(
    task="Review spec compliance for Task N",
    context=(
        "You are reviewing whether an implementation matches its specification.\n\n"

        "## What Was Requested\n"
        "<FULL TEXT of Task N requirements from the plan>\n\n"

        "## What the Implementer Claims They Built\n"
        "<Paste the implementer's final report verbatim>\n\n"

        "## Commit range to inspect\n"
        "Base: <git SHA before this task>\n"
        "Head: <git SHA after this task>\n"
        "Use bash('git show <head>') or bash('git diff <base>..<head>') to see the change.\n\n"

        "## CRITICAL: Do NOT Trust the Report\n"
        "The implementer may be incomplete, inaccurate, or optimistic.\n"
        "You MUST verify everything independently.\n\n"
        "**DO NOT:**\n"
        "- Take their word for what they implemented\n"
        "- Trust their claims about completeness\n"
        "- Accept their interpretation of requirements\n\n"
        "**DO:**\n"
        "- Read the actual code with read_file / bash('git show')\n"
        "- Compare actual implementation to requirements line by line\n"
        "- Check for missing pieces they claimed to implement\n"
        "- Look for extra features they didn't mention\n\n"

        "## Your Job\n"
        "Verify from the source code:\n\n"
        "**Missing requirements:**\n"
        "- Did they implement everything that was requested?\n"
        "- Are there requirements they skipped or missed?\n"
        "- Did they claim something works but didn't actually implement it?\n\n"
        "**Extra / unneeded work:**\n"
        "- Did they build things that weren't requested?\n"
        "- Did they over-engineer or add unnecessary features?\n"
        "- Did they add 'nice to haves' that weren't in spec?\n\n"
        "**Misunderstandings:**\n"
        "- Did they interpret requirements differently than intended?\n"
        "- Did they solve the wrong problem?\n"
        "- Did they implement the right feature but the wrong way?\n\n"
        "**Verify by reading code, NOT by trusting the report.**\n\n"

        "## Report Format\n"
        "Conclude with:\n\n"
        "Status: SPEC_COMPLIANT | ISSUES_FOUND\n"
        "Missing: <list any missing requirements with file:line references>\n"
        "Extra: <list any unrequested work>\n"
        "Misunderstandings: <list any misinterpretations>\n"
        "Evidence: <cite the specific lines/files that support each finding>\n"
    ),
    agent_name="code-reviewer",  # read-only tools, ideal for review
)
```

## Handling the result

- **SPEC_COMPLIANT** → proceed to the code-quality reviewer
- **ISSUES_FOUND** → re-dispatch the implementer with the gap list, then re-run this spec reviewer; don't skip the re-review
