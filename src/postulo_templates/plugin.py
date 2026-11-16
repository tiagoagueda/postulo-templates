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
    # The portfolio is drawn by the same page: Postulo puts its projects first, and the
    # masthead says which of the two it is.
    templates={
        ThemeKind.CV: "postulo_templates/europass/cv.html",
        ThemeKind.PORTFOLIO: "postulo_templates/europass/cv.html",
        ThemeKind.LETTER: "postulo_templates/europass/letter.html",
        ThemeKind.REPORT: "postulo_templates/europass/report.html",
        ThemeKind.LIST: "postulo_templates/europass/list.html",
    },
    provider=PROVIDER,
    # Fluid: a 45 mm column of labels and the rest for the content, margins in millimetres
    # and nothing measured against A4's 210. Every paper in the tests keeps it so.
    papers=("any",),
    # The scripts the shipped font draws, by ISO 15924. A document in another script is set
    # in the server's fonts instead, and Postulo leaves this one out (postulo/postulo#343).
    font_scripts={"assets/fonts/Arimo-Regular.woff2": ("Latn", "Grek", "Cyrl")},
)


#: A CV an applicant tracking system reads cleanly: one column, real headings, no text in
#: pictures, system fonts. Fluid, with a margin and nothing else measured in millimetres.
ATS = Theme(
    name="ats",
    label=_("Applicant tracking"),
    templates={
        ThemeKind.CV: "postulo_templates/ats/cv.html",
        ThemeKind.PORTFOLIO: "postulo_templates/ats/portfolio.html",
        ThemeKind.LETTER: "postulo_templates/ats/letter.html",
        ThemeKind.REPORT: "postulo_templates/ats/report.html",
        ThemeKind.LIST: "postulo_templates/ats/list.html",
    },
    provider=PROVIDER,
    papers=("any",),
)

#: The job-search report made for handing to an employment service (#4): the person, the
#: office and the adviser first, every application of the period in a table, then a line for
#: the date and one for a signature. It sets the report and nothing else.
HANDOVER = Theme(
    name="handover",
    label=_("Hand-over report"),
    templates={ThemeKind.REPORT: "postulo_templates/handover/report.html"},
    provider=PROVIDER,
    papers=("any",),
)

#: A list for few columns and long text (#5): each row a block, so a note takes the width of
#: the page instead of a narrow column. The table for every other list is in the families.
RECORDS = Theme(
    name="records",
    label=_("Records list"),
    templates={ThemeKind.LIST: "postulo_templates/records/list.html"},
    provider=PROVIDER,
    papers=("any",),
)


class Templates:
    """Postulo's official document templates."""

    name = "templates"
    version = __version__
    kind = "feature"
    label = _("Document templates")
    description = _(
        "More themes to set a CV or a portfolio in, beside Postulo's own: one a hiring "
        "system reads cleanly and one laid out as the Europass CV is. Switched off, the "
        "themes are no longer offered, and a document set in one of them is drawn in the "
        "plain theme until it is switched on again."
    )
    themes = (EUROPASS, ATS, HANDOVER, RECORDS)
