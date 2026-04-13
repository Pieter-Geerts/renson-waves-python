# Release Checklist — renson-waves-client

Follow this checklist for every PyPI release.

---

## Pre-release

- [ ] All CI checks pass on `main` (lint, typecheck, tests, build)
- [ ] Coverage ≥ 90 %
- [ ] `CHANGELOG.md` updated — move items from `[Unreleased]` to a new version section
- [ ] Version bumped in both places:
  - `src/renson_waves_client/__init__.py` → `__version__ = "X.Y.Z"`
  - `pyproject.toml` → `version = "X.Y.Z"`
- [ ] `requires-python` in `pyproject.toml` still accurate
- [ ] Dependency versions reviewed (aiohttp lower bound)
- [ ] `README.md` examples and payload fields up to date
- [ ] No `print()` or debug code left in `src/`
- [ ] No Home Assistant imports anywhere in `src/`

## Tagging

```bash
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

## Build & verify

```bash
python -m build
# inspect
tar -tzf dist/renson_waves_client-*.tar.gz | head -30
python -m zipfile -l dist/renson_waves_client-*.whl
# should contain py.typed marker
```

## Test on TestPyPI first

```bash
pip install twine
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ renson-waves-client==X.Y.Z
```

## Publish to PyPI

```bash
twine upload dist/*
```

## Post-release

- [ ] GitHub Release created from tag with CHANGELOG section
- [ ] `[Unreleased]` section reset in `CHANGELOG.md`
- [ ] dependent HA integration `manifest.json` pinned to new version
- [ ] Announce in relevant community threads if applicable
