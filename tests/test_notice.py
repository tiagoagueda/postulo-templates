"""The NOTICE carries what CC BY 4.0 asks of the Europass-derived theme (postulo-templates#12)."""

from __future__ import annotations

from pathlib import Path

NOTICE = (Path(__file__).resolve().parents[1] / "NOTICE").read_text(encoding="utf-8")


def test_the_notice_credits_the_source_under_cc_by_and_says_what_changed():
    assert "© European Union, 2002-2015" in NOTICE
    assert "europass.cedefop.europa.eu" in NOTICE
    assert "CC BY 4.0" in NOTICE
    assert "https://creativecommons.org/licenses/by/4.0/" in NOTICE
    assert "https://european-union.europa.eu/legal-notice_en" in NOTICE
    assert "Changes:" in NOTICE


def test_the_notice_says_logos_and_names_are_not_licensed_nor_used_nor_endorsed():
    assert "not licensed" in NOTICE
    assert "ships no Europass or European Union logo" in NOTICE
    assert "not affiliated with, endorsed by or sponsored by" in NOTICE
