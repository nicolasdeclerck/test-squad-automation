#!/usr/bin/env python3
"""Lint bash code blocks embedded in SKILL.md / references.

Extracts fenced ```bash blocks from every Markdown file under
``.claude/skills/``, writes each block to a temporary file, and runs
``shellcheck`` on it. Exits non-zero if any block fails.

Notes
-----
- SKILL.md snippets mix shell variables (``$VAR``) and placeholder
  syntax (``{ISSUE_NUMBER}``, ``{session}``). To avoid a flood of
  false-positives, we run shellcheck with ``-e SC1009,SC1072,SC1073,SC2086``
  and ``-S warning`` (errors + warnings only, no info/style).
- ``{PLACEHOLDER}`` tokens are substituted with ``PLACEHOLDER`` before
  lint so shellcheck can parse the block as valid bash.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"

# Directories under .claude/skills/ that should NOT be linted:
# - _archived: historical snapshots, not maintained
# - agent-browser: external skill imported as-is, not our code
EXCLUDED_DIRS = {"_archived", "agent-browser"}

FENCE_RE = re.compile(r"^```bash\s*$")
FENCE_END_RE = re.compile(r"^```\s*$")
PLACEHOLDER_RE = re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")

SHELLCHECK_DISABLED = [
    "SC1009",  # confused about mismatched keywords in heredoc
    "SC1072",
    "SC1073",
    "SC2016",  # single quotes around $VAR in Python heredocs is intentional
    "SC2086",  # quoting of $VAR — many snippets rely on word splitting
    "SC2154",  # referenced but not assigned (env vars injected by workflow)
    "SC2155",  # declare and assign separately
    "SC2034",  # unused variables (they are used later in the surrounding prose)
]


def extract_bash_blocks(path: pathlib.Path) -> list[tuple[int, str]]:
    """Return list of (start_line, block_content) for each ```bash block."""
    blocks: list[tuple[int, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        if FENCE_RE.match(lines[i]):
            start = i + 1
            buf: list[str] = []
            i += 1
            while i < len(lines) and not FENCE_END_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            blocks.append((start, "\n".join(buf) + "\n"))
        i += 1
    return blocks


def normalise(block: str) -> str:
    """Replace ``{PLACEHOLDER}`` tokens with ``PLACEHOLDER`` so shellcheck parses."""
    return PLACEHOLDER_RE.sub(lambda m: m.group(1), block)


def lint_block(block: str) -> tuple[int, str]:
    disabled = ",".join(SHELLCHECK_DISABLED)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False, encoding="utf-8"
    ) as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(normalise(block))
        tmp = f.name
    try:
        proc = subprocess.run(
            [
                "shellcheck",
                "--shell=bash",
                "-S",
                "warning",
                "-e",
                disabled,
                tmp,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout + proc.stderr
    finally:
        pathlib.Path(tmp).unlink(missing_ok=True)


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"No skills directory at {SKILLS_DIR}", file=sys.stderr)
        return 0

    md_files = sorted(
        p
        for p in SKILLS_DIR.rglob("*.md")
        if not any(part in EXCLUDED_DIRS for part in p.relative_to(SKILLS_DIR).parts)
    )
    failed = 0
    total = 0

    for md in md_files:
        rel = md.relative_to(ROOT)
        blocks = extract_bash_blocks(md)
        for start_line, block in blocks:
            total += 1
            rc, output = lint_block(block)
            if rc != 0:
                failed += 1
                print(f"::error file={rel},line={start_line}::shellcheck failed")
                print(f"--- {rel}:{start_line} ---")
                print(output.rstrip())
                print()

    print(
        f"lint-skills: {total - failed}/{total} bash blocks clean "
        f"({failed} failing) across {len(md_files)} files."
    )
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
