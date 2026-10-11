"""This plugin's own catalogues, held to the rule Postulo holds its own to.

Postulo never translates a plugin's strings, so Postulo's release gate cannot see these;
this is the same gate, here (postulo/postulo#187). English is the source, every translation
is made in Weblate (postulo/postulo#706) and arrives as its pull request, and the twenty-four
European Union catalogues are complete in a published version -- `uv run pytest -m release`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from django.conf import settings

# Imported, not `importorskip`ed. The tool arrived with Postulo 0.3 and the dev group now
# pins the 0.3 core, so a machine where this import fails has the wrong Postulo — which is
# the thing to be told about. Skipping said "no catalogue problems" on a green run that had
# never opened a catalogue.
from postulo.core import messages_tool

REPO = Path(__file__).resolve().parents[1]

#: What a person writes in this repository, as opposed to what a tool makes.
WRITTEN_BY_HAND = {".py", ".md", ".toml", ".yml", ".json", ".html", ".txt"}

#: The twenty-four, minus the source. Complete in a published version, not in every commit.
EUROPEAN_UNION = (
    "bg",
    "cs",
    "da",
    "de",
    "el",
    "es",
    "et",
    "fi",
    "fr-FR",
    "ga",
    "hr",
    "hu",
    "it",
    "lt",
    "lv",
    "mt",
    "nl",
    "pl",
    "pt-PT",
    "ro",
    "sk",
    "sl",
    "sv",
)


@pytest.fixture(scope="module")
def tool():
    messages_tool.use(REPO)
    return messages_tool


def missing(tool, code: str) -> list[str]:
    catalogue = tool.parse(tool.po_path(code).read_text(encoding="utf-8"))
    return [m.msgid for m in catalogue.messages.values() if not m.translated]


def test_the_catalogues_are_current(tool):
    assert tool.cmd_extract(check=True) == 0, "run `uv run postulo-messages extract`"


def test_placeholders_and_plural_forms_agree(tool):
    assert tool.cmd_check() == 0


def test_every_language_postulo_offers_has_a_catalogue(tool):
    absent = [code for code in tool.translated_languages() if not tool.po_path(code).is_file()]
    assert absent == [], "run `uv run postulo-messages extract`"


@pytest.mark.release
@pytest.mark.parametrize("code", EUROPEAN_UNION)
def test_every_european_union_language_stays_complete(tool, code):
    gaps = missing(tool, code)
    assert gaps == [], f"{code}: {len(gaps)} untranslated, e.g. {gaps[:3]}"


def test_a_language_code_is_written_one_way():
    """`fr-FR` wherever a code is written here, the way Postulo writes one.

    The catalogue tool refuses a catalogue asked for in another spelling. Nothing would
    notice one anywhere else, so this reads the files: no code Postulo offers with a region
    or a script in it may appear in lower case. The directories under `locale/` are
    gettext's names for a catalogue (`fr_FR`), not codes, and are not read.
    """
    otherwise = sorted(code.lower() for code, _name in settings.LANGUAGES if "-" in code)
    assert otherwise, "Postulo offers no code with a region in it, so this would hold nothing"

    read = [REPO / "README.md", REPO / "pyproject.toml"]
    for folder in ("src", "tests", ".forgejo"):
        read += [
            path
            for path in sorted((REPO / folder).rglob("*"))
            if path.suffix in WRITTEN_BY_HAND and "locale" not in path.parts
        ]
    found = [
        f"{path.relative_to(REPO).as_posix()}: {spelling}"
        for path in read
        for spelling in otherwise
        if spelling in path.read_text(encoding="utf-8")
    ]
    assert found == []
