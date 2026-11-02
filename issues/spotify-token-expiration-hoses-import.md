When importing, the existing Spotify token may be expired, in which case it tries to reauthenticate a few times, but it seems to always fail, and ultimately no Spotify candidates are found.

Example:
```
$ beet -vvvv import -s --timid ~/Desktop/tagged/Gackt/REDEMPTION/01\ REDEMPTION.m4a
user configuration: /home/curtis/.config/beets/config.yaml
data directory: /home/curtis/.config/beets
plugin paths: ['/home/curtis/code/music/beets-ibroadcast/beetsplug']
Loading plugins: artistcountry, discogs, duplicates, edit, embedart, fetchart, fuzzy, ibroadcast, info, inline, lyrics, mbsync, missing, playlist, spotify, the, types, usertag, web, wlg
artresizer: method is ImageMagick
fetchart: google: Disabling art source due to missing key
fetchart: lastfm: Disabling art source due to missing key
inline: adding item field topdir
inline: adding item field subdir_singleton
inline: adding item field safeprefix
inline: adding item field safetitle
inline: adding item field safeartist
inline: adding item field disc_and_track
inline: adding album field topdir
inline: adding album field subdir
inline: adding album field albumdir
Sending event: pluginload
library database: /home/curtis/.config/beets/library.db
library directory: /quark/music
Sending event: library_opened
Sending event: import_begin
Sending event: import_task_created
Sending event: import_task_start
Looking up: /home/curtis/Desktop/tagged/Gackt/REDEMPTION/01 REDEMPTION.m4a
Searching for track ID: cce60b4d-c344-48f7-9ac7-16b6161a1968
discogs: Searching for release cce60b4d-c344-48f7-9ac7-16b6161a1968
spotify: Invalid Spotify ID: cce60b4d-c344-48f7-9ac7-16b6161a1968
Item search terms: Gackt - REDEMPTION
discogs: Getting master release 76443
discogs: Getting master release 1395115
discogs: Getting master release 3177822
Sending event: trackinfo_received
Sending event: trackinfo_received
Sending event: trackinfo_received
Sending event: trackinfo_received
spotify: Searching Spotify for 'REDEMPTION artist:"Gackt"'
spotify: Spotify access token has expired. Reauthenticating.
spotify: Spotify access token: BQDZE3qUzmCilNZTBAWwFXo57thJphWbhNQDaP7wINkE1TxTedGmeRYvKbHCYw1iW3FnqpcPgNx1NHlbqyAp0q8iudYPu7PVCLMO72EaBphuty7Lyy-02hW00pWJ0zADXt_M3Ot9kro
spotify: Spotify access token has expired. Reauthenticating.
spotify: Spotify access token: BQDZE3qUzmCilNZTBAWwFXo57thJphWbhNQDaP7wINkE1TxTedGmeRYvKbHCYw1iW3FnqpcPgNx1NHlbqyAp0q8iudYPu7PVCLMO72EaBphuty7Lyy-02hW00pWJ0zADXt_M3Ot9kro
spotify: Spotify access token has expired. Reauthenticating.
spotify: Spotify access token: BQDZE3qUzmCilNZTBAWwFXo57thJphWbhNQDaP7wINkE1TxTedGmeRYvKbHCYw1iW3FnqpcPgNx1NHlbqyAp0q8iudYPu7PVCLMO72EaBphuty7Lyy-02hW00pWJ0zADXt_M3Ot9kro
spotify: Spotify access token has expired. Reauthenticating.
spotify: Spotify access token: BQDZE3qUzmCilNZTBAWwFXo57thJphWbhNQDaP7wINkE1TxTedGmeRYvKbHCYw1iW3FnqpcPgNx1NHlbqyAp0q8iudYPu7PVCLMO72EaBphuty7Lyy-02hW00pWJ0zADXt_M3Ot9kro
spotify: Spotify API error: Maximum retries reached.
Found 4 candidates.

/home/curtis/Desktop/tagged/Gackt/REDEMPTION/01 REDEMPTION.m4a
Sending event: before_choose_candidate

Finding tags for track"Gackt - REDEMPTION".
  Candidates:
  1. (39.8%) Jay Rock - Redemption
             ≠ id, artist, source, ...
             Discogs, Index 12, Track B12, [Redemption]
  2. (39.8%) Jay Rock - Redemption
             ≠ id, artist, source, ...
             Discogs, Index 12, Track B6, [Redemption]
  3. (37.5%) RMB - Redemption
             ≠ id, artist, length, ...
             Discogs, Index 1, Track A, [Redemption]
  4. (34.8%) Jay Rock - Redemption
             ≠ id, length, artist, ...
             Discogs, Index 12, Track B12, [Redemption]
➜ # selection (default 1), Skip, Use as-is, Enter search, enter Id, aBort,
eDit, edit Candidates? b
Sending event: import
wlg: Catched NoneType error in WhatLastGenre.setdown().
Sending event: cli_exit
playlist: Updating playlist: /quark/music/Playlists/Quit.m3u
playlist: Updating playlist: /quark/music/Playlists/Twelve-step Suite.m3u
```

But if you first delete the `config/spotify_token.json`, then it works:

```
Finding tags for track"Gackt - REDEMPTION".
  Candidates:
  1. (62.5%) GACKT - REDEMPTION
             ≠ id, source
             Spotify, Index 1, Track None, [REDEMPTION]
  2. (56.1%) GACKT - REDEMPTION
             ≠ id, source, index, ...
             Spotify, Index 6, Track None, [THE ELEVENTH DAY ～SINGLE COLLECTION～]
  3. (50.9%) GACKT - REDEMPTION - Live
             ≠ id, source, index, ...
             Spotify, Index 5, Track None, [GACKT PHILHARMONIC 2025 - DEMONIC PHILHARMONY (Live at Sumida Trifony Hall, Tokyo 2025)]
  4. (40.0%) GACKT - REDEMPTION (STUDIO APARTMENT ReMIX)
             ≠ id, length, source, ...
             Spotify, Index 4, Track None, [GACKTRACKS -ULTRA DJ ReMIX-]
  5. (39.8%) Jay Rock - Redemption
             ≠ id, artist, source, ...
             Discogs, Index 12, Track B12, [Redemption]
  6. (39.8%) Jay Rock - Redemption
             ≠ id, artist, source, ...
             Discogs, Index 12, Track B6, [Redemption]
  7. (39.4%) GACKT - LONGING
             ≠ id, title, source, ...
             Spotify, Index 2, Track None, [REDEMPTION]
  8. (37.5%) RMB - Redemption
             ≠ id, artist, length, ...
             Discogs, Index 1, Track A, [Redemption]
  9. (34.8%) Jay Rock - Redemption
             ≠ id, length, artist, ...
             Discogs, Index 12, Track B12, [Redemption]
➜ # selection (default 1), Skip, Use as-is, Enter search, enter Id, aBort,
```
