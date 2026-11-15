"""The applicant-tracking theme: a page a parser reads, and in the order a person does."""

from __future__ import annotations

import datetime as dt
import io
import re

import pytest
from postulo.documents import themes
from postulo.documents.models import CV, CVKind
from postulo.documents.pdf import WeasyPrintBackend
from postulo.documents.rendering import render_cv_html
from postulo.resume.models import Education, Experience, Project
from pypdf import PdfReader

from .support import on_the_cv
from .test_every_theme import draw, needs_pango

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]

SENTINELS = [
    "Alex Morgan",
    "Test engineer",
    "Ten years of keeping things calm.",
    "Experience",
    "Aperture Science",
    "Kept the turrets calm.",
    "Education",
    "MSc Applied Physics",
]


@pytest.fixture
def cv(person):
    document = CV.objects.create(
        owner=person,
        name="Main",
        theme="ats",
        language="en-GB",
        headline="Test engineer",
        summary="Ten years of keeping things calm.",
    )
    on_the_cv(
        document,
        Experience.objects.create(
            owner=person,
            organisation="Aperture Science",
            role="Test engineer",
            start_date=dt.date(2019, 3, 1),
            highlights="Kept the turrets calm.",
        ),
        Education.objects.create(
            owner=person,
            qualification="MSc Applied Physics",
            institution="University of Porto",
            start_date=dt.date(2012, 9, 1),
            end_date=dt.date(2014, 7, 1),
        ),
    )
    return document


def test_the_theme_sets_a_cv_and_a_portfolio():
    theme = themes.find("ats")
    assert theme.sets(themes.Kind.CV)
    assert theme.sets(themes.Kind.PORTFOLIO)
    assert ("ats", "Applicant tracking, from Postulo Templates") in themes.choices_for(
        themes.Kind.CV
    )


@pytest.mark.parametrize("kind", [themes.Kind.CV, themes.Kind.PORTFOLIO])
def test_the_page_is_one_column_of_real_headings_and_no_pictures(person, kind):
    html = draw(person, "ats", kind)

    assert len(re.findall(r"<h1[ >]", html)) == 1
    assert "<h2" in html
    if kind == themes.Kind.CV:
        assert "<h3" in html, "a job is a heading"
    for refused in ("<img", "<svg", "<table", "<canvas", "@font-face"):
        assert refused not in html
    for refused in ("float:", "grid", "column-count", "position: absolute"):
        assert refused not in html, f"{refused} makes the reading order the renderer's guess"


def test_the_photograph_is_never_drawn(cv):
    """A picture a parser cannot read, which an employer may not want: hidden even where the
    CV chose one."""
    html = render_cv_html(cv)

    assert re.search(r"\.photo\s*\{\s*display:\s*none", html)


def test_a_portfolio_leads_with_its_work(person):
    document = CV.objects.create(
        owner=person, name="Work", theme="ats", language="en-GB", kind=CVKind.PORTFOLIO
    )
    on_the_cv(
        document,
        Project.objects.create(owner=person, name="Turret governor", summary="Keeps them calm."),
    )

    html = render_cv_html(document)

    assert "Turret governor" in html
    assert 'class="piece"' in html


def pdf_text(cv) -> str:
    content = WeasyPrintBackend().document(render_cv_html(cv)).write_pdf()
    return " ".join(page.extract_text() for page in PdfReader(io.BytesIO(content)).pages)


@needs_pango
def test_the_pdf_yields_its_text_in_reading_order(cv):
    """What an applicant tracking system gets from the file: the words, in the order the
    document says them, with none lost and none doubled."""
    text = re.sub(r"\s+", " ", pdf_text(cv))

    found = [text.index(word) for word in SENTINELS]
    assert found == sorted(found), text
    assert text.count("Aperture Science") == 1
