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
