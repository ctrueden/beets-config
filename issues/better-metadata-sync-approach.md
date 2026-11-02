The `beet mbsync` command syncs metadata from MusicBrainz.

In case the metadata source was Spotify, the `beet spotifysync` command syncs it from there.

The `beet import -L` command does a more thorough job (see also handle-genres-better.md), running through various import-time steps/plugins and refreshing the database entry...

But I want to sync *more generally*, pulling metadata from *all* linked sources (see also items-only-have-one-data-source.md) and refreshing the metadata accordingly.

* How do we mark a given field as manually overridden, so that it stops getting stomped on (see also handle-genres-better.md)?

* In case of conflict between sources, how do we decide which one wins? Prompt the user? Then remember the choice for that track?

* Finally, tangentially, I noticed that running `beet import -L` causes the `album_id` of an updated track to change... that seems bad! Is beets creating a new album ID? What happened to the old album ID? This might need to be split out into a separate issue...

## Status (beets 2.14)

* On the `album_id` question: this is by design. `beet import -L` removes
  the old album and items from the library and adds new ones, so both
  album and item IDs change. It carries over the `added` date and flexible
  attributes (except source-specific IDs that the new match provides, like
  `spotify_album_id`). Paths, and hence playlists, are unaffected, but
  anything that remembers beets IDs (e.g. Beetle URLs) goes stale.
* The genre half of "stomped on" is addressed: MusicBrainz genres are now
  disabled (`musicbrainz.genres: no`), so `beet mbsync` no longer replaces
  whatlastgenre's genres. See handle-genres-better.md.
* Still no general mechanism to mark a field as manually overridden.
