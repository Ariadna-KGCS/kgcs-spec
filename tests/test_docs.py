"""Internal Markdown links resolve (CLAUDE.md release check)."""

import re
from urllib.parse import unquote

import pytest

from conftest import ROOT

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP_DIRS = {".git", ".venv", "venv", ".pytest_cache", "node_modules"}
MD_FILES = sorted(p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.parts))


@pytest.mark.parametrize("path", MD_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_markdown_links_resolve(path):
    text = path.read_text(encoding="utf-8")
    broken = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        candidate = (path.parent / target).resolve()
        if not candidate.exists():
            broken.append(target)
    assert not broken, f"{path.relative_to(ROOT)}: broken relative links {broken}"


def test_markdown_files_present():
    assert MD_FILES
