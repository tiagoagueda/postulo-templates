"""The Europass theme, drawn by a real Postulo from the plugin as it is installed.

Through the entry point rather than by registering the theme by hand, because the entry
point is what an instance reads: a theme that renders when it is handed to Postulo directly
and is never offered by the plugin is the failure worth catching.
"""

from __future__ import annotations

import datetime as dt
import re
from ctypes.util import find_library

import pytest
from postulo.documents import pdf as pdf_options
from postulo.documents import themes
from postulo.documents.models import CV, CVKind
from postulo.documents.pdf import WeasyPrintBackend
from postulo.documents.rendering import render_cv_html
from postulo.resume.models import Certification, Education, Experience, LanguageSkill

from .support import on_the_cv

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]

ROLE = "Test engineer"
QUALIFICATION = "MSc Applied Physics"


@pytest.fixture
def cv(person):
    document = CV.objects.create(
        owner=person,
        name="Main",
        theme="europass",
        language="en-GB",
        headline="Test engineer",
        summary="Ten years of keeping things calm.",
        show_eqf_level=True,
    )
    on_the_cv(
        document,
        Experience.objects.create(
            owner=person,
            organisation="Aperture Science",
            role=ROLE,
            location="Cleveland",
            start_date=dt.date(2019, 3, 1),
            highlights="Kept the turrets calm.\nWrote the safety notes.",
        ),
        Education.objects.create(
            owner=person,
            qualification=QUALIFICATION,
            institution="University of Porto",
            start_date=dt.date(2012, 9, 1),
            end_date=dt.date(2014, 7, 1),
            eqf_level=7,
        ),
        LanguageSkill.objects.create(owner=person, name="Portuguese", proficiency="native"),
        LanguageSkill.objects.create(owner=person, name="English", proficiency="b2"),
        LanguageSkill.objects.create(owner=person, name="French", proficiency=""),
        Certification.objects.create(
            owner=person, name="ISTQB Foundation", issuer="ISTQB", issued_on=dt.date(2020, 5, 1)
        ),
    )
    return document


def text_of(html: str) -> str:
    """The words in the markup, in order, without the tags or the stylesheet."""
    body = re.split(r"<body[^>]*>", html, maxsplit=1)[1]
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()


# ----------------------------------------------------------- what the plugin offers


def test_the_plugin_offers_the_theme_for_a_cv_and_names_itself():
    theme = themes.find("europass")
    assert theme is not None, "the entry point did not register the theme"
    assert theme.sets(themes.Kind.CV)
    wanted = ("europass", "Europass layout, from Postulo Templates")
    assert wanted in themes.choices_for(themes.Kind.CV)


def test_it_sets_a_portfolio_with_the_same_page():
    assert "europass" in [one.name for one in themes.for_kind(themes.Kind.PORTFOLIO)]


def test_a_portfolio_says_it_is_one_in_the_masthead(person):
    portfolio = CV.objects.create(
        owner=person, name="Work", theme="europass", kind=CVKind.PORTFOLIO, language="en-GB"
    )

    assert "Portfolio" in text_of(render_cv_html(portfolio))[:40]
    assert "Curriculum Vitae" not in render_cv_html(portfolio)


# ------------------------------------------------------------------- what it draws


def test_the_cv_says_its_language_and_direction(cv):
    html = render_cv_html(cv)

    assert '<html lang="en-GB" dir="ltr">' in html
    assert "<title>" in html


def test_an_arabic_cv_is_laid_out_right_to_left(person):
    cv = CV.objects.create(owner=person, name="سيرة", theme="europass", language="ar")

    assert 'dir="rtl"' in render_cv_html(cv)


def test_every_entry_is_drawn_with_its_dates_in_the_label_column(cv):
    html = render_cv_html(cv)

    assert f'<h3 class="role">{ROLE}</h3>' in html
    assert QUALIFICATION in html
    assert "EQF level 7" in html
    assert "Kept the turrets calm." in html
    dates = re.findall(r'<p class="aside dates">([^<]*)</p>', html)
    assert dates == ["March 2019 – present", "September 2012 – July 2014"]


def test_the_name_comes_first_and_the_sections_keep_their_order(cv):
    words = text_of(render_cv_html(cv))

    assert words.startswith("Curriculum Vitae Personal information Alex Morgan")
    order = [words.index(one) for one in ("Experience", "Education", "Languages", "Certifications")]
    assert order == sorted(order)


def test_each_language_label_is_printed_once_and_a_level_only_where_there_is_one(cv):
    words = text_of(render_cv_html(cv))

    assert words.count("Mother tongue(s)") == 1
    assert words.count("Other language(s)") == 1
    assert "Mother tongue(s) Portuguese Other language(s) English B2" in words
    assert re.search(r"French\s*Levels:", words), "a level nobody stated printed something"
    assert words.count("Common European Framework of Reference") == 1


def test_no_cefr_note_where_no_language_has_a_level(person):
    cv = CV.objects.create(owner=person, name="Plain", theme="europass")
    on_the_cv(cv, LanguageSkill.objects.create(owner=person, name="Basque", proficiency="native"))

    assert "Common European Framework" not in render_cv_html(cv)


def test_the_icons_are_hidden_and_nothing_is_written_by_css(cv):
    html = render_cv_html(cv)

    # Postulo's sanitiser drops attributes it does not know from an SVG, so the picture is
    # hidden by the element around it.
    icons = re.findall(r"<svg[^>]*>", html)
    assert icons, "the contact lines drew no icon"
    assert html.count('<span class="icon" aria-hidden="true"><svg') == len(icons)
    contents = re.findall(r'content:\s*("[^"]*")', html)
    assert set(contents) <= {'""', '" / "'}, contents


# ------------------------------------------------------------------------- the PDF


needs_pango = pytest.mark.skipif(
    find_library("pango-1.0") is None,
    reason="Pango is not installed here, and WeasyPrint draws with it",
)


def outside(page) -> list:
    """Everything laid out past either side of the page's printable area.

    Postulo's own measurement (`tests/test_pdf_render.py` in the core), taken at both
    edges, because a right-to-left document runs off on the left. The page number sits in a
    margin box, which is in the margin on purpose and is not measured.
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


@needs_pango
def test_the_pdf_draws_within_the_page_and_fetches_nothing(cv, caplog):
    document = WeasyPrintBackend().document(render_cv_html(cv)).render()

    assert document.pages, "nothing was drawn"
    assert not any(outside(page) for page in document.pages)
    assert "Failed to load" not in caplog.text, "the theme asked for something outside itself"


@needs_pango
def test_an_arabic_pdf_draws_within_the_page(person):
    cv = CV.objects.create(
        owner=person, name="سيرة", theme="europass", language="ar", summary="عشر سنوات"
    )
    on_the_cv(cv, LanguageSkill.objects.create(owner=person, name="العربية", proficiency="native"))

    document = WeasyPrintBackend().document(render_cv_html(cv)).render()

    assert len(document.pages) == 1
    assert not outside(document.pages[0])


@needs_pango
def test_the_pdf_carries_a_tag_tree_and_its_language(cv):
    content = (
        WeasyPrintBackend()
        .document(render_cv_html(cv))
        .write_pdf(**pdf_options.WEASYPRINT_PDF_OPTIONS, uncompressed_pdf=True)
    )

    assert b"/StructTreeRoot" in content
    assert b"/Lang (en-GB)" in content
    assert b"/Title" in content
