# csspin-tooling — agent guide

Plugin package for the csspin task runner. Bundles miscellaneous utility
plugins.

## Plugin (`src/csspin_tooling/`)

- **`sbomasm`** — wraps the [sbomasm](https://github.com/interlynk-io/sbomasm)
  CLI. Tasks:
  - `sbomasm:assemble` — merges `*.cdx.json` SBOMs into one. Single-input
    case is a pass-through copy (sbomasm itself rejects single inputs).
  - `sbomasm:enrich` — fills the assembled SBOM with project metadata
    (name, version, author, supplier, license) extracted via
    `python -m build --metadata`.

Standard csspin plugin shape (`defaults`, `provision(cfg)` downloads the
sbomasm release binary if not cached, `@task`, sibling
`sbomasm_schema.yaml`).

## Schema

`sbomasm_schema.yaml` validates: `version` (sbomasm release), `install_dir`,
`use` (override binary), `output_file` (default
`{spin.project_name}.cdx.json`), `format.spec` (`cyclonedx` or `spdx`),
`format.version`.

## Sibling deps

- `csspin` (core), `csspin-python` (provides the Python interpreter used for
  `python -m build --metadata`).
- Build/dev: setuptools, setuptools_scm, pytest, mypy, pylint, black, isort.

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
- **Tests run via plain `pytest`**, not `spin test`. Integration tests
  shell out to `spin` themselves to exercise the plugin end-to-end.
- Run provisioning tests only in case something for the provisioning has
  changed.
- **`spin <task>` is for exploratory verification** — e.g., running
  `spin sbom assemble` / `spin sbom enrich` to confirm the plugin
  actually produces the expected merged/enriched SBOM during development.
  It is not the test runner.
- Python ≥3.10.
- Pre-commit hooks (run via `prek`): mypy (strict), pylint, black, isort.

## Non-obvious

- **CycloneDX is the default format**; SPDX is reachable via the schema
  config, not a separate task.
- **`enrich` is independent of `assemble`** — both run on the project's
  output SBOM and can be invoked separately.
- **Metadata extraction requires a properly configured `pyproject.toml`** in
  the consuming project; missing fields surface as empty enrichments rather
  than errors.
