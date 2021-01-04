https://musicbrainz.org/series/b2b031ec-176e-45fd-8965-4691a9e79691 = OverClocked ReMix
https://musicbrainz.org/series/29eb0b44-aa4c-4ca8-9ea9-da482ce53f00 = OC ReMoved

Changelog   = https://ocremix.org/info/ReMix_Changelog
Forum topic = https://ocremix.org/community/topic/38248-the-ocr-catalog-on-musicbrainz/
Style guide = https://musicbrainz.org/doc/Style/Titles/OC_ReMix_series
OC ReMoved  = https://williamjacksn.github.io/ocremoved/

Work I did  = https://ocremix.org/community/topic/38248-the-ocr-catalog-on-musicbrainz/?tab=comments#comment-848290

The file ocremix/ids.txt is a database of OC-ReMix + MusicBrainz information.
The fields are: 1) OCR code; 2) MusicBrainz recording ID; 3) MB title; 4) filename.

- MB titles are from MusicBrainz metadata, not completely consistent with
  the original title from pristine MP3 title tag.

- Filenames are from the torrent, or from the "OC ReMoved" repository on GitHub.

- Some OCR codes were reused after the previous entry was removed, and some weren't.
 -- To indicate an item was removed, I'm using an 'x' suffix to the tag (OCR#####x).

- Some supposedly removed entries never had a code at all. These use OCRxxxxxx.

---------------------------------------------------------
TO DO

* After edits have settled down, on musicbrainz.org, double check
  the "OverClocked ReMix" and "OC ReMoved" series.
 -- Ensure all items appear in the correct series, and only the correct series.
 -- Pay special attention to OCR00461 and OCR01059 (see also
    https://ocremix.org/community/topic/50136-ocr00461-and-ocr01059-are-missing-from-ocremixorg/).
