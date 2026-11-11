# MusicBrainz "writer" credits are ignored

On MusicBrainz, a work's credits can be `composer`, `lyricist` or plain
`writer`. Editors use `writer` when the source doesn't say who wrote the music
and who wrote the words, which is common for pop and rock. beets only reads
the first two (`_parse_work_relations` in `beetsplug/musicbrainz.py`), so
writer-only works get no composers at all.

Example: Barenaked Ladies, "Baby Seat" (recording
bf695f93-5d44-46cb-a255-4d9b414097fc). Its work credits Stephen Duffy and
Steven Page as `writer`, so beets gets no composers for it.

Scale: 27,801 tracks with a MusicBrainz recording ID have no composers
(November 2026). How many of those are writer-only works hasn't been counted.

Checked beetbox/beets for existing issues ("writer", "songwriter", "writer
composer"): none. The nearest is #5698 (storing composer/lyricist MBIDs).

## Ideal fix (upstream PR)

Add an option to treat writers as composers, e.g.:

```yaml
musicbrainz:
  writer_as_composer: no
```

In `_parse_work_relations`, when it is on, add `writer` credits to
`composers` / `composers_ids` / `composer_sort`. Default off, so existing
behavior is unchanged. Needs a test and a changelog entry.

Why this rather than new `writers` / `writers_ids` fields (like Picard's
`WRITER` tag):

* Players and Jellyfin already show composers, so the credits show up
  everywhere straight away. Few players read `WRITER`.
* A separate field would also need a mediafile PR (it has no writer field)
  and a database migration.
* The cost: "composer" becomes slightly inaccurate, since a writer may have
  written the words as well. That is why it should be an option.

Mention separate `writers` fields in the PR as a possible follow-up, if
maintainers prefer it.

## After the fix, here

* Turn the option on and run `beet mbsync -W -p`, then `beet mbsync -W`.
  `-W` updates only the database, so no file mtimes change (no iBroadcast
  re-uploads) and file-only tags survive.
* This fills composers *with artist IDs*, so `beet romanize` can then look up
  their Latin names on MusicBrainz.
* mbsync only changes tracks where MusicBrainz has credits. With the default
  `overwrite_null`, tracks with none keep their current value, including the
  bad splits below.

## Related: bad composer splits from the 2.9 migration

Where the old single `composer` string didn't come from MusicBrainz (e.g.
"Baby Seat" has `Duffy, Stephen & Page, Steven`, probably from the ripper's
Gracenote-style tags), beets kept it on import, since MusicBrainz had no
composer. The 2.9 `MultiComposerFieldMigration` later split it into
`composers` on the first separator found (`"; "`, `", "`, `" / "`), giving
`Duffy` / `Stephen & Page` / `Steven`.

Most of the 5,533 comma-containing strings split correctly. The bad ones:

* "Last, First": `Page, Steven & Robertson, Ed` (11 tracks) and
  `Duffy, Stephen & Page, Steven` (1).
* ", Jr.": about 70 tracks, e.g.
  `Bono, Adam Clayton, The Edge, Larry Mullen, Jr.` (51), where `Jr.`
  becomes a composer of its own. Also Berry Gordy, Jr. and similar.

The legacy `composer` column still holds the original strings, so these can
be repaired in the database only, e.g.:

```
beet modify -W 'composer:Duffy, Stephen & Page, Steven' 'composers=Stephen Duffy; Steven Page'
beet modify -W 'composer:Page, Steven & Robertson, Ed' 'composers=Steven Page; Ed Robertson'
beet modify -W 'composer:Larry Mullen, Jr.' 'composers=Bono; Adam Clayton; The Edge; Larry Mullen, Jr.'
```

Do this after the mbsync above, so it only covers what MusicBrainz didn't fix.
The files still hold the single combined string, so the database and files
differ for these tracks. That is harmless unless they are written (`beet write`
or tag mode's `beet romanize`).
