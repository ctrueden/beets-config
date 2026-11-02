When I set up Beets, the plugins that kept track of your non-music companion files (art assets, textual notes, etc.) did not work well. For example, the `copyartifacts` plugin had a horrible bug that corrupted part of my collection. I remember trying at least one other plugin and finding it lacking. Now that beets is more mature, it would be good to finally solve this issue:

* How can I ensure that `beet import <some-directory>` moves the non-music files from that directory into the ultimate destination directory?
* How can I ensure that commands like `beet move` don't leave my non-music files behind?
* How can I ensure that files don't disappear into `/dev/null`?

## Status (November 2026)

beets still has no built-in support. The maintained plugin is
[beets-filetote](https://github.com/gtronset/beets-filetote) (1.3.7, August
2026, beets >= 2.4), a successor to copyartifacts. Next step: evaluate it on
a scratch library (copy a few album folders with artwork and notes, import,
then `beet modify`/`beet move` them) before enabling it on the real one.
