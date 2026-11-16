"""The printed calendar (postulo/postulo#6): every entry, and nothing told apart by colour."""

from __future__ import annotations

import re

import pytest

from .support import a_calendar

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]


@pytest.mark.parametrize("view", ["month", "week", "day", "agenda"])
def test_every_entry_of_the_period_is_drawn_not_the_first_two(person, view):
    html = a_calendar(person, "sheet", view=view)

    assert all(f"Chase {number}" in html for number in range(5))
    assert "Already done" in html


def test_a_finished_entry_is_marked_without_colour(person):
    html = a_calendar(person, "sheet")

    assert 'class="entry kind-reminder over"' in html
    assert "line-through" in html
    assert "2715" in html


def test_no_kind_of_entry_depends_on_colour(person):
    """A black-and-white printer must lose nothing: the stylesheet has no colour but greys."""
    html = a_calendar(person, "sheet")
    css = re.search(r"<style[^>]*>(.*?)</style>", html, re.S).group(1)

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    colours = set(re.findall(r"#[0-9a-fA-F]{3,6}\b", css))
    assert colours
    for colour in colours:
        digits = colour.lstrip("#")
        digits = "".join(c * 2 for c in digits) if len(digits) == 3 else digits
        assert digits[0:2] == digits[2:4] == digits[4:6], f"{colour} is not a grey"


def test_each_kind_has_its_own_rule(person):
    css = re.search(r"<style[^>]*>(.*?)</style>", a_calendar(person, "sheet"), re.S).group(1)
    rules = re.findall(r"\.kind-(\w+) \{ border-inline-start: ([^;]+);", css)

    assert len({shape for _kind, shape in rules}) == len(rules) >= 6
