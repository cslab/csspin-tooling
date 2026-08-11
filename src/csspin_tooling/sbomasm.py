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

"""Module implementing the SBOM assembly plugin for spin."""

from __future__ import annotations

import os
import sys
from tempfile import TemporaryDirectory

from csspin import (
    backtick,
    config,
    die,
    download,
    exists,
    extract,
    group,
    info,
    setenv,
)
from csspin.tree import ConfigTree
from path import Path

defaults = config(
    version="2.0.10",
    install_dir="{spin.data}/csspin_tooling/sbomasm",
    output_file="{spin.project_name}.cdx.json",
    format=config(spec="cyclonedx", version="1.6"),
    primary_sbom="{spin.project_name}*.python_sbom.cdx.json",
    requires=config(spin=["csspin_python.python"]),
)


def provision(cfg: ConfigTree) -> None:
    """Provision the plugin"""
    _provision_sbomasm(cfg)


def init(cfg: ConfigTree) -> None:
    """Make the managed sbomasm binary discoverable on ``PATH``."""
    sbomasm_dir = cfg.sbomasm.install_dir / cfg.sbomasm.version
    setenv(PATH=os.pathsep.join((sbomasm_dir, "{PATH}")))


@group()
def sbomasm(cfg: ConfigTree) -> None:  # pylint: disable=unused-argument
    """sbomasm-based SBOM assembly."""


@sbomasm.task(when="sbom:assemble")
def assemble(cfg: ConfigTree) -> None:
    """Merge the top-level SBOMs into a single one."""
    _assemble_sbom(cfg)


# -- Internals -----------------------------------------------------------------
def _provision_sbomasm(cfg: ConfigTree) -> None:
    """Downloads sbomasm"""
    version = cfg.sbomasm.version
    sbomasm_install_dir = cfg.sbomasm.install_dir / version

    if exists(sbomasm_install_dir / f"sbomasm{cfg.platform.exe}"):
        info(f"Using cached sbomasm ({sbomasm_install_dir})")
        return

    info("Installing sbomasm")
    archive = (
        f"sbomasm_{version}_Windows_x86_64.tar.gz"
        if sys.platform == "win32"
        else f"sbomasm_{version}_Linux_x86_64.tar.gz"
    )

    with TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / archive
        download(
            f"https://github.com/interlynk-io/sbomasm/releases/download/v{version}/{archive}",
            archive_path,
        )
        extract(archive_path, sbomasm_install_dir, f"sbomasm{cfg.platform.exe}")


def _assemble_sbom(cfg: ConfigTree) -> None:
    """Merge SBOMs in the working directory into ``cfg.sbomasm.output_file``.

    The primary SBOM is resolved from the ``cfg.sbomasm.primary_sbom`` glob and
    extended with every other ``*.cdx.json`` file found next to it. A glob that
    matches nothing is a hard error; if it matches several files the first
    (sorted) one is used as the primary and the rest are merged in as regular
    inputs. With no other SBOMs the primary is copied through unchanged.
    """
    output = Path(cfg.sbomasm.output_file)

    primary_matches = sorted(p.name for p in Path().glob(cfg.sbomasm.primary_sbom))
    if not primary_matches:
        die(f"No primary SBOM matching {cfg.sbomasm.primary_sbom!r} found.")
        return
    primary = primary_matches[0]
    if len(primary_matches) > 1:
        info(
            f"Multiple primary SBOMs matched {cfg.sbomasm.primary_sbom!r}: "
            f"{primary_matches}; using {primary}."
        )

    others = sorted(
        p.name
        for p in Path().glob("*.cdx.json")
        if p.name not in {output.name, primary}
    )
    info(f"Found {len(others)} SBOM(s) to merge into {primary}: {others}")

    if not others:
        output.write_text(Path(primary).read_text(encoding="utf-8"), encoding="utf-8")
        info(f"Single SBOM {primary} copied to {output}")
        return

    args = [
        "sbomasm",
        "assemble",
        "--flatMerge",
        "--primary",
        primary,
    ]
    if cfg.sbomasm.format.spec.lower() == "spdx":
        args.append("--outputSpecSpdx")
    args += ["--outputSpecVersion", cfg.sbomasm.format.version]
    args.extend(others)

    sbom_text = backtick(*args)
    output.write_text(sbom_text, encoding="utf-8")
    info(f"Merged {len(others)} SBOM(s) into {primary} -> {output}")
