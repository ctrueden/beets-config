I have Beets configured to transliterate into ASCII with `asciify_paths: yes`.

However, Beets's transliterations leave a lot to be desired.

For example, the GACKT song:

    この誰もいない部屋で

gets named by Beets as:

```
GACKT - konoShui moinaiBu Wu de.mp3
```

Whereas Google Translate transliterates it as:

    Kono daremoinai heya de

And translates it as:

    In this empty room

In the above example, I *think* it's correctly treating it as Japanese (not Chinese) script, but the transliteration is strange; when fed back into Google Translate, it comes out as "この首位 もい内部 う で" and translates as "This top position is also". I also think that Beets sometimes mixes up Chinese versus Japanese transliterations; maybe it does not use the appropriate script metadata from MusicBrainz to figure out which script a particular item is using before transliterating it?

I dug into this once years ago, and determined that Beets uses the `unidecode` library, but not [`unihandecode`](https://pypi.org/project/unihandecode/), to do the decoding. I tried using unihandecode in the `transliterate.py` script in this directory, but never finished turning it into a proper Beets plugin and/or upstream contribution.

As part of this project: I would also like to *tag* the files with transliterated characters, writing the original (non-ASCII) script field values to separate tags within the file. I.e. I don't want to throw away the original titles, artist names, album names, etc., but I *do* want to see the transliterated values in my music players. (If the music players themselves would transliterate on the fly, that would be even better, but they don't, and it's easier to just do it in the metadata so that all players behave the way I would prefer.)

See also: the `languages` subfolder, which contains a list of track titles from my collection in various scripts, with text files named according to the four-character script codes.

## Progress

* Symbols: `ctrpaths` now maps symbols that `unidecode` drops or renders
  poorly (hearts, stars, notes, the Letterlike Symbols block, Japanese
  punctuation, etc.) to readable ASCII before beets asciifies paths. See
  `_TRANSLIT` and `_WORD_SYMBOLS` in `ctrpaths/__init__.py`.
