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
