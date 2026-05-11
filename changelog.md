# Changelog

- Introduces support for custom speech dictionaries (SpeechDictionaries) across buildVars, sconstruct, sitescons manifests, and typings. Adds explanatory comments for configuration.

- Revamps CI/workflow:
Restructures .github/workflows/buildaddon.yml with template guards and simplified steps.
Implements uv caching for faster builds.
Separates artifact uploads.
Adjusts artifact download/merge and release steps.

- Updates pre-commit config to align with NVDA repo conventions:
Adjusts hooks and runs pyright via uv.
Tightens pyright/pyproject settings and NVDA/wxPython workarounds to reduce false positives.
Removes pyright ignore comments in addon/globalPlugins/SIRA (init.py).

- Bumps several tooling packages in uv.lock.
