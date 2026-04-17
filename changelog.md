# Changelog

This commit updates the SIRA addon to utilize `globalVars.appArgs.configPath` for database storage, ensuring that the database and its necessary directories are correctly managed within the application's configuration path.

Changes:

- `configPanel`: Sets `DatabaseConfig.defaultPath` to `<configPath>/SIRADB/database.db`.
- `dbConfig`: `getCurrentDatabasePath` now returns the primary DB path if the selected path is empty, preventing potential errors.

`model`:

- Builds `ADDONDATADIR` from `globalVars.appArgs.configPath`.
- Defines `DEFAULTDBPATH`.
- Creates the database directory on `Section.enter` before connecting to the database.

`buildVars`:

-Bumps the addon version to `2026.2.5`.
- Raises the minimum NVDA version requirement to `2025.1.0`.
