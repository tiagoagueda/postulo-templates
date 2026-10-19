"""The workflows install uv from a pinned, checksummed installer and audit the lock (#15)."""

from pathlib import Path

import pytest

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"


@pytest.mark.parametrize("workflow", sorted(WORKFLOWS.glob("*.yml")), ids=lambda p: p.name)
def test_uv_is_installed_from_a_versioned_installer_whose_checksum_is_checked(workflow):
    text = workflow.read_text(encoding="utf-8")
    assert "astral.sh/uv/install.sh" not in text, "an unversioned address answers whatever it likes"
    if "astral.sh/uv/" in text:
        assert "https://astral.sh/uv/${UV_VERSION}/install.sh" in text
        assert 'echo "${UV_INSTALLER_SHA256}  /tmp/uv-install.sh" | sha256sum -c -' in text
        assert "| sh" not in text, "the installer is checked, then run; never piped"


def test_the_lock_is_audited_on_a_schedule():
    text = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "schedule:" in text and "cron:" in text
    assert "pip-audit==" in text and "pip-audit --strict" in text
