"""aru-superpowers bootstrap plugin.

Injects the `using-superpowers` skill content into the system prompt of
primary agents (build/executor). Mirrors the Claude Code SessionStart hook
that the original obra/superpowers plugin relies on, but uses Aru's
`chat.system.transform` hook for the same effect.

Behavior:
  - Loads skills/using-superpowers/SKILL.md once at plugin init.
  - On every primary-agent creation, appends the bootstrap to the system prompt.
  - Skips lightweight subagents (explorer, plan) to save tokens.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aru.plugins import Hooks, PluginInput

logger = logging.getLogger("aru.plugins.superpowers")


PRIMARY_AGENT_NAMES = {"", "Aru", "build", "executor", "general"}
BOOTSTRAP_SENTINEL = "<!-- aru-superpowers:bootstrap -->"
BOOTSTRAP_HEADER = (
    "\n\n"
    f"{BOOTSTRAP_SENTINEL}\n"
    "<EXTREMELY_IMPORTANT>\n"
    "The following superpowers bootstrap governs how to discover and invoke "
    "other skills. Treat it as binding guidance.\n"
    "</EXTREMELY_IMPORTANT>\n\n"
)


def _find_plugin_root(start: Path | None = None) -> Path:
    """Walk up from this file until we find aru-plugin.json."""
    candidate = (start or Path(__file__)).resolve()
    for parent in [candidate, *candidate.parents]:
        if (parent / "aru-plugin.json").is_file():
            return parent
    # Fallback: this file's parent's parent (plugins/ -> plugin_root)
    return Path(__file__).resolve().parent.parent


def _load_bootstrap(plugin_root: Path) -> str:
    skill_md = plugin_root / "skills" / "using-superpowers" / "SKILL.md"
    if not skill_md.is_file():
        logger.warning("using-superpowers SKILL.md not found at %s", skill_md)
        return ""
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        logger.warning("Failed to read %s: %s", skill_md, exc)
        return ""
    # Strip frontmatter so we only inject the body
    if content.startswith("---"):
        lines = content.split("\n")
        end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end > 0:
            content = "\n".join(lines[end + 1:])
    return content.strip()


def plugin(ctx: PluginInput, options=None) -> Hooks:
    hooks = Hooks()
    options = options or {}

    plugin_root = _find_plugin_root()
    bootstrap = _load_bootstrap(plugin_root)
    if not bootstrap:
        logger.info("superpowers: no bootstrap content, hook inactive")
        return hooks

    primary_names = set(options.get("primary_agents") or PRIMARY_AGENT_NAMES)
    payload = BOOTSTRAP_HEADER + bootstrap

    @hooks.on("chat.system.transform")
    def inject_bootstrap(event):
        agent = event.data.get("agent") or ""
        if agent not in primary_names:
            return
        prompt = event.system_prompt
        # Idempotent: skip if sentinel already present
        if BOOTSTRAP_SENTINEL in prompt:
            return
        event.system_prompt = prompt + payload

    logger.info("superpowers: bootstrap hook active (%d chars)", len(payload))
    return hooks
