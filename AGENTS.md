# csspin-tooling — agent guide

Plugin package for the csspin task runner. Bundles miscellaneous utility
plugins.

## Plugins (`src/csspin_tooling/`)

### `sbomasm`

Wraps the [sbomasm](https://github.com/interlynk-io/sbomasm) CLI. Exposed as a
task group with two tasks, each hooked into the `sbom:*` lifecycle via `when=`:

- `sbomasm assemble` (`when="sbom:assemble"`) — merges `*.cdx.json` SBOMs into
  one. Single-input case is a pass-through copy (sbomasm itself rejects single
  inputs).
- `sbomasm enrich` (`when="sbom:enrich"`) — enriches the assembled SBOM's
  primary component with project metadata (name, version, author, license)
  extracted via `csspin_python.python.get_project_metadata`. Authors are parsed
  from RFC 2822 `Author-email` into sbomasm's `name (email)` format.

`provision(cfg)` always downloads the sbomasm release binary (Linux/Windows
x86_64) into `{spin.data}/csspin_tooling/sbomasm/{version}` if not cached.

The `init` hook prepends that versioned dir to `PATH` (same pattern as
`sbomqs`), so tasks invoke the binary as plain `sbomasm`. There is no `use`
override.

### `sbomqs`

Wraps the [sbomqs](https://github.com/interlynk-io/sbomqs) CLI. Quality gate for
the assembled SBOM, invoked standalone after `spin sbom` (no `when=` lifecycle
hook). Exposed as a task group with one task:

- `sbomqs policy` — runs `sbomqs policy -f <policy_file> <input_file>` via
  `sh` (`check=True`), so a policy violation makes the task exit non-zero. The
  policy applies uniformly to every component, including nested ones.

`provision(cfg)` always downloads the sbomqs release binary (Linux/Windows
x86_64) into `{spin.data}/csspin_tooling/sbomqs/{version}`. The download itself
is cached. Same tar.gz layout as sbomasm.

The `init` hook prepends that versioned dir to `PATH` (same pattern as
`csspin_java.java` / `csspin_ce.mkinstance`), so the binary is discoverable on
every task. The `policy` task resolves it inline with `shutil.which("sbomqs")`.
There is no `use` override.

The `policy_file` default is a callable (`default_policy_file`) resolving via
`importlib.resources` to the bundled `policies/default.yaml`; the `configure`
hook materializes it during defaults (same pattern as `csspin_ce.mkinstance`). A
configured path replaces it entirely. The default blacklists copyleft licenses
(`GPL-.*`, `EUPL-.*`,
`CC-BY-SA/NC/ND`) and requires `name`/`version`/`license` on every component.

### `fetch_vex`

Downloads the VEX file for a project from a Dependency-Track instance.

- `fetch_vex` — looks up the project UUID via the DepTrack API, fetches its
  CycloneDX VEX data, and writes it to `target_directory`. The filename is
  derived from `/metadata/component` name+version (slugified), falling back to
  `vex.json` (which then raises, since that signals invalid VEX data).

Runtime dep: `requests`. No `provision` step.

## Schemas

- `sbomasm_schema.yaml` — `version` (sbomasm release), `install_dir`,
  `output_file` (default `{spin.project_name}.cdx.json`),
  `format.spec` (`cyclonedx` or `spdx`), `format.version`.
- `sbomqs_schema.yaml` — `version` (sbomqs release), `install_dir`,
  `input_file` (default `{spin.project_name}.cdx.json`),
  `policy_file` (callable default → bundled policy, resolved in `configure`;
  else path override).
- `fetch_vex_schema.yaml` — `project_name`, `project_version`, `deptrack_url`,
  `deptrack_api_key` (`secret`), `cyclonedx_version`, `target_directory`. All
  four of url/api_key/project_name/project_version are required at runtime; the
  task dies if any is missing.

## Deps

- Runtime (`pyproject.toml`): `csspin-python`, `requests`.
- Sibling plugins: `csspin` (core), `csspin-python` (Python interpreter +
  `get_project_metadata`).
- Build/dev: setuptools, setuptools_scm, pytest, pytest-cov, mypy, pylint,
  black, isort.

## Dev workflow

```bash
uv venv venv
source venv/bin/activate # required for spin/pytest to be on PATH
uv pip install -r requirements-dev.txt # installs spin + dev deps
spin provision # provision the project for running spin tasks
pytest tests/ # run tests
prek run --all-files # run linting and formatting
```

- `requirements-dev.txt` is the single source of truth for the dev env: it
  pulls in `spin` itself plus everything needed to develop and test the
  plugin. No separate `pip install -e .` step.
- **Tests run via plain `pytest`**, not `spin test`. `tests/unit/` holds the
  unit tests (`test_sbomasm.py`, `test_sbomqs.py`, `test_fetch_vex.py`);
  `tests/integration/`
  shells out to `spin` to exercise provisioning end-to-end.
- Run provisioning tests only in case something for the provisioning has
  changed.
- **`spin <task>` is for exploratory verification** — e.g., running
  `spin sbomasm assemble` / `spin sbomasm enrich` / `spin sbomqs policy` /
  `spin fetch_vex` to confirm the plugins behave as expected during
  development. It is not the test runner.
- Python ≥3.10.
- Pre-commit hooks (run via `prek`): mypy (strict), pylint, black, isort.

## Non-obvious

- **CycloneDX is the default SBOM format**; SPDX is reachable via the
  `sbomasm` schema config, not a separate task.
- **`enrich` is independent of `assemble`** — both run on the project's output
  SBOM and can be invoked separately.
- **Metadata extraction requires a properly configured `pyproject.toml`** in
  the consuming project. `sbomasm enrich` dies on missing name/version/license;
  authors must each carry both a name and an email.
- **Docs**: `doc/` is built with `csspin_docs.sphinx`. Schema reference pages
  are generated from the schemas via `schemadoc` build rules in `spinfile.yaml`.
