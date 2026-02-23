- Replace `addonPath` with `ADDONPATH` and add `is64` detection to select `lib` or `lib64` directories. 

- Update imports across SIRA plugins to load internal libs from the correct folder and log/raise clearer errors when mandatory internal modules are missing.

- Centralize SQLite/sql handling in `sqlLoader` and adjust model/controller code to use the new `sql` module.

- Add `onUninstall` logic to optionally clear add-on config on uninstall and ensure addon data dir/name capitalization is consistent.

- Bump add-on version/name in `buildVars`, add `pyproject.toml` and `uv.lock` for packaging/dependencies, and overhaul `pre-commit`/`ruff`/`pyright` configurations.

- Miscellaneous fixes: tidy up `sitescons` tool code (formatting, typing, builder args), small typing/formatting edits, and add missing trailing commas.
