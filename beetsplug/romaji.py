"""Fetch Latin-script names and titles from MusicBrainz, for ctrpaths.

`beet romaji [QUERY]` looks up, for the matching items:

- Latin names for every non-Latin artist and album artist credit not already
  known (see ctrpaths/aliases.py), into romaji-names.json.
- Latin album and track titles from MusicBrainz pseudo-releases, for releases
  with non-Latin titles not already looked up (see ctrpaths/titles.py), into
  the flexible attributes `album_transl` and `title_transl`.

`-f` looks everything up again. With `romaji.auto` (the default), newly
imported music is looked up during import, before its files are moved, so
paths use the Latin forms.

Configuration (defaults shown):

    romaji:
      auto: yes
      titles: yes            # look up pseudo-release titles
      languages: [eng]       # translation languages (ISO 639-3, as
                             # MusicBrainz uses), most preferred first
      prefer: translation    # or: transliteration
"""

import re

from beets import ui
from beets.plugins import BeetsPlugin

from ctrpaths import aliases, titles

_UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

# Flexible attribute recording which pseudo-release was used ('none' if the
# release has none), so that releases are not looked up again.
_CHECKED = 'transl_release'


class RomajiPlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.config.add({
            'auto': True,
            'titles': True,
            'languages': ['eng'],
            'prefer': titles.TRANSLATION,
        })
        prefer = self.config['prefer'].as_choice(
            [titles.TRANSLATION, titles.TRANSLITERATION])
        self.prefer = prefer
        self.languages = self.config['languages'].as_str_seq()
        if self.config['auto'].get(bool):
            self.register_listener('import_task_apply', self.import_task_apply)
            if self.config['titles'].get(bool):
                # A plugin stage runs after the album is added to the library
                # and before its files are moved.
                self.import_stages = [self.import_stage]

    def commands(self):
        cmd = ui.Subcommand(
            'romaji',
            help='fetch Latin-script names and titles from MusicBrainz',
        )
        cmd.parser.add_option(
            '-f', '--force', action='store_true',
            help='look up names and titles again, even if already known',
        )

        def func(lib, opts, args):
            items = list(lib.items(args))
            self.fetch(items, force=opts.force, verbose=True)
            if self.config['titles'].get(bool):
                self.fetch_titles(lib, items, force=opts.force, verbose=True)

        cmd.func = func
        return [cmd]

    def import_task_apply(self, session, task):
        self.fetch(task.imported_items())

    def import_stage(self, session, task):
        if task.skip:
            return
        self.fetch_titles(session.lib, task.imported_items())

    ### Artist names ###

    def fetch(self, items, force=False, verbose=False):
        seen = set()
        fetched = learned = 0
        for item in items:
            for entity, mbid, credit in (
                ('recording', item.mb_trackid, item.artist),
                ('release', item.mb_albumid, item.albumartist),
            ):
                if not credit or aliases.is_latin(credit) or credit in seen:
                    continue
                seen.add(credit)
                if aliases.known(credit) and not force:
                    continue
                if not (mbid and _UUID.match(mbid)):
                    continue
                try:
                    learned += aliases.learn(entity, mbid, credit)
                except Exception as e:
                    self._log.warning('{} {}: {}', entity, mbid, e)
                    continue
                fetched += 1
                latin = aliases.lookup(credit)
                if verbose:
                    self._log.info('{} -> {}', credit, latin or '(no Latin name)')
                if fetched % 20 == 0:
                    aliases.save()
        if fetched:
            aliases.save()
        if verbose:
            self._log.info(
                'Fetched {} credits; learned {} artist names.', fetched, learned
            )

    ### Titles ###

    def fetch_titles(self, lib, items, force=False, verbose=False):
        # Group items by album (or by release, for singletons).
        groups = {}
        for item in items:
            key = ('album', item.album_id) if item.album_id else (
                'release', item.mb_albumid)
            groups.setdefault(key, []).append(item)

        looked_up = found = 0
        for (kind, _), group in groups.items():
            album = group[0].get_album() if kind == 'album' else None
            if album is not None:
                group = list(album.items())
            mbid = group[0].mb_albumid
            album_title = album.album if album else group[0].album
            if not (mbid and _UUID.match(mbid)):
                continue
            if aliases.is_latin(album_title or '') and all(
                    aliases.is_latin(item.title or '') for item in group):
                continue  # Nothing to transliterate.
            holder = album if album is not None else group[0]
            if holder.get(_CHECKED) and not force:
                continue
            try:
                result = titles.lookup(mbid, self.languages, self.prefer)
            except Exception as e:
                self._log.warning('release {}: {}', mbid, e)
                continue
            looked_up += 1
            if result:
                found += 1
            self._store(album, group, result)
            if verbose:
                name = f'{group[0].albumartist} - {album_title}'
                if result:
                    self._log.info('{} -> {} ({} {})', name,
                                   result['album'] or album_title,
                                   result['language'], result['kind'])
                else:
                    self._log.info('{} -> (no pseudo-release)', name)
        if verbose:
            self._log.info('Looked up {} releases; {} with Latin titles.',
                           looked_up, found)

    def _store(self, album, items, result):
        release = result['release'] if result else 'none'
        if album is not None:
            album[_CHECKED] = release
            _set(album, 'album_transl', result and _latin_for(
                album.album, result['album']))
            album.store(inherit=False)
        for item in items:
            if album is None:
                item[_CHECKED] = release
                _set(item, 'album_transl', result and _latin_for(
                    item.album, result['album']))
            _set(item, 'title_transl', result and _latin_for(
                item.title, titles.track_title(result, item)))
            item.store()


def _latin_for(original, latin):
    """The Latin form to store for an original title, if it needs one."""
    if not original or aliases.is_latin(original) or not latin:
        return None
    return latin


def _set(obj, key, value):
    if value:
        obj[key] = value
    else:
        try:
            del obj[key]
        except KeyError:
            pass
