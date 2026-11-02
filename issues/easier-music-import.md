Right now, I import music with a `beet` command line call, specifying the
appropriate custom attributes for correct file naming in the collection.

Example:

```shell
beet import --set=category=Soundtracks --set=avmedia='Video Games' --set=franchise='Vampire Survivors' Vampire\ Survivors\ The\ Original\ Soundtrack
```

But for family members who are not me, a GUI would be much more accessible.

The closest thing to a solution I've found is beets-flask, which has a
UI-driven import process. But it needs support for flexible attribute fields:
`category`, `subcategory`, `avmedia`, `franchise`, ...

And probably other things, pending testing on real-world to-be-imported music.
