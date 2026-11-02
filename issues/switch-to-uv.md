I'd like to modernize the project management from conda to uv.
There is probably not a reason we need conda, but good to double check.

I guess I would want `uv tool install beets` for the actual` beet command line executable?
But then I need to install the necessary plugins and dependencies into that same tool environment.
And I need to `python setup.py install` in `whatlastgenre` with the beets tool environment active as well, assuming I keep using the beets `wlg` plugin (see also handle-genres-better.md).
