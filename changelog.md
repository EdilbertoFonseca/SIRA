Adds a `lib64` tree containing bundled modules (CSV, SQLite3 with necessary binaries/tests, and various wx/tools utilities like `img2img`, `pywxrc`, `helpviewer`, etc.). Includes a new masked widget package (`masked`, `combobox`, `ctrl`, etc.).

Also updates runtime dependencies and UI controls for the SIRA addon. Includes updates to `sqlLoader`, `model.py`, and `installTasks.py`.

Applies minor documentation and localization fixes across Portuguese README, locale files, `buildVars`, `changelog`, and `pyproject.toml`. These changes ensure reliable execution of the SIRA global plugin by bundling required libraries and polishing documentation.
