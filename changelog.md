Adds many bundled `lib64` modules and helpers required by the SIRA plugin (including `csv`, `masked` package, `sqlite3` package with binary extensions and tests, various tools, and `wordwrap`).

Also introduces `sqlLoader` and other support files under `addon/globalPlugins/SIRA`.

Applies formatting fixes to the Portuguese readme (`addon/doc/pt_BR/readme.md`) and updates existing files:
- `addon/globalPlugins/SIRA/model.py`
- `addon/installTasks.py`
- `buildVars.py`
- `pyproject.toml`
- top-level `readme.md`

These changes bundle necessary runtime dependencies and polish documentation/metadata for the SIRA add-on.