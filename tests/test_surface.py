"""This plugin imports `postulo.plugins.api`, and nothing else from Postulo.

`postulo.plugins.api` is a promise: those names keep working across a minor release. The
rest of Postulo is internals that may be renamed in a patch release, so a plugin importing
them breaks on somebody else's Tuesday. The check is Postulo's own, imported rather than
copied. Only `src/` is measured; the tests may reach into Postulo to set a world up.
"""

from __future__ import annotations

from pathlib import Path

from postulo.plugins.testing import SURFACE, assert_imports_only_the_surface, imports_of

PACKAGE = "postulo_templates"
SOURCE = Path(__file__).resolve().parents[1] / "src" / PACKAGE


def test_there_is_something_to_check():
    """A sanity check on the check: an empty package would make everything below pass."""
    assert len(list(SOURCE.rglob("*.py"))) >= 2


def test_the_plugin_imports_only_the_surface():
    assert_imports_only_the_surface(SOURCE, package=PACKAGE)


def test_the_surface_is_what_this_plugin_actually_uses():
    """The other half: the surface is imported, rather than merely not reached past."""
    found = imports_of(SOURCE, package=PACKAGE)
    assert found, "the package imports nothing from Postulo"
    # By name since postulo/postulo 12504e44f: `postulo.plugins.api.FieldSpec`, not the module.
    assert all(name == SURFACE or name.startswith(SURFACE + ".") for name in found), found
