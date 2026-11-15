"""Every word a template writes is marked for translation, and is drawn in the document's own
language, not the reader's (postulo/postulo#7).

Section titles, dates and the language names come from Postulo already written in the
document's language; a template translates only the words it adds, and those come from this
plugin's catalogues. These hold that: no visible English word sits in a template unmarked,
the CSS uses logical properties so one template serves both directions, and a word that has a
translation is drawn translated. That every string has one in each European Union language
before a tag is the release gate (`uv run pytest -m release`, `test_catalogues.py`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from postulo.core import messages_tool
from postulo.documents import themes

from postulo_templates.plugin import Templates

from .test_every_theme import draw

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = sorted((REPO / "src" / "postulo_templates" / "templates").rglob("*"))
TEMPLATES = [path for path in TEMPLATES if path.is_file()]


def words_a_reader_sees(source: str) -> str:
    """What is left of a template once everything that is not a bare word is taken out: the
    comments, the stylesheet, the drawings, every tag of the template language and of HTML.
    What `translate` and `blocktranslate` write is translated, so they go too; what a
    variable prints is the person's own or already in the document's language."""
    for pattern in (
        # A theme that extends Postulo's page writes its whole stylesheet in this block.
        r"\{%\s*block page_styles\s*%\}.*?\{%\s*endblock\s*%\}",
        r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
        r"\{%\s*blocktranslate.*?%\}.*?\{%\s*endblocktranslate\s*%\}",
        r"\{%\s*translate.*?%\}",
        r"\{#.*?#\}",
        r"<style\b.*?</style>",
        r"<svg\b.*?</svg>",
        r"\{%.*?%\}",
        r"\{\{.*?\}\}",
        r"<[^>]+>",
    ):
        source = re.sub(pattern, " ", source, flags=re.DOTALL)
    return source


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda path: path.relative_to(REPO).as_posix())
def test_no_visible_word_is_left_out_of_translation(path):
    if path.suffix != ".html":
        pytest.skip("not a template")
    left = re.findall(r"[^\W\d_]{2,}", words_a_reader_sees(path.read_text(encoding="utf-8")))
    assert left == [], f"{path.name}: words not marked for translation: {left}"


#: A physical side in a stylesheet. A direction-aware template says start and end, so one
#: template serves left-to-right and right-to-left languages; the few places where a
#: position must be a side are mirrored in the template, which is what the exemptions are.
PHYSICAL = re.compile(
    r"(?:margin|padding|border)-(?:left|right)\b"
    r"|text-align:\s*(?:left|right)\b"
    r"|float:\s*(?:left|right)\b"
    r"|(?<![-\w])(?:left|right):[ \t]*(?![ \t]|auto\b|0\b)"
)


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda path: path.relative_to(REPO).as_posix())
def test_the_css_uses_logical_properties(path):
    if path.suffix not in {".html", ".css"}:
        pytest.skip("no stylesheet")
    found = PHYSICAL.findall(path.read_text(encoding="utf-8"))
    assert found == [], f"{path.name}: use start/end, not a physical side: {found}"


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda path: path.relative_to(REPO).as_posix())
def test_a_side_that_is_set_by_hand_is_mirrored_for_right_to_left(path):
    """`right: 0` or `left: 0` is allowed only in a template that says what it does in a
    right-to-left document."""
    if path.suffix != ".html":
        pytest.skip("not a template")
    source = path.read_text(encoding="utf-8")
    if re.search(r"(?<![-\w])(?:left|right):\s*0\b", source):
        assert '[dir="rtl"]' in source, f"{path.name} places something by side and never mirrors it"


@pytest.fixture(scope="module")
def tool():
    messages_tool.use(REPO)
    return messages_tool


def translated(tool, code: str) -> dict[str, str]:
    catalogue = tool.parse(tool.po_path(code).read_text(encoding="utf-8"))
    return {m.msgid: m.msgstr[0] for m in catalogue.messages.values() if m.translated}


@pytest.mark.django_db
@pytest.mark.usefixtures("installed")
@pytest.mark.parametrize("code", ["fr-FR", "pt-PT"])
@pytest.mark.parametrize(
    ("name", "kind"), [(t.name, k) for t in Templates.themes for k in t.templates]
)
def test_a_word_with_a_translation_is_drawn_translated(person, tool, code, name, kind):
    """No English word of the template's own where its language has the word.

    Only for strings that have a translation: one nobody has translated yet is drawn in
    English by design (it arrives from Weblate), and the release gate is what demands it.
    """
    from .test_europass import text_of

    html = draw(person, name, kind, language=code)
    shown = text_of(html)
    own = {
        msgid: msgstr
        for msgid, msgstr in translated(tool, code).items()
        if msgstr != msgid and not msgid.startswith("More themes") and len(msgid) < 80
    }
    drawn_in_english = [
        msgid for msgid in own if re.search(rf"(?<!\w){re.escape(msgid)}(?!\w)", shown)
    ]
    assert drawn_in_english == []


@pytest.mark.django_db
@pytest.mark.usefixtures("installed")
def test_dates_follow_the_documents_language(person):
    """A date is written by Postulo from the document's language, whatever the reader's."""
    from .test_europass import text_of

    french = text_of(draw(person, "europass", themes.Kind.CV, language="fr-FR"))

    assert "mars 2019" in french
    assert "March 2019" not in french
