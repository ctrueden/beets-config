"""Romanization of Japanese text in path components.

beets' asciify_paths uses unidecode, which transliterates one character at a
time and reads every kanji with its Mandarin reading: この誰もいない部屋で
becomes "konoShui moinaiBu Wu de". Here, runs of Japanese text are instead
romanized with cutlet, which segments words with MeCab/UniDic and reads them
in context: "Kono dare mo inai heya de".

Text outside the Japanese runs is left alone, for unidecode to handle later.
"""

import functools
import re

# Whether to restore the original spelling of katakana loanwords
# (モノクロレター -> "Monochrome letter" rather than "Monokuro retaa").
# Often nicer, but sometimes wrong (シャープネル -> "sharp flannel").
FOREIGN_SPELLING = False

_KANA = '\u3040-\u309f\u30a0-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9f'
_KANJI = '\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3005-\u3007'
_HAS_KANA = re.compile(f'[{_KANA}]')
_HAS_KANJI = re.compile(f'[{_KANJI}]')
_JAPANESE_RUN = re.compile(f'[{_KANA}{_KANJI}]+')
_PARTICLES = {'と', 'の', 'や', 'が', 'に', 'で', 'を', 'は', 'へ', 'も'}
_OPENERS = '([{<"\'~-「『（［｛〈《【“‘〜～'

# Variant kanji (itaiji) common in names, which UniDic does not know.
_VARIANTS = str.maketrans({
    '髙': '高',
    '﨑': '崎',
    '嵜': '崎',
    '栁': '柳',
    '濵': '濱',
    '邉': '邊',
    '德': '徳',
})


@functools.cache
def _cutlet():
    import cutlet
    c = cutlet.Cutlet()
    c.use_foreign_spelling = FOREIGN_SPELLING
    return c


@functools.lru_cache(maxsize=65536)
def _romanize_run(run, capitalize, title):
    romaji = _romanize(run, capitalize, title)
    if '?' in romaji:
        # Some character is unknown to UniDic; romanize what we can.
        romaji = ''.join(
            _romanize_char(ch, capitalize and i == 0, title)
            for i, ch in enumerate(run)
        ) if len(run) > 1 else romaji
    return romaji


def _romanize(text, capitalize, title):
    return _cutlet().romaji(text.translate(_VARIANTS),
                            capitalize=capitalize or title, title=title)


def _romanize_char(ch, capitalize, title):
    romaji = _romanize(ch, capitalize, title)
    if '?' not in romaji:
        return romaji
    from unidecode import unidecode
    return unidecode(ch).strip()


def romanize(s, kanji=True, title=False):
    """Romanize the Japanese runs of s.

    If `title` is true, capitalize every word, as for names: 天野月 becomes
    "Amano Tsuki" rather than "Amano tsuki".

    Runs containing kana are always treated as Japanese. Runs of only kanji
    are romanized only if `kanji` is true; otherwise they are left alone, so
    that e.g. Chinese text keeps unidecode's pinyin readings.
    """
    if not (_HAS_KANA.search(s) or (kanji and _HAS_KANJI.search(s))):
        return s

    def replace(m):
        run = m.group()
        if not (kanji or _HAS_KANA.search(run)):
            return run
        start, end = m.span()
        before = s[start - 1] if start > 0 else ''
        after = s[end] if end < len(s) else ''
        # Capitalize at the start of a phrase, but not mid-phrase: "FFの曲"
        # becomes "FF no kyoku", not "FF No kyoku".
        capitalize = before == '' or before.isspace() or before in _OPENERS
        if title and run in _PARTICLES:
            # Keep particles lowercase in names: "Ranma Saotome to Akane Tendo".
            romaji = _romanize_run(run, False, False)
        else:
            romaji = _romanize_run(run, capitalize, title)
        # Separate romaji from adjacent letters and digits: "LOVEマシーン"
        # becomes "LOVE mashiin", not "LOVEmashiin".
        if before.isalnum(): romaji = ' ' + romaji
        if after.isalnum(): romaji += ' '
        return romaji

    return _JAPANESE_RUN.sub(replace, s)
