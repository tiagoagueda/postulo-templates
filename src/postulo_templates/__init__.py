"""postulo-templates: the official document templates for Postulo, as a plugin.

Postulo sets a document in a theme, and a theme reaches the renderer through one door: an
installed plugin that declares it (postulo/postulo#132). This package is that plugin. It
declares its themes in :mod:`.plugin`, and Postulo finds the markup in the ``templates/``
directory beside this file when it loads the plugin.

A theme shapes the PDF and the preview, and nothing else: the Word and plain-text exports
are built from the document's outline and never see one.

Every string a theme prints is translated by this package itself, from ``locale/`` next to
this file; Postulo never carries a plugin's words.
"""

from importlib import metadata

#: One version, kept in `pyproject.toml` and read back from the installed distribution.
try:
    __version__ = metadata.version("postulo-templates")
except metadata.PackageNotFoundError:  # pragma: no cover - only outside an installation
    __version__ = "0.0.0+unknown"
