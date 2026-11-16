"""Helpers the test files share."""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from postulo.documents.models import CVItem


def on_the_cv(cv, *entries) -> None:
    for order, entry in enumerate(entries):
        CVItem.objects.create(
            owner=cv.owner,
            cv=cv,
            content_type=ContentType.objects.get_for_model(entry),
            object_id=entry.pk,
            order=order,
        )


#: A line with nowhere to wrap, which is what finds a column measured for one paper only.
LONG_ADDRESS = "https://example.org/" + "a" * 180


def sent_applications(person, count: int = 30) -> None:
    """``count`` applications sent in March 2026, the first with a long address: more than a
    page of evidence, and one line that cannot break."""
    import datetime as dt

    from django.utils import timezone
    from postulo.applications.models import Application, Status
    from postulo.applications.services import change_status
    from postulo.jobs.models import Company, JobPosting

    for number in range(count):
        firm, _made = Company.objects.get_or_create(owner=person, name=f"Aperture {number % 7}")
        posting = JobPosting.objects.create(
            owner=person,
            company=firm,
            title="Test engineer",
            source="A job board",
            url=LONG_ADDRESS if number == 0 else "https://example.org/1",
        )
        when = timezone.make_aware(dt.datetime(2026, 3, 1 + number % 28, 10, 0))
        application = Application.objects.create(
            owner=person, posting=posting, status=Status.DRAFT, applied_at=when
        )
        change_status(application, Status.APPLIED, occurred_at=when)
        Application.objects.filter(pk=application.pk).update(applied_at=when)


def a_report(person, theme: str, *, language: str = "en-GB", paper: str = "") -> str:
    """The job-search report for March 2026, drawn the way Postulo draws it."""
    from postulo.applications import reports

    sent_applications(person)
    person.profile.office = "Employment office"
    person.profile.save()
    _report, html, _theme, _language = reports.draw(
        person, reports.month_period(2026, 3), theme=theme, language=language, paper=paper
    )
    return html


def a_list(person, theme: str, *, language: str = "en-GB", paper: str = "") -> str:
    """The companies table in every column it has, one company with a long address."""
    from django.test import RequestFactory
    from postulo.core import list_export, tables
    from postulo.jobs.models import Company
    from postulo.jobs.tables import CompaniesTable

    for number in range(40):
        Company.objects.create(
            owner=person,
            name=f"Aperture {number}",
            website=LONG_ADDRESS if number == 0 else "https://example.org",
            notes="Keeps the turrets calm. " * 12,
        )
    tables.save_settings(person, "companies", {"columns": [c.key for c in CompaniesTable.columns]})
    request = RequestFactory().get("/")
    request.user = person
    html, _theme, _language = list_export.draw(
        request, "companies", theme=theme, language=language, paper=paper
    )
    return html


def a_calendar(
    person, theme: str, *, language: str = "en-GB", paper: str = "", view: str = "month"
) -> str:
    """September 2026, one day holding five reminders, one of them long."""
    import datetime as dt

    from django.test import RequestFactory
    from postulo.applications import calendar_print
    from postulo.applications.models import Reminder

    due = dt.datetime(2026, 9, 15, 9, tzinfo=dt.UTC)
    Reminder.objects.create(owner=person, summary=f"Read {LONG_ADDRESS}", due_at=due)
    for number in range(5):
        Reminder.objects.create(owner=person, summary=f"Chase {number}", due_at=due)
    done = Reminder.objects.create(owner=person, summary="Already done", due_at=due)
    Reminder.objects.filter(pk=done.pk).update(done_at=due)
    asked = {"month": "2026-09"} if view == "month" else {"view": view, "on": "2026-09-15"}
    request = RequestFactory().get("/", asked)
    request.user = person
    html, _theme, _language = calendar_print.draw(
        request, theme=theme, language=language, paper=paper
    )
    return html
