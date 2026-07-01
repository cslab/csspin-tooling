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

"""Module implementing the SBOM assembly and enrichment plugin for spin."""

from __future__ import annotations

import email.utils
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
from csspin_python.python import get_project_metadata
from path import Path

defaults = config(
    version="2.0.8",
    install_dir="{spin.data}/csspin_tooling/sbomasm",
    output_file="{spin.project_name}.cdx.json",
    format=config(spec="cyclonedx", version="1.6"),
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
    """sbomasm-based SBOM assembly and enrichment."""


@sbomasm.task(when="sbom:assemble")
def assemble(cfg: ConfigTree) -> None:
    """Merge the top-level SBOMs into a single one (no enrichment)."""
    _assemble_sbom(cfg)


@sbomasm.task(when="sbom:enrich")
def enrich(cfg: ConfigTree) -> None:
    """Enrich the assembled SBOM with project metadata."""
    _enrich_sbom(cfg)


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

    With a single input, the file is copied through unchanged — ``sbomasm
    assemble`` rejects single-input invocations. Enrichment is handled
    separately by :func:`_enrich_sbom`.
    """
    output = Path(cfg.sbomasm.output_file)
    sboms = {path for path in Path().glob("*.cdx.json") if output != path}
    info(f"Found {len(sboms)} SBOM(s) to assemble: {[str(p) for p in sboms]}")

    if not sboms:
        die("No SBOMs found to assemble.")
        return

    if len(sboms) == 1:
        single_sbom = sboms.pop()
        output.write_text(single_sbom.read_text(encoding="utf-8"), encoding="utf-8")
        info(f"Single SBOM {single_sbom} copied to {output}")
        return

    metadata = get_project_metadata(cfg.spin.project_root, cfg.python.index_url)
    args = [
        "sbomasm",
        "assemble",
        "-m",
        "-n",
        metadata.get("name", "unknown"),
        "-v",
        metadata.get("version", "0.0.0"),
        "-t",
        "application",
        "-e",
        cfg.sbomasm.format.version,
    ]
    if cfg.sbomasm.format.spec.lower() == "spdx":
        args.append("-s")
    args.extend(str(p) for p in sboms)

    sbom_text = backtick(*args)
    output.write_text(sbom_text, encoding="utf-8")
    info(f"Merged {len(sboms)} SBOMs into {output}")


def _enrich_sbom(cfg: ConfigTree) -> None:
    """Enrich ``cfg.sbomasm.output_file`` in place via ``sbomasm edit``."""
    output = Path(cfg.sbomasm.output_file)
    if not exists(output):
        die(f"Cannot enrich {output}: file does not exist.")

    metadata = get_project_metadata(cfg.spin.project_root, cfg.python.index_url)

    if not (name := metadata.get("name")):
        die("Project metadata is missing 'name'.")
    if not (version := metadata.get("version")):
        die("Project metadata is missing 'version'.")
    if not (license_id := metadata.get("license")):
        die("Project metadata is missing 'license'.")

    authors = _parse_authors(
        author_name=metadata.get("author", "").strip(),
        author_email=metadata.get("author_email", "").strip(),
    )

    args = [
        "sbomasm",
        "edit",
        "--subject",
        "primary-component",
        "--name",
        name,
        "--version",
        version,
        "--author",
        authors,
        "--license",
        license_id,
        str(output),
    ]

    info(f"Enriching SBOM {output}")
    sbom_text = backtick(*args)
    output.write_text(sbom_text, encoding="utf-8")
    info(f"Enriched SBOM written to {output}")


def _parse_authors(author_name: str, author_email: str) -> str:
    """
    Parse RFC 2822 Author-email metadata and return a comma-separated string in
    sbomasm-acceptable format ('name (email)' or multiple authors,
    comma-separated).
    """
    if not author_email:
        die("Project metadata has no Author-email field.")
        return ""

    entries = email.utils.getaddresses([author_email])

    # setup.py case: single bare address paired with a separate Author field
    if len(entries) == 1 and not entries[0][0] and author_name:
        entries = [(author_name, entries[0][1])]

    for name, addr in entries:
        if not name:
            die(f"Author entry '{addr}' has no name; all authors require a name.")
            return ""
        if not addr:
            die(f"Author entry '{name}' has no email; all authors require an email.")
            return ""

    return ", ".join(f"{name} ({addr})" for name, addr in entries)
