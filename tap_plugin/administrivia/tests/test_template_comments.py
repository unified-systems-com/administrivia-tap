"""No template carries a multi-line `{# ... #}` comment.

Django's `{# #}` comment is single-line only: a newline before the closing `#}` makes the whole
block render as literal page text (the Plugins page showed a "Tabulator mount ..." paragraph).
A comment that spans lines must be `{% comment %}...{% endcomment %}`.

Pure source pin: no Django, no database, no browser.
"""

from __future__ import annotations

from pathlib import Path

import pytest

TEMPLATES = sorted((Path(__file__).resolve().parent.parent / "templates").rglob("*.html"))


def test_templates_were_found() -> None:
    assert TEMPLATES, "the guard walked no templates"


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda p: p.name)
def test_no_multiline_hash_comment(path: Path) -> None:
    offenders = [
        number
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if "{#" in line and "#}" not in line.split("{#", 1)[1]
    ]
    assert not offenders, f"{path.name}: multi-line `{{# #}}` comment opens on line(s) {offenders}; use {{% comment %}}"
