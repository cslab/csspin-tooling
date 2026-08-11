# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CONTACT Software GmbH
# https://www.contact-software.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for csspin_tooling.sbomasm"""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# Mocking csspin modules to allow importing the sbomasm module without
# requiring a full csspin environment (@task does spin magic that needs to be
# mocked).
for _mod in (
    "csspin.tree",
    "csspin_python.python",
):
    sys.modules.setdefault(_mod, MagicMock())

from csspin_tooling.sbomasm import _assemble_sbom  # noqa: 402


@pytest.fixture(autouse=True)
def _silence_info():
    """Silence csspin ``info``, which needs a full config tree to run."""
    with patch("csspin_tooling.sbomasm.info"):
        yield


def _make_cfg(
    *,
    output_file: str = "cs.template.cdx.json",
    primary_sbom: str = "cs.template*.python_sbom.cdx.json",
    spec: str = "cyclonedx",
    version: str = "1.6",
) -> SimpleNamespace:
    """Build a minimal cfg stub for :func:`_assemble_sbom`."""
    return SimpleNamespace(
        sbomasm=SimpleNamespace(
            output_file=output_file,
            primary_sbom=primary_sbom,
            format=SimpleNamespace(spec=spec, version=version),
        )
    )


def test_assemble_no_primary_match_dies(tmp_path, monkeypatch) -> None:
    """Fail when the primary glob resolves to nothing."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "other.cdx.json").write_text("{}", encoding="utf-8")

    with patch("csspin_tooling.sbomasm.die", side_effect=SystemExit(1)) as die:
        with pytest.raises(SystemExit):
            _assemble_sbom(_make_cfg())
    die.assert_called_once()


def test_assemble_single_primary_copied_through(tmp_path, monkeypatch) -> None:
    """With only the primary present, copy it through without invoking sbomasm."""
    monkeypatch.chdir(tmp_path)
    primary = tmp_path / "cs.template.linux_x86_64.python_sbom.cdx.json"
    primary.write_text('{"primary": true}', encoding="utf-8")

    with patch("csspin_tooling.sbomasm.backtick") as backtick:
        _assemble_sbom(_make_cfg())

    backtick.assert_not_called()
    output = tmp_path / "cs.template.cdx.json"
    assert output.read_text(encoding="utf-8") == '{"primary": true}'


def test_assemble_multiple_primary_takes_first(tmp_path, monkeypatch) -> None:
    """With multiple primary matches, use the first (sorted) and merge the rest."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cs.template.a.python_sbom.cdx.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cs.template.b.python_sbom.cdx.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cs.template.js_sbom.cdx.json").write_text("{}", encoding="utf-8")

    with patch("csspin_tooling.sbomasm.backtick", return_value="{}") as backtick:
        _assemble_sbom(_make_cfg())

    args = list(backtick.call_args.args)
    assert args[:4] == ["sbomasm", "assemble", "--flatMerge", "--primary"]
    assert args[4] == "cs.template.a.python_sbom.cdx.json"
    # Every other SBOM (including the unused primary match) is appended.
    assert "cs.template.b.python_sbom.cdx.json" in args
    assert "cs.template.js_sbom.cdx.json" in args


def test_assemble_appends_others_and_excludes_output(tmp_path, monkeypatch) -> None:
    """The primary is passed via --primary; every other SBOM but the output is appended."""
    monkeypatch.chdir(tmp_path)
    primary = tmp_path / "cs.template.linux_x86_64.python_sbom.cdx.json"
    primary.write_text("{}", encoding="utf-8")
    (tmp_path / "cs.template.js_sbom.cdx.json").write_text("{}", encoding="utf-8")
    # A stale previous output must never be merged back in.
    (tmp_path / "cs.template.cdx.json").write_text("{}", encoding="utf-8")

    with patch(
        "csspin_tooling.sbomasm.backtick", return_value='{"merged": true}'
    ) as backtick:
        _assemble_sbom(_make_cfg())

    args = list(backtick.call_args.args)
    assert "--primary" in args
    assert args[args.index("--primary") + 1] == primary.name
    assert "cs.template.js_sbom.cdx.json" in args
    assert "cs.template.cdx.json" not in args
    # CycloneDX output carries the configured spec version and no SPDX flag.
    assert args[args.index("--outputSpecVersion") + 1] == "1.6"
    assert "--outputSpecSpdx" not in args
    assert (tmp_path / "cs.template.cdx.json").read_text(
        encoding="utf-8"
    ) == '{"merged": true}'


def test_assemble_spdx_adds_flag(tmp_path, monkeypatch) -> None:
    """SPDX output adds the --outputSpecSpdx flag."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cs.template.python_sbom.cdx.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cs.template.js_sbom.cdx.json").write_text("{}", encoding="utf-8")

    with patch("csspin_tooling.sbomasm.backtick", return_value="{}") as backtick:
        _assemble_sbom(_make_cfg(spec="spdx"))

    assert "--outputSpecSpdx" in backtick.call_args.args


def test_assemble_writes_output_to_configured_directory(tmp_path, monkeypatch) -> None:
    """A directory-qualified output_file is honored, not collapsed to the cwd."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cs.template.python_sbom.cdx.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cs.template.js_sbom.cdx.json").write_text("{}", encoding="utf-8")
    (tmp_path / "dist").mkdir()

    with patch("csspin_tooling.sbomasm.backtick", return_value='{"merged": true}'):
        _assemble_sbom(_make_cfg(output_file="dist/cs.template.cdx.json"))

    assert (tmp_path / "dist" / "cs.template.cdx.json").read_text(
        encoding="utf-8"
    ) == '{"merged": true}'
    assert not (tmp_path / "cs.template.cdx.json").exists()
