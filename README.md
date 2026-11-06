My [beets](https://beets.io/) configuration.

## Installation

```
./setup.sh
```

This clones the needed plugin sources into `~/code/music`, then installs
`beet` as a [uv](https://docs.astral.sh/uv/) tool: a pinned beets release
from PyPI, plus editable installs of ctrpaths and the third-party plugins.

To upgrade beets, back up `config/library.db` first (new versions may migrate
the database schema), bump `beets_version` in `setup.sh`, then:

```
uv tool uninstall beets && ./setup.sh
```

## My flexible attributes

- category: Primary directory override
- subcategory: Secondary directory override
- subtitle: disambiguating string after title, in brackets
- prefix: string at beginning of filename, in brackets

For soundtracks:
- avmedia: Animation, TV, Video Games, Musicals, Movies
- franchise: Final Fantasy

For world music:
- nationality: Japanese

For holiday music:
- holiday: Halloween

Naming schemes:
- `A Cappella/<artist>/...`
- `Anthems/<subcategory>/...`
- `Artists/<artist>/...`
- `Children/<subcategory>/...`
- `Classical/<composer>/...`
- `Comedy/<artist>/...`
- `Covers/<title>/...`
- `Crap/<artist>/...`
- `Holidays/<holiday>/...`
- `Meditation/<artist>/...`
- `Soundtracks/<franchise>/...`

See `ctrpaths` logic for full details.

## Import examples

```
beet import -s --set=category=Soundtracks --set=avmedia='Video Games' --set=franchise='Final Fantasy' Due-Recompense.opus
```

## FAQ

### A track or album ended up in the wrong place. How do I fix it?

Set the fields that drive `ctrpaths`, and beets moves the files to match:

```
beet modify -a album:'Final Fantasy VI' category=Soundtracks avmedia='Video Games' franchise='Final Fantasy'
```

Use `-a` for album-level fields (as set by `beet import --set`), or omit it to
change individual tracks. `beet modify` moves files by default (since
`import.move` is on); pass `-M` to skip that, and run `beet move <query>`
later. To preview what would move without moving anything, use
`beet move -p <query>`.

### A track has wrong metadata. How do I fix it?

- To refresh from the source it was tagged from, run `beet mbsync <query>`;
  it uses each item's `data_source` (MusicBrainz, Spotify, ...).
- To match it to a different release, run `beet import -L <query>` and pick
  (or enter the ID of) the right one. Note that this replaces the album and
  items in the library: their beets IDs change, though the `added` date and
  flexible attributes are kept.
- For one-off fixes, `beet modify <query> field=value`, or `beet edit
  <query>` to edit in a text editor.

Then `beet write <query>` to write the changes to the files' tags.

### How are non-ASCII names transliterated for paths?

With `asciify_paths: yes`, beets transliterates paths with `unidecode`.
Before that, ctrpaths (`_translit` in `ctrpaths/__init__.py`):

1. Applies the overrides in the `ctrpaths: romaji:` section of `config.yaml`,
   which map original text to its Latin form. Use these to fix anything
   that comes out wrong, in names or titles.
2. For artist names, uses Latin names from MusicBrainz (English aliases or
   sort names): 矢井田瞳 -> `Hitomi Yaida`. The `romaji` plugin
   (`beetsplug/romaji.py`) fetches these into `config/romaji-names.json`
   automatically on import; run `beet romaji` to fetch any that are missing
   (e.g. after rebuilding the setup), or `beet romaji -f <query>` to refresh.
3. For album and track titles, uses Latin titles from MusicBrainz
   pseudo-releases: 硝子の夢 -> `Dream of Glass` (English translation) or
   `Glass no Yume` (romaji). The `romaji` plugin stores these in the
   database as `album_transl` and `title_transl` (the names the built-in
   `mbpseudo` plugin uses), and records the pseudo-release used in
   `transl_release` (`none` if there is none), at the same times as
   artist names. The `romaji:` section of `config.yaml` sets which kind
   wins: `prefer: translation` (in the `languages` listed) or
   `transliteration`. Each title falls back to the next pseudo-release that
   has it, and then to the steps below. See `ctrpaths/titles.py`.
4. Maps symbols that unidecode drops or mangles to readable ASCII:
   ♥ -> `(heart)`, ☆☆ -> `(stars)`, ・ -> `.`, ℗ -> `(P)`, etc. Edit the
   `_TRANSLIT` and `_WORD_SYMBOLS` tables to change these.
5. Romanizes remaining Japanese with cutlet (`ctrpaths/japanese.py`):
   この誰もいない部屋で -> `Kono dare mo inai heya de`. Kanji are read as
   Japanese unless the item's `script`/`language` is Chinese or Korean; to
   fix a misread release, set those fields, e.g.
   `beet modify -a album:… script=Hant language=zho`.

Preview the effect of any change with `beet move -p <query>`.
