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
