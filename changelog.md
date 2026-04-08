# Changelog

Configuration and Architecture:

- Renamed and standardized configuration constants and architecture flags (e.g., `is64` to `IS64`, `mask` to `MASK`).
- Updated usages of these constants across SIRA modules.
- Adjusted library path logic accordingly.

UpdateManager:

- Refactored API and internals (method and attribute renames).
- Improved logging and threading method names.
- Fixed call sites (e.g., `checkForUpdates`).

Input Sanitization:

- Added a paste-and-clean handler for phone, landline, and extension fields to - sanitize clipboard input.

UI/UX Improvements:

- Revamped `configPanel` layout and grouping for phone masks, general options, and database management.
- Made minor control/label changes.
- Improved helper usage.

Localization and Versioning:

- Updated translations (ptBR).
- Bumped add-on version to `2026.2.0` in `buildVars.py`.
