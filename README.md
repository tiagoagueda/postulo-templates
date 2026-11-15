# postulo-templates

The official document templates for [Postulo](https://source.tiagoagueda.com/postulo/postulo),
as a plugin: install it and its themes appear in the theme picker of a CV, beside Postulo's
own *Plain* and *Classic*, each named with this plugin as its provider ("Europass layout, from
Postulo Templates").

A theme shapes the PDF and the preview. The plain-text, OpenDocument and Word exports, and
any format another plugin adds, are built from the document's outline and never see one.

## Install

A template from here reaches an instance the one way Postulo accepts a theme from outside
itself: inside an installed plugin. There is no upload form for a theme and there will not
be one, since a theme is markup Postulo runs.

**From the interface**, as an administrator, under *Server settings → Plugins*. This plugin
is in Postulo's official catalogue: the *Official* repository is listed there already,
switched off; *Switch on* it, press *Check for updates* under *Catalogues*, and *Install*
*postulo-templates*. The signed index and the wheel's checksum are checked before anything
is installed. Or download the wheel from this repository's releases and upload it under
*Install a package*. Either way it is installed on the data volume, not into the image, so
an upgrade of Postulo does not lose it, and its themes are offered at once, without a
restart. A newer release of this plugin over an older one is in use once Postulo has been
restarted, since every process keeps the code it has already loaded.

**By hand**, on an instance you run without a container, into Postulo's environment, then
restart Postulo:

```sh
uv pip install git+https://source.tiagoagueda.com/postulo/postulo-templates.git
```

To bake it into an image of your own instead, see *Plugins* on
[Installing Postulo](https://source.tiagoagueda.com/postulo/postulo/wiki/Installing-Postulo).

Install the release with the same minor version as your Postulo (0.5.x beside Postulo 0.5):
the plugin is released beside the core and tested against that release.

The plugin is a feature: an administrator can switch it off under *Installed on this
instance* on the same page, like any other. Switched off, its themes are no longer
offered, and a document set in one of them is drawn in *Plain* until it is switched on
again. Nothing is deleted, and the same holds if the plugin is removed.

## The themes

| Theme | Sets | Paper | What it is for |
| --- | --- | --- | --- |
| `europass` | CV | Fluid | A CV laid out as the Europass CV is, for applications in Europe that ask for one or where the format is familiar. |

**Paper.** Every theme says which papers it prints on, and the picker offers a document no
other. *Fluid* means every paper Postulo has (A4 and US Letter, each upright or on its side);
a theme drawn for one sheet is *restricted* and names the papers it keeps to, with the reason,
in this table. A fluid theme is drawn on every paper by the tests, and a restricted one on
each it names, and fails if anything runs past the page.

### Europass layout

Drawn from the Europass CV Word template (2013–2019): a narrow column of labels and dates,
right-aligned in dark blue, the content beside it, each section opened by its name and a
thin blue rule ending in a square, Arial throughout. Each entry's dates sit in the label
column, level with its title.

What it prints is what Postulo gives a theme: the contact details the CV chose (each on its
own line, behind a small icon), the photograph if the CV has one, the personal statement,
and every section in the order the CV has them.

What it leaves out of the Word template, on purpose:

- **The Europass logo** and the template's "© European Union" footer. The mark is the
  European Union's; this plugin is not affiliated with Europass, Cedefop or the European
  Commission.
- **The five-skill language grid.** Postulo keeps one level a language. Printing it under
  listening, reading, spoken interaction, spoken production and writing would put five
  claims on a CV that the person made once. A language is printed with its level, and with
  nothing where no level was stated.
- **The "Job applied for" row.** A CV's headline goes under the name.

It is laid out right to left for a right-to-left language, and it is fluid: the label column
is 45 mm and the content takes the rest, so it holds on US Letter and on a page turned on
its side.

## Translations

The words a theme prints ("Personal information", "Mother tongue(s)") are this plugin's
own, in its catalogues under `src/postulo_templates/locale/`. Every translation is made in
Weblate, at <https://translate.tiagoagueda.com/projects/postulo/>, and arrives as its pull
request -- never in a commit, as for the rest of Postulo (postulo/postulo#706). A string
nobody has translated yet is printed in English.

## Developing

```sh
uv sync
uv run postulo-messages compile
uv run pytest
```

The tests run the plugin inside a real Postulo, pinned in the dev group, through the entry
point an instance reads. The PDF tests need Pango and skip where it is missing (most
Windows machines); CI runs them.

A new theme is a `Theme` in `src/postulo_templates/plugin.py` and a template under
`src/postulo_templates/templates/postulo_templates/<name>/`. Its name is first come, first
served across an instance, so it is a plain family name, the same for a CV and the letter
that goes with it.

After changing a string, run `uv run postulo-messages extract` and commit the catalogues
with the change, their slots empty.

## Licence

AGPL-3.0-or-later; see `LICENSE` and `NOTICE`.
