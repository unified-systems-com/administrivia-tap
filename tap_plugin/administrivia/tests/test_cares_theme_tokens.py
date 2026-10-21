"""The CARES stylesheets read core's theme palette, never a literal hex colour.

Core's theme (`tap_web/specs/spec-web-theme.md`, `req-web-theme-scope`) leaves a plugin's own stylesheet to
the plugin: a literal `#f8fafc` surface stays light when the viewer picks dark. Every colour in the
CARES pages' stylesheets is therefore `rgb(var(--tap-<name>-<shade>))`, which has a light and a dark
value. The only literals allowed are `rgb(R G B)` triplets for the two things that must NOT flip:
the solid-fill Run / Self-test buttons (white label on a fixed fill) and the dark log console.

Pure source pin: no Django, no database, no browser.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CSS_DIR = Path(__file__).resolve().parent.parent / "static" / "administrivia" / "css"
CARES_CSS = sorted(
    "cares_" + name + ".css"
    for name in ("collector_table", "collector_detail", "run_detail", "schedule_table", "schedule_detail")
)

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
LEGACY_FN = re.compile(r"\b(?:rgba|hsla?)\(")
# `rgb(29 78 216)`-style fixed triplets: allowed, but only these exact fills.
FIXED_TRIPLET = re.compile(r"rgb\(\s*\d+\s+\d+\s+\d+\s*\)")
ALLOWED_FIXED = {
    "rgb(29 78 216)",  # primary button fill
    "rgb(30 64 175)",  # primary button hover
    "rgb(71 85 105)",  # secondary button fill / log console border
    "rgb(51 65 85)",  # secondary button hover
    "rgb(255 255 255)",  # button label
    "rgb(15 23 42)",  # log console background
    "rgb(226 232 240)",  # log console text
}


def _text(name: str) -> str:
    return re.sub(r"/\*.*?\*/", "", (CSS_DIR / name).read_text(), flags=re.S)


def test_the_five_cares_stylesheets_exist() -> None:
    for name in CARES_CSS:
        assert (CSS_DIR / name).is_file(), name


@pytest.mark.parametrize("name", CARES_CSS)
def test_no_literal_hex_colour(name: str) -> None:
    assert HEX.findall(_text(name)) == []


@pytest.mark.parametrize("name", CARES_CSS)
def test_no_rgba_or_hsl_literals(name: str) -> None:
    assert LEGACY_FN.findall(_text(name)) == []


@pytest.mark.parametrize("name", CARES_CSS)
def test_fixed_triplets_are_only_the_named_exceptions(name: str) -> None:
    found = {re.sub(r"\s+", " ", m).replace("( ", "(").replace(" )", ")") for m in FIXED_TRIPLET.findall(_text(name))}
    assert found <= ALLOWED_FIXED, found - ALLOWED_FIXED


@pytest.mark.parametrize("name", CARES_CSS)
def test_palette_references_use_a_real_token_shape(name: str) -> None:
    for token in re.findall(r"var\((--tap-[a-z0-9-]+)\)", _text(name)):
        assert re.fullmatch(r"--tap-(?:[a-z]+-\d{2,3}|white|black|canvas)", token), token
