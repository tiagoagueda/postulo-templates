"""The plugin Postulo loads, and the themes it brings.

A feature plugin rather than a kind of its own, because a theme is a declaration and not a
service: the plugin is not asked to do anything, only to say which themes it has. Switching
it off takes every theme with it (Postulo has no switch per theme), and a document set in
one of them falls back to Postulo's `plain` rather than failing to export.

**A theme's name is first come, first served across the instance**, and Postulo refuses one
already taken, its own `plain` and `classic` included. The names here are plain family
names, the same for a CV and the letter that goes with it, so that two documents sent
together can be set in one family.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from postulo.plugins.api import Theme, ThemeKind

from . import __version__

#: Who provides these themes, as the picker says it: "Europass layout, from Postulo Templates".
PROVIDER = _("Postulo Templates")

#: A CV laid out as the Europass CV is: a column of labels and dates, the content beside it.
EUROPASS = Theme(
    name="europass",
    # "Europass layout", not plain "Europass": core ships an importer that reads Europass files,
    # labelled "Europass import", and the same word for both left people unable to tell them
    # apart. The name stays "europass", because stored documents record it (postulo/postulo#911).
    label=_("Europass layout"),
    templates={ThemeKind.CV: "postulo_templates/europass/cv.html"},
    provider=PROVIDER,
)


class Templates:
    """Postulo's official document templates."""

    name = "templates"
    version = __version__
    kind = "feature"
    label = _("Document templates")
    description = _(
        "More themes to set a CV in, beside Postulo's own: a CV laid out as the Europass CV "
        "is. Switched off, the themes are no longer offered, and a document set in one of "
        "them is drawn in the plain theme until it is switched on again."
    )
    themes = (EUROPASS,)
