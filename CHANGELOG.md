# Changelog

All notable changes to `renson-waves-client` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- _nothing yet_

---

## [0.1.0] – 2026-04-13

### Added
- `RensonWavesClient` — async client for the Renson WAVES local HTTP API
- Six endpoint methods:
  - `async_get_constellation` (connectivity probe, always strict)
  - `async_get_wifi_status`
  - `async_get_global_uptime`
  - `async_get_decision_room`
  - `async_get_decision_silent`
  - `async_get_decision_breeze`
- `async_get_all()` — fetches all six endpoints concurrently via `asyncio.gather`
- `WavesData` dataclass aggregate model
- `strict` keyword argument on all non-probe methods (default `False`)
- Custom exceptions: `RensonWavesError`, `RensonWavesCannotConnect`,
  `RensonWavesRequestError`, `RensonWavesResponseError`
- `py.typed` marker for PEP 561 compliance
- `src` layout, `hatchling` build backend
- Full mypy strict compliance
- Ruff lint/format configuration
- Pytest suite with `aioresponses` HTTP-level mocking (~95 % coverage)
- GitHub Actions CI workflow (lint → typecheck → test matrix → build)

[Unreleased]: https://github.com/Pietergeerts/renson-waves-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Pietergeerts/renson-waves-python/releases/tag/v0.1.0
