"""Every theme this plugin declares, drawn for every kind it declares.

Written over the plugin's own list rather than by naming themes, so a theme added later is
held to the same promises without anybody remembering to add it here: it says its language
and its direction, it asks for nothing outside itself, it carries what the document says
about itself, and it draws within the paper it says it prints on.
"""

from __future__ import annotations

import datetime as dt
import itertools
import re
from ctypes.util import find_library

import pytest
from postulo.documents import paper as papers
from postulo.documents import themes
from postulo.documents.models import CV, CoverLetter, CVKind
from postulo.documents.pdf import WeasyPrintBackend
from postulo.documents.properties import SCRUB_META, Properties
from postulo.documents.rendering import render_cv_html, render_letter_html
from postulo.resume.models import Experience

from postulo_templates.plugin import Templates

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]

#: Each theme the plugin declares, with each kind it sets: what a picker would offer.
EVERY = [(theme.name, kind) for theme in Templates.themes for kind in theme.templates]

#: A language each way round, and one with a script of its own.
LANGUAGES = [("en-GB", "ltr"), ("fr-FR", "ltr"), ("ar", "rtl")]

#: A document's name is unique to its owner, and one test may draw two.
COUNT = itertools.count(1)

needs_pango = pytest.mark.skipif(
    find_library("pango-1.0") is None,
    reason="Pango is not installed here, and WeasyPrint draws with it",
)


def draw(person, name: str, kind: str, *, language: str = "en-GB", **options) -> str:
    """The HTML of one document of ``kind`` set in the theme ``name``."""
    if kind == themes.Kind.LETTER:
        letter = CoverLetter.objects.create(
            owner=person,
            name=f"Letter {next(COUNT)}",
            subject="Test engineer",
            body="Dear team,\n\nI would like to keep your turrets calm.\n\nAlex",
            theme=name,
            language=language,
        )
        return render_letter_html(letter, **options)
    cv = CV.objects.create(
        owner=person,
        name=f"Main {next(COUNT)}",
        theme=name,
        language=language,
        headline="Test engineer",
        summary="Ten years of keeping things calm.",
        kind=CVKind.PORTFOLIO if kind == themes.Kind.PORTFOLIO else CVKind.CV,
    )
    Experience.objects.create(
        owner=person,
        organisation="Aperture Science",
        role="Test engineer",
        start_date=dt.date(2019, 3, 1),
        highlights="Kept the turrets calm.",
    )
    return render_cv_html(cv, **options)


def test_the_plugin_declares_something_to_hold_to_this():
    """A sanity check on the check: no themes would make everything below pass."""
    assert EVERY


@pytest.mark.parametrize(("name", "kind"), EVERY)
def test_every_theme_is_offered_for_every_kind_it_sets(name, kind):
    assert name in [one.name for one in themes.for_kind(kind)]


@pytest.mark.parametrize(("name", "kind"), EVERY)
@pytest.mark.parametrize(("language", "direction"), LANGUAGES)
def test_every_theme_says_its_language_and_direction(person, name, kind, language, direction):
    html = draw(person, name, kind, language=language)

    assert f'<html lang="{language}" dir="{direction}">' in html
    assert "<title>" in html


@pytest.mark.parametrize(("name", "kind"), EVERY)
def test_no_theme_asks_for_anything_outside_the_document(person, name, kind):
    """Both renderers refuse everything but a `data:` address, so a theme that asks fails
    quietly in the PDF and loudly in the preview."""
    html = draw(person, name, kind)

    asked = re.findall(r"""(?:src\s*=\s*|url\(\s*)["']?(?!data:)([^"')\s>]+)""", html)
    assert asked == []
    assert "@import" not in html
    assert "<link" not in html


@pytest.mark.parametrize(("name", "kind"), EVERY)
def test_every_theme_carries_what_the_export_says_about_itself(person, name, kind):
    """The author where the properties are carried; the instruction to strip where they
    are not (postulo/postulo#878, #480)."""
    assert '<meta name="author" content="Alex Morgan">' in draw(person, name, kind)

    stripped = draw(person, name, kind, properties=Properties(include=False))
    assert 'name="author"' not in stripped

    person.profile.export_strip_metadata = True
    person.profile.save()
    assert f'<meta name="{SCRUB_META}" content="producer">' in draw(person, name, kind)


# ------------------------------------------------------------------------- the PDF


def outside(page) -> list:
    """Everything laid out past either side of the page's printable area.

    Postulo's own measurement (`tests/test_pdf_render.py` in the core), taken at both
    edges, because a right-to-left document runs off on the left. A margin box is in the
    margin on purpose and is not measured.
    """
    box = page._page_box
    start = box.content_box_x()
    end = start + box.width
    return [
        child
        for child in box.descendants()
        if isinstance(getattr(child, "position_x", None), int | float)
        and isinstance(getattr(child, "width", None), int | float)
        and child is not box
        and type(child).__name__ != "MarginBox"
        and (child.position_x < start - 1 or child.position_x + child.width > end + 1)
    ]


PRINTED = [
    (name, kind, paper.key)
    for name, kind in EVERY
    for paper in papers.declared(
        next(theme for theme in Templates.themes if theme.name == name), kind
    )
]


@needs_pango
@pytest.mark.parametrize(("name", "kind", "paper"), PRINTED)
@pytest.mark.parametrize("language", ["en-GB", "ar"])
def test_every_theme_draws_within_every_paper_it_declares(
    person, caplog, name, kind, paper, language
):
    html = draw(person, name, kind, language=language, paper=paper)

    document = WeasyPrintBackend().document(html).render()

    assert document.pages, "nothing was drawn"
    assert not any(outside(page) for page in document.pages)
    assert "Failed to load" not in caplog.text, "the theme asked for something outside itself"
