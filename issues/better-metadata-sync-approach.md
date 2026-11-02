The `beet mbsync` command syncs metadata from MusicBrainz.

In case the metadata source was Spotify, the `beet spotifysync` command syncs it from there.

The `beet import -L` command does a more thorough job (see also handle-genres-better.md), running through various import-time steps/plugins and refreshing the database entry...

But I want to sync *more generally*, pulling metadata from *all* linked sources (see also items-only-have-one-data-source.md) and refreshing the metadata accordingly.

* How do we mark a given field as manually overridden, so that it stops getting stomped on (see also handle-genres-better.md)?

* In case of conflict between sources, how do we decide which one wins? Prompt the user? Then remember the choice for that track?

* Finally, tangentially, I noticed that running `beet import -L` causes the `album_id` of an updated track to change... that seems bad! Is beets creating a new album ID? What happened to the old album ID? This might need to be split out into a separate issue...
