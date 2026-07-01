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

"""Module implementing the SBOM quality gate plugin for spin."""

from __future__ import annotations

import os
import sys
from importlib import resources
from tempfile import TemporaryDirectory

from csspin import (
    Verbosity,
    config,
    die,
    download,
    exists,
    extract,
    group,
    info,
    setenv,
    sh,
)
from csspin.tree import ConfigTree
from path import Path


def default_policy_file(cfg: ConfigTree) -> Path:  # pylint: disable=unused-argument
    """Return the path to the bundled default policy file."""
    return Path(resources.files("csspin_tooling") / "policies/default.yaml")


defaults = config(
    version="2.0.9",
    install_dir="{spin.data}/csspin_tooling/sbomqs",
    input_file="{spin.project_name}.cdx.json",
    policy_file=default_policy_file,
)


def configure(cfg: ConfigTree) -> None:
    """Resolve callable defaults in the sbomqs subtree to concrete values."""
    for key, value in cfg.sbomqs.items():
        if callable(value):
            cfg.sbomqs[key] = value(cfg)


def provision(cfg: ConfigTree) -> None:
    """Download the managed sbomqs binary."""
    _provision_sbomqs(cfg)


def init(cfg: ConfigTree) -> None:
    """Make the managed sbomqs binary discoverable on ``PATH``."""
    sbomqs_dir = cfg.sbomqs.install_dir / cfg.sbomqs.version
    setenv(PATH=os.pathsep.join((sbomqs_dir, "{PATH}")))


@group()
def sbomqs(cfg: ConfigTree) -> None:  # pylint: disable=unused-argument
    """sbomqs-based SBOM quality gating."""


@sbomqs.task(when="sbom:quality")
def policy(cfg: ConfigTree) -> None:
    """Gate the SBOM against the policy and exit non-zero on violations."""
    sbom = cfg.sbomqs.input_file
    if not exists(sbom):
        die(f"Cannot gate {sbom}: file does not exist.")

    policy_file = cfg.sbomqs.policy_file
    info(f"Check {sbom} against policy {policy_file}")
    extra = ["-o", "table"] if cfg.verbosity > Verbosity.NORMAL else []
    sh("sbomqs", "policy", "-f", str(policy_file), *extra, str(sbom))


# -- Internals -----------------------------------------------------------------
def _provision_sbomqs(cfg: ConfigTree) -> None:
    """Downloads sbomqs"""
    version = cfg.sbomqs.version
    sbomqs_install_dir = cfg.sbomqs.install_dir / version

    if exists(sbomqs_install_dir / f"sbomqs{cfg.platform.exe}"):
        info(f"Using cached sbomqs ({sbomqs_install_dir})")
        return

    info("Installing sbomqs")
    archive = (
        f"sbomqs_{version}_Windows_x86_64.tar.gz"
        if sys.platform == "win32"
        else f"sbomqs_{version}_Linux_x86_64.tar.gz"
    )

    with TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / archive
        download(
            f"https://github.com/interlynk-io/sbomqs/releases/download/v{version}/{archive}",
            archive_path,
        )
        extract(archive_path, sbomqs_install_dir, f"sbomqs{cfg.platform.exe}")
