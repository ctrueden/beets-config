"""Fetch Latin-script artist names from MusicBrainz, for ctrpaths.

`beet romaji [QUERY]` looks up every non-Latin artist and album artist
credit of the matching items that is not already known; `-f` looks them up
again. With `romaji.auto` (the default), newly imported music is looked up
during import, before its files are moved, so paths use the Latin names.

See ctrpaths/aliases.py for details.
"""

import re

from beets import ui
from beets.plugins import BeetsPlugin

from ctrpaths import aliases

_UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


class RomajiPlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.config.add({'auto': True})
        if self.config['auto'].get(bool):
            self.register_listener('import_task_apply', self.import_task_apply)

    def commands(self):
        cmd = ui.Subcommand(
            'romaji', help='fetch Latin-script artist names from MusicBrainz'
        )
        cmd.parser.add_option(
            '-f', '--force', action='store_true',
            help='look up names again, even if already known',
        )
        cmd.func = lambda lib, opts, args: self.fetch(
            lib.items(args), force=opts.force, verbose=True
        )
        return [cmd]

    def import_task_apply(self, session, task):
        self.fetch(task.imported_items())

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
