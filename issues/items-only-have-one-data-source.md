When importing a track, only one data source can be used. For example:

```
$ beet info -l brazil album:supercharged | grep '\(mb_\|spotify\|discogs\|data_source\)'
         data_source: Spotify
     discogs_albumid: 0
    discogs_artistid: 0
     discogs_labelid: 0
    mb_albumartistid: 5LfGQac0EIXyAN8aUwmNAQ
   mb_albumartistids: 5LfGQac0EIXyAN8aUwmNAQ
          mb_albumid: 5PDtsevGakWdIRZyeOZ83g
         mb_artistid: 5LfGQac0EIXyAN8aUwmNAQ
        mb_artistids: 5LfGQac0EIXyAN8aUwmNAQ
   mb_releasegroupid: 
   mb_releasetrackid: 
          mb_trackid: 5bRstyy39l6RBiP6wJ1VSB
           mb_workid: 
    spotify_album_id: 5PDtsevGakWdIRZyeOZ83g
   spotify_artist_id: 5LfGQac0EIXyAN8aUwmNAQ
    spotify_track_id: 5bRstyy39l6RBiP6wJ1VSB
```

In the example above, the spotify source was used, as indicated by `data_source: Spotify`. The `mb_*` fields are reused to store Spotify-specific IDs, which is horribly confusing since these are not MusicBrainz IDs, and especially since those values *also* get stored to `spotify_*` fields as well! So why corrupt the `mb_*` fields?

* Is MusicBrainz too hardcoded into Beets?
* Why can't we have MusicBrainz IDs *and* Spotify IDs (and Discogs, and any/all autotag sources) attached to the same item?

Tangentially: where do these `spotify_*` fields come from? Are they Beets flexible attributes? They aren't in the DB schema:
```
$ echo '.schema items' | sqlite3 ~/.config/beets/library.db
CREATE TABLE items (id INTEGER PRIMARY KEY, path BLOB, album_id INTEGER, title TEXT, artist TEXT, artist_sort TEXT, artist_credit TEXT, album TEXT, albumartist TEXT, albumartist_sort TEXT, albumartist_credit TEXT, genre TEXT, lyricist TEXT, composer TEXT, composer_sort TEXT, arranger TEXT, grouping TEXT, year INTEGER, month INTEGER, day INTEGER, track INTEGER, tracktotal INTEGER, disc INTEGER, disctotal INTEGER, lyrics TEXT, comments TEXT, bpm INTEGER, comp INTEGER, mb_trackid TEXT, mb_albumid TEXT, mb_artistid TEXT, mb_albumartistid TEXT, mb_releasetrackid TEXT, albumtype TEXT, label TEXT, acoustid_fingerprint TEXT, acoustid_id TEXT, mb_releasegroupid TEXT, asin TEXT, catalognum TEXT, script TEXT, language TEXT, country TEXT, albumstatus TEXT, media TEXT, albumdisambig TEXT, releasegroupdisambig TEXT, disctitle TEXT, encoder TEXT, rg_track_gain REAL, rg_track_peak REAL, rg_album_gain REAL, rg_album_peak REAL, r128_track_gain INTEGER, r128_album_gain INTEGER, original_year INTEGER, original_month INTEGER, original_day INTEGER, initial_key TEXT, length REAL, bitrate INTEGER, format TEXT, samplerate INTEGER, bitdepth INTEGER, channels INTEGER, mtime REAL, added REAL, style TEXT, discogs_albumid INTEGER, discogs_artistid INTEGER, discogs_labelid INTEGER, work TEXT, mb_workid TEXT, work_disambig TEXT, trackdisambig TEXT, isrc TEXT, albumtypes TEXT, bitrate_mode TEXT, encoder_info TEXT, encoder_settings TEXT, artists TEXT, artists_ids TEXT, artists_sort TEXT, artists_credit TEXT, remixer TEXT, albumartists TEXT, albumartists_sort TEXT, albumartists_credit TEXT, mb_artistids TEXT, mb_albumartistids TEXT, barcode TEXT, release_group_title TEXT);
```
So maybe the spotify plugin is pulling them from `mb_*` after all and validating them against some regex? Need to check the code...

The main question here is: How do I associate a given track with its corresponding track ID across multiple remote metadata sources? Doing this has value for a number of reasons, such as keeping playlists synchronized between local/Beets and services like Spotify and iBroadcast. For the beets-ibroadcast plugin, I use custom attributes `ib_tagids`, `ib_trackid`, `ib_uploadtime`. Is this what the spotify plugin is doing? Need to check. What about Discogs? It also has `discogs_*` (custom?) attributes, but also steals the `mb_*` fields...

This issue has been discussed on the Beets forum. See:
* https://github.com/beetbox/beets/discussions/4220

And was solved in a merged PR:
* https://github.com/beetbox/beets/pull/4708

By "solved" I mean that it pulls the linked Discogs and Spotify IDs from the track's MusicBrainz metadata. But:
* What if the track isn't on MusicBrainz, but rather only Spotify (or YouTube Music, or Amazon Music, or...)?
* What if Discogs was chosen as the primary tagging source over MusicBrainz?
