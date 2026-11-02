Some tracks are publicly available on YouTube and/or Spotify.

I'd like to glean/remember the YouTube ID somehow, either in ID3 tags, beets DB, or both. Same for Spotify tracks and potentially other services. Knowing these links is very helpful for assembling shareable playlists on whatever service(s) happen to have access to all/most tracks of a given local playlist.

It would also be cool to glean some metadata (title, artist, album, year?) from such remote services, e.g. infer the YouTube video description. Relatedly: how does YouTube Music relate to YouTube in general? Does YouTube Music have more metadata? Is it publicly/freely accessible?

See also `items-only-have-one-data-source.md`.

## Status (beets 2.14)

* Album-level Spotify/Discogs/Bandcamp/Deezer/Beatport/Tidal IDs are now
  recorded from MusicBrainz URL relations (the musicbrainz plugin's
  `external_ids` option, enabled in `config.yaml`) on import and
  `beet mbsync`. Existing albums get them on their next mbsync.
* Spotify-tagged items have `spotify_track_id`. Nothing records YouTube IDs.
