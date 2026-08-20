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

"""Integration test fixtures."""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path as PathlibPath
from typing import Generator

import pytest

from .helpers import YAML_SBOMQS, execute_spin


def short_tmp_dir(name: str, tmp_path_factory: pytest.TempPathFactory) -> PathlibPath:
    """Create a temp directory whose path stays below Windows' MAX_PATH limit.

    Pytest normally embeds the full test name into the temp directory, which
    easily exceeds Windows' 260-char MAX_PATH limit when the runner's base path
    is already long.  We truncate the name and append a short hash so it stays
    unique.

    On Windows we bypass tmp_path_factory's basetemp entirely. GitLab CI
    runners often set TEMP/TMP to the long build path, so even a short leaf
    name still overflows. Instead we create the directory directly under the
    system temp root (C:\\Windows\\Temp or equivalent) where the base is short.
    """
    suffix = hashlib.sha256(name.encode()).hexdigest()[:6]

    # TODO: Remove this override once the Windows GitLab runners no longer enforce
    # the 260-character MAX_PATH limit (i.e. after migrating to a setup with
    # LongPathsEnabled or a shorter base-temp path).
    max_name_len = 16
    short = f"{name[:max_name_len]}_{suffix}"

    if sys.platform == "win32":
        # On Windows: use the system drive root temp dir to keep total path short.
        drive = PathlibPath(tempfile.gettempdir()).anchor  # e.g. "C:\\"
        path = PathlibPath(drive) / "pytest-tmp" / short
        path.mkdir(parents=True, exist_ok=True)
        return path
    return tmp_path_factory.mktemp(short, numbered=True)


@pytest.fixture()
def tmp_path(
    tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
) -> Generator[PathlibPath, None, None]:
    """Like the built-in tmp_path, but with a short directory name."""
    yield short_tmp_dir(request.node.name, tmp_path_factory)


@pytest.fixture(scope="module")
def sbomqs_env(tmp_path_factory: pytest.TempPathFactory) -> PathlibPath:
    """A spin environment with sbomqs provisioned, shared across a test module."""
    env = short_tmp_dir("sbomqs", tmp_path_factory)
    execute_spin(yaml=YAML_SBOMQS, env=env, cmd="provision")
    return env
