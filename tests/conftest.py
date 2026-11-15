"""What every test here starts from: the plugin loaded as Postulo loads it, and a person."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from postulo.documents import themes
from postulo.plugins import registry


@pytest.fixture
def installed(settings):
    """The plugin loaded the way Postulo loads it at start-up, and forgotten afterwards."""
    settings.TEMPLATES = [{**settings.TEMPLATES[0], "DIRS": list(settings.TEMPLATES[0]["DIRS"])}]
    registry._cache.clear()
    registry.plugins("feature", refresh=True)
    yield
    themes.forget()
    registry._cache.clear()


@pytest.fixture
def person():
    user = get_user_model().objects.create_user(
        email="alex@example.org",
        password="not-a-real-password",  # noqa: S106
    )
    user.first_name, user.last_name = "Alex", "Morgan"
    user.save()
    return user
