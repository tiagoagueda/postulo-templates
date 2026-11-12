"""The workflows call the shared plugin CI and audit the lock weekly (#15, postulo/postulo#1170).

The pinned, checksummed uv installer (#15) now lives in the shared action, Postulo/plugin-ci,
not in these files; what is left to hold here is that every workflow calls that action by
its full address and that the lock is still audited on a schedule.
"""

import re
from pathlib import Path

import pytest

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"
ACTION = "https://source.tiagoagueda.com/Postulo/plugin-ci@v1"


@pytest.mark.parametrize("workflow", sorted(WORKFLOWS.glob("*.yml")), ids=lambda p: p.name)
def test_every_workflow_runs_the_shared_action_rather_than_its_own_copy(workflow):
    text = workflow.read_text(encoding="utf-8")
    assert "astral.sh" not in text, "uv is installed by the shared action, pinned and checked"
    uses = re.findall(r"^\s*(?:-\s+)?uses:\s*(\S+)", text, re.M)
    assert ACTION in uses
    # A bare `Postulo/plugin-ci` would be looked up on the instance's default actions host.
    assert set(uses) <= {"actions/checkout@v4", ACTION}


@pytest.mark.parametrize("name", ["ci.yml", "release.yml"])
def test_the_subsetter_weasyprint_asks_for_is_installed(name):
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    assert "extra-system-packages: libharfbuzz-subset0" in text


def test_the_lock_is_audited_on_a_schedule():
    text = (WORKFLOWS / "weekly.yml").read_text(encoding="utf-8")
    assert "schedule:" in text and "cron:" in text
    assert "mode: audit" in text
    assert "mode: audit" in (WORKFLOWS / "ci.yml").read_text(encoding="utf-8"), "and every push"
