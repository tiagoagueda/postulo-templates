"""The plugin's own files: listed, licensed, drawn from the package and never fetched.

A theme cannot fetch anything while it is drawn (postulo/postulo#163), so what it carries
comes from its package through `{% theme_asset %}` (postulo/postulo#343). These hold the
promises of the issue about assets: every file listed with its licence, vector first, no
colour of its own, a font only for the scripts it draws.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from postulo.documents.theme_assets import load
from postulo.documents.themes import Kind

from postulo_templates import plugin
from postulo_templates.plugin import Templates

from .test_every_theme import draw

pytestmark = pytest.mark.usefixtures("installed")

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "src" / "postulo_templates"
ASSETS = PACKAGE / "assets"
FILES = sorted(path for path in ASSETS.rglob("*") if path.is_file())
FONTS = [path for path in FILES if path.suffix in {".woff2", ".woff", ".ttf", ".otf"}]
ICONS = [path for path in FILES if path.suffix == ".svg"]


def name_of(path: Path) -> str:
    return path.relative_to(PACKAGE).as_posix()


def test_there_are_assets_to_hold():
    assert ICONS
    assert FONTS


@pytest.mark.parametrize("path", FILES, ids=name_of)
def test_every_asset_is_listed_with_its_source_and_licence(path):
    register = (REPO / "ASSETS.md").read_text(encoding="utf-8")
    assert f"`{name_of(path)}`" in register, f"{name_of(path)} is not in ASSETS.md"


@pytest.mark.parametrize("path", FONTS, ids=name_of)
def test_a_font_has_its_licence_beside_it_and_declares_its_scripts(path):
    assert list(path.parent.glob("*OFL*.txt")) or list(path.parent.glob("*LICENSE*"))
    declared = {name for theme in Templates.themes for name in theme.font_scripts}
    assert name_of(path) in declared


@pytest.mark.parametrize("path", ICONS, ids=name_of)
def test_an_icon_is_a_vector_that_takes_its_colour_from_the_text(path):
    """So it prints in black and white, and a theme sets its colour in one place."""
    asset = load("postulo_templates", name_of(path))
    assert asset.kind == "svg"
    assert "currentColor" in asset.written
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgb\(", asset.written), "an icon sets a colour"
    assert "<text" not in asset.written, "no words inside a graphic"


def test_every_asset_a_template_names_exists_and_is_used():
    named = set()
    for path in (PACKAGE / "templates").rglob("*.html"):
        named |= set(re.findall(r'theme_asset "([^"]+)"', path.read_text(encoding="utf-8")))
    shipped = {name_of(path) for path in FILES if path.suffix != ".txt"}
    assert named <= shipped, f"named but not shipped: {sorted(named - shipped)}"
    assert shipped <= named, f"shipped but never used: {sorted(shipped - named)}"


@pytest.mark.django_db
def test_the_cv_carries_its_font_and_icons_in_the_document(person):
    html = draw(person, plugin.EUROPASS.name, Kind.CV)

    assert "@font-face" in html
    assert "data:font/woff2;base64," in html
    assert html.count('<span class="icon" aria-hidden="true"><svg') >= 1
    assert "assets/" not in html.replace("data:", ""), "a path leaked into the document"


@pytest.mark.django_db
def test_a_script_the_font_does_not_draw_is_set_in_the_servers_fonts(person):
    """Arabic is not Arimo's: Postulo leaves the font out, so the stack falls through."""
    html = draw(person, plugin.EUROPASS.name, Kind.CV, language="ar")

    assert "@font-face" not in html
