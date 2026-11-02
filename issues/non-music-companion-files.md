When I set up Beets, the plugins that kept track of your non-music companion files (art assets, textual notes, etc.) did not work well. For example, the `copyartifacts` plugin had a horrible bug that corrupted part of my collection. I remember trying at least one other plugin and finding it lacking. Now that beets is more mature, it would be good to finally solve this issue:

* How can I ensure that `beet import <some-directory>` moves the non-music files from that directory into the ultimate destination directory?
* How can I ensure that commands like `beet move` don't leave my non-music files behind?
* How can I ensure that files don't disappear into `/dev/null`?
