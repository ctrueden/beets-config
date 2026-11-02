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

I dug into this once years ago, and determined that Beets uses the `unidecode` library, but not [`unihandecode`](https://pypi.org/project/unihandecode/), to do the decoding. I tried using unihandecode in the `.local/transliterate.py` script, but never finished turning it into a proper Beets plugin and/or upstream contribution.

As part of this project: I would also like to *tag* the files with transliterated characters, writing the original (non-ASCII) script field values to separate tags within the file. I.e. I don't want to throw away the original titles, artist names, album names, etc., but I *do* want to see the transliterated values in my music players. (If the music players themselves would transliterate on the fly, that would be even better, but they don't, and it's easier to just do it in the metadata so that all players behave the way I would prefer.)

See also: the `.local/languages` folder, which contains a list of track titles from my collection in various scripts, with text files named according to the four-character script codes.

## Progress

* Symbols: `ctrpaths` now maps symbols that `unidecode` drops or renders
  poorly (hearts, stars, notes, the Letterlike Symbols block, Japanese
  punctuation, etc.) to readable ASCII before beets asciifies paths. See
  `_TRANSLIT` and `_WORD_SYMBOLS` in `ctrpaths/__init__.py`.

* Japanese: `ctrpaths.japanese` romanizes runs of Japanese text with
  [cutlet](https://github.com/polm/cutlet) (MeCab + UniDic), which segments
  words and reads them in context, so the example above becomes
  `GACKT - Kono dare mo inai heya de`. unihandecode turned out to be little
  better than unidecode: it swaps Mandarin readings for single-character
  Japanese on'yomi (`konoSui moinaiBu Oku de`), with no word segmentation.
  Text with kana is always treated as Japanese; kanji-only text is treated as
  Japanese unless the item's `script`/`language` says Chinese or Korean.

* Names: artist names now come from MusicBrainz (English aliases or Latin
  sort names), fetched by the `romaji` plugin into a local cache: 矢井田瞳 ->
  `Hitomi Yaida`, 小池令 -> `Ryo Koike` (cutlet said `Ya Ida Hitomi` and
  `Koikerei`). Of ~330 non-Latin artist credits, 17 have no Latin name on
  MusicBrainz; those fall back to cutlet, with an override table
  (`ctrpaths: romaji:` in `config.yaml`) for the ones it gets wrong.

Still open:

* Kanji-only text in a Chinese release with no Chinese `script`/`language`
  metadata is misread as Japanese.
* Tagging files with transliterated values while keeping the originals (see
  above) is not started.
