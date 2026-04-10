# Changelog

Rename `secretary_office` to `secretaryOffice` throughout `addEditRecord.py` and update related UI controls, bindings, focus mapping, form data keys, and clearing logic to use the new identifier.

Improve `TextCtrl` configuration (add `formatcodes`) and reorder bindings for paste handling. Rework `onPasteAndClean` to robustly handle `Ctrl+V`:

- Clean clipboard text to digits.
- Detect the field mask.
- Count mask digits.
- Pad shorter inputs to align with the mask.
- Set the field value.
- Adjust the insertion point to preserve expected formatting.

Bump add-on version to `2026.2.2` and update the changelog in `buildVars.py` to mention the paste fix.
