# Upstream bug reports and PRs to file

Found while upgrading to beets 2.14.1 (November 2026). Line numbers are for
beets master at 27e390ce9. None of these had an existing issue when checked.

## beets

### 1. inline: item fields can't see album-level values (one-line fix)

`beetsplug/inline.py`, `_dict_for()` (line ~103):

```python
for key in obj.keys(computed=False):
    ...
    out[key] = obj._get(key)
```

For an item, `obj.keys()` includes the album's field names, but `_get()` reads
only the item's own fields, so album-only attributes (e.g. a flexible attribute
set with `beet modify -a category=Classical`) come through as `None`. The fix is
`obj.get(key)`, which falls back to the album.

Repro: set an album-only flexible attribute, use it in an item-level inline
field, and run `beet ls -f '$myfield'` on the album's tracks. It prints nothing.

Workaround here: ctrpaths takes `db_obj` (inline passes it since 2.10) and calls
`obj.get()` itself.

### 2. Upgrade from pre-2.7 to 2.13+ loses the instrumental-lyrics flag

`beets/library/migrations.py`:

- `LyricsMetadataInFlexFieldsMigration` (2.7) parses each lyric with
  `Lyrics.from_legacy_text()`. `Lyrics.__post_init__` calls
  `handle_instrumental()`, which turns the text `[Instrumental]` into
  `text=""` and `instrumental=True`. The migration then writes `full_text`
  (now empty) back to the table. Its `lyr_fields` list is backend, url,
  language and translation_language, so `instrumental` is never stored.
- `InstrumentalLyricsInFlexFieldMigration` (2.13) looks for
  `lyrics == '[Instrumental]'`, but those rows are already empty, so nothing is
  flagged.

The result: every instrumental track (1,648 of them here) loses its marker
silently. Fix: include `instrumental` in the 2.7 migration's flex rows (store
`lyrics_instrumental=1` when true). Users who already upgraded can recover the
flags from the `library.db-before-items-lyrics_metadata_in_flex_fields.bak`
backup (that's how I restored them here).

### 3. New built-in fields silently hide custom attributes of the same name

2.11.0 added a built-in `subtitle` field (ID3 `TIT3`, commit 7eadc5e1d). Any
library that already had a flexible attribute called `subtitle` keeps the old
values in `item_attributes`, but beets now reads the new, empty, built-in
column instead. Nothing warns the user, and paths using `$subtitle` change.

Ask for at least one of:
- A changelog note under 2.11.0 that a flexible `subtitle` is now hidden.
- A migration that copies a flexible attribute into a new built-in column of
  the same name when the column is NULL (and removes the flex row).
- A general warning at startup when a flex attribute shadows a fixed field.

Workaround here: copied the 36 values into the built-in field by hand.

### 4. Migrations create `:memory:-before-*.bak` files

`beets/dbcore/db.py`, `Migration._before_migration_backup()` (line ~1065):

```python
dest = os.fsdecode(self.db.path) + f"-before-{table}-{self.name}.bak"
```

For `Library(":memory:")`, this writes 11 files named
`:memory:-before-items-multi_genre_field.bak` etc. to the current directory.
That affects any plugin test or script that uses an in-memory library. Fix:
skip the backup when the path is `:memory:` (or the database is new and has no
rows).

### 5. web: serve embedded album art (feature PR)

`/album/<id>/art` returns 404 when the album has no `artpath`, even though the
tracks have embedded art (common with `embedart` and `fetchart.store_source: no`
or `embedart.remove_art_file: yes`). Our fork branch `ctrueden/beets:qol`
(commit daf968505, "Extract album art on demand from media files") falls back
to the first track's embedded image. Beetle depends on it.

Before filing:
- Detect the MIME type from the image data instead of assuming JPEG.
- Add tests (an album with embedded art and no artpath, and one with neither).
- Add a changelog entry and a note in `docs/plugins/web.rst`.

## whatlastgenre

`plugin/beets/beetsplug/wlg.py` imports `beets.ui.decargs`, which is
deprecated and will be removed in beets 3.0 (line 100:
`lib.albums(decargs(args))` → `lib.albums(args)`). A one-line PR; upstream
merged the `genres` list port in March 2026, so it is still maintained.
