When I set up Beets, the plugins that kept track of your non-music companion files (art assets, textual notes, etc.) did not work well. For example, the `copyartifacts` plugin had a horrible bug that corrupted part of my collection. I remember trying at least one other plugin and finding it lacking. Now that beets is more mature, it would be good to finally solve this issue:

* How can I ensure that `beet import <some-directory>` moves the non-music files from that directory into the ultimate destination directory?
* How can I ensure that commands like `beet move` don't leave my non-music files behind?
* How can I ensure that files don't disappear into `/dev/null`?

## Status (November 2026)

beets still has no built-in support. Its maintained plugin is
[beets-filetote](https://github.com/gtronset/beets-filetote) 1.3.7, the
successor to copyartifacts; it is now installed (`setup.sh`) and enabled
(`config.yaml`).

Evaluated on a scratch library with copies of real albums (all passed):
* import: paired `.lrc` files, a `C_scan-*/` subfolder (kept as a
  subfolder), cue/log files and loose txt/jpg files all came along.
  `album.nfo` was excluded, as configured.
* `beet modify` of an album field that changes the path (year, category),
  and `beet move` after a path-format change: every file followed, and
  the old folders were removed.
* singletons: renaming one renamed its paired `.lrc`; other loose files in
  the shared artist folder stayed put.
* Jellyfin's `album.nfo`/`artist.nfo` are listed under `clutter`, so beets
  deletes them and prunes the folder once the music has moved out.
  Jellyfin regenerates them at the new location.

Why: the 2026-11-02 `beet move` (2,921 tracks, before filetote) left
companion files behind in 125 old folders. They were moved by hand (215
files; 167 identical `.lrc` copies and 44 stale `album.nfo` deleted); the log
is in `.local/move-2026-11-02-companion-files.tsv`.

Remaining: confirm on the next real import, then close this issue. Not
covered: `beet remove -d` leaves companion files behind.
