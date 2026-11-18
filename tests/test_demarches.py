"""The job-search report laid out for France Travail (postulo/postulo#1262).

The person's own list of the period's applications and interviews, in the two groups France
Travail's tool for recording steps uses; never an official form, never another person's
name, and drawn on a Postulo that hands the interviews and the method and on one that does not.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.template.loader import render_to_string
from postulo.documents import themes

from .support import a_report
from .test_europass import text_of

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]

TEMPLATE = "postulo_templates/demarches/report.html"


def context(**more) -> dict:
    """A report's context as Postulo hands it, with the names #1262 added when ``more`` has
    them: two applications, one with a method and a place and one without."""
    rows = [
        {
            "applied_on": dt.date(2026, 3, 2),
            "company": "Aperture Science",
            "role": "Test engineer",
            "source": "A job board",
            "url": "",
            "status": "Applied",
            "last_activity_on": dt.date(2026, 3, 2),
        },
        {
            "applied_on": dt.date(2026, 3, 5),
            "company": "Black Mesa",
            "role": "Physicist",
            "source": "",
            "url": "",
            "status": "Interview",
            "last_activity_on": None,
        },
    ]
    if "interviews" in more:
        rows[0].update(channel="Email", channel_key="email", location="Lyon")
        rows[1].update(channel="", channel_key="", location="")
    return {
        "document_language": "en-GB",
        "document_direction": "ltr",
        "document_title": "Report",
        "csp_nonce": "",
        "person": "Alex Morgan",
        "office": "Agence de Lyon",
        "adviser": "",
        "produced_at": dt.datetime(2026, 4, 1, 9, 0, tzinfo=dt.UTC),
        "period": {
            "label": "March 2026",
            "start": dt.date(2026, 3, 1),
            "end": dt.date(2026, 3, 31),
        },
        "total": 2,
        "through_service": 0,
        "appointments_attended": 1,
        "happened": {"replies": 1, "interviews": 1, "offers": 0, "rejections": 0},
        "cadence": {"per_week": 0.5, "empty_weeks": 2},
        "evidence": rows,
        **more,
    }


def test_the_plugin_offers_it_for_the_report_and_names_the_country():
    theme = themes.find("demarches")

    assert theme is not None, "the entry point did not register the theme"
    assert set(theme.templates) == {themes.Kind.REPORT}
    assert "(France)" in str(theme.label), "the label says whose office it is laid out for"


def test_every_application_is_a_row_under_the_offices_headings(person):
    shown = text_of(a_report(person, "demarches"))

    assert "Record of job-search steps" in shown
    for heading in ("Date", "Employer and place", "Position", "Result"):
        assert heading in shown
    assert shown.count("Test engineer") == 30, "one row per application sent"


def test_what_postulo_does_not_hold_is_left_for_the_pen(person):
    html = a_report(person, "demarches")

    assert '<dt>France Travail identifier</dt><dd class="blank"></dd>' in html
    for caption in ("Signed at", "Date", "Signature"):
        assert f'<div class="label">{caption}</div>' in html


def test_it_says_it_is_the_persons_own_list_and_carries_no_mark(person):
    html = a_report(person, "demarches")

    assert "not a France Travail form" in text_of(html)
    assert "<img" not in html
    assert "<svg" not in html


def test_nobody_elses_name_is_printed(person):
    """Who referred the person is their own business and another person's name (#239)."""
    from postulo.applications.models import Application
    from postulo.jobs.models import Contact

    a_report(person, "demarches")  # the applications
    referrer = Contact.objects.create(owner=person, name="Pat Referrer")
    Application.objects.filter(owner=person).update(referred_by=referrer)

    from postulo.applications import reports

    _report, html, _theme, _language = reports.draw(
        person, reports.month_period(2026, 3), theme="demarches", language="en-GB"
    )
    assert "Pat Referrer" not in html


def test_without_the_interviews_and_the_method_the_page_leaves_them_out():
    """A Postulo before #1262 hands neither: no empty column, no empty table."""
    shown = text_of(render_to_string(TEMPLATE, context()))

    assert "Black Mesa" in shown
    assert "How" not in shown
    assert "Job interviews" not in shown


def test_with_them_each_row_says_how_and_where_and_the_interviews_follow():
    interviews = [{"on": dt.date(2026, 3, 20), "company": "Initech", "role": "Analyst", "kind": ""}]
    shown = text_of(render_to_string(TEMPLATE, context(interviews=interviews)))

    assert "How" in shown
    assert "Aperture Science Lyon" in shown, "the place sits under the employer"
    assert "Email" in shown
    assert "Job interviews" in shown
    assert "Initech Analyst —" in shown, "an interview of no kind says so with a dash"


def test_a_period_with_no_interview_says_so():
    shown = text_of(render_to_string(TEMPLATE, context(interviews=[])))

    assert "No interview in this period." in shown
