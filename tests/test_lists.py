"""The exported lists (postulo/postulo#5): every row, and the columns the person chose."""

from __future__ import annotations

import pytest
from postulo.documents import themes

from .support import a_list

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("installed")]


@pytest.mark.parametrize("name", ["ats", "europass", "records"])
def test_every_row_of_the_list_is_drawn(person, name):
    html = a_list(person, name)

    assert all(f"Aperture {number}<" in html for number in range(40))


@pytest.mark.parametrize("name", ["ats", "europass"])
def test_a_table_repeats_its_headings_and_keeps_a_row_whole(person, name):
    html = a_list(person, name)

    assert "<thead>" in html
    assert "display: table-header-group" in html
    assert "break-inside: avoid" in html


def test_a_record_names_each_value_by_its_column(person):
    html = a_list(person, "records")

    assert "<dt><bdi>Website</bdi></dt>" in html
    assert "Keeps the turrets calm." in html


def test_the_lists_are_offered_with_this_plugin_as_its_provider():
    offered = dict(themes.choices_for(themes.Kind.LIST))

    assert {"ats", "europass", "records"} <= set(offered)
    assert offered["records"].endswith(", from Postulo Templates")
