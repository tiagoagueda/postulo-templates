"""The letters that pair with the CVs: one for each theme, under the same name."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from postulo.documents import themes
from postulo.documents.models import CoverLetter
from postulo.documents.rendering import render_letter_html

from postulo_templates.plugin import Templates

from .test_every_theme import draw

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "postulo_templates"
#: The themes that set a CV: a report-only theme is not a family and has no letter.
FAMILIES = [theme.name for theme in Templates.themes if theme.sets(themes.Kind.CV)]

MONTHS_IN_FRENCH = (
    "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
)


def test_every_cv_theme_has_a_letter_under_the_same_name():
    """What is sent together looks like one set (postulo/postulo#132)."""
    for theme in Templates.themes:
        if not theme.sets(themes.Kind.CV):
            continue
        assert theme.sets(themes.Kind.LETTER), f"{theme.name} has a CV and no letter"


@pytest.mark.parametrize("name", FAMILIES)
def test_the_letter_picker_offers_it_with_this_plugin_as_its_provider(name):
    assert name in [one.name for one in themes.for_kind(themes.Kind.LETTER)]
    label = dict(themes.choices_for(themes.Kind.LETTER))[name]
    assert label.endswith(", from Postulo Templates")


@pytest.mark.parametrize("name", FAMILIES)
def test_a_letter_stands_alone_with_the_senders_details_at_the_top(person, name):
    """No application and no CV beside it: the sender opens the page."""
    html = draw(person, name, themes.Kind.LETTER)

    body = html.split("<body>", 1)[1]
    assert body.index("Alex Morgan") < body.index("Dear team")
    assert "I would like to keep your turrets calm." in html


@pytest.mark.parametrize("name", FAMILIES)
def test_the_date_follows_the_letters_language_not_the_readers(person, name):
    french = draw(person, name, themes.Kind.LETTER, language="fr-FR")

    assert re.search(MONTHS_IN_FRENCH, french), "the date is not in French"


@pytest.mark.parametrize("name", FAMILIES)
def test_a_letter_adds_no_word_of_its_own(name):
    """Nothing here for a translator: the date and the recipient arrive written, and the
    rest is what the person typed."""
    source = PACKAGE / "templates" / "postulo_templates" / name / "letter.html"
    text = source.read_text(encoding="utf-8")
    assert "translate" not in text
    assert "blocktranslate" not in text


def test_the_europass_letter_is_set_in_the_cvs_typeface(person):
    html = draw(person, "europass", themes.Kind.LETTER)

    assert "data:font/woff2;base64," in html
    assert "font-family: Arimo" in html


def test_an_arabic_letter_mirrors_the_rule_under_the_sender(person):
    html = draw(person, "europass", themes.Kind.LETTER, language="ar")

    assert 'dir="rtl"' in html
    assert '[dir="rtl"] .sender::after' in html
    assert "@font-face" not in html, "Arimo does not draw Arabic"


def test_a_letter_may_name_an_application(person):
    """The recipient line is the base's, filled from the application's company; a letter
    drawn without one says nothing of the sort."""
    letter = CoverLetter.objects.create(
        owner=person, name="Plain", subject="Hello", body="Body", theme="ats"
    )

    assert 'class="recipient"' not in render_letter_html(letter)
