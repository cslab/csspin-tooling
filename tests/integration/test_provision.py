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

"""Integration tests for csspin_tooling provisioning"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path as PathlibPath

import pytest

from .helpers import execute_spin

SBOMASM_VERSION = "2.0.3"
SBOMQS_VERSION = "2.0.12"


def _binary(
    tmp_path: PathlibPath, tool: str, version: str, install_subdir: str
) -> PathlibPath:
    exe = f"{tool}.exe" if sys.platform == "win32" else tool
    return tmp_path / install_subdir / version / exe


@pytest.mark.integration
@pytest.mark.parametrize(
    "tool, version, install_subdir",
    [
        ("sbomasm", SBOMASM_VERSION, "csspin_tooling/sbomasm"),
        ("sbomqs", SBOMQS_VERSION, "csspin_tooling/sbomqs"),
    ],
)
def test_provision(
    tmp_path: PathlibPath,
    tool: str,
    version: str,
    install_subdir: str,
) -> None:
    """Test the provision task of a tool plugin in various scenarios."""
    yaml = f"{tool}.yaml"
    execute_spin(yaml=yaml, env=tmp_path, cmd="cleanup")

    # 1. Check that provision downloads the tool and that the binary is
    #    executable.
    execute_spin(yaml=yaml, env=tmp_path, cmd="provision")

    binary = _binary(tmp_path, tool, version, install_subdir)
    assert binary.exists(), f"{tool} binary not found at {binary}"
    assert os.access(binary, os.X_OK), f"{tool} binary is not executable: {binary}"
    output = subprocess.check_output(
        [str(binary), "version"], encoding="utf-8", stderr=subprocess.STDOUT
    )
    assert version in output

    # 2. Ensure the tool's task group is runnable through spin (exits non-zero
    #    on failure, which execute_spin re-raises).
    group_run = execute_spin(yaml=yaml, env=tmp_path, cmd=tool)
    assert f"spin {tool}" in group_run

    # 3. Ensure that a second regular provision run uses the cached binary
    #    without re-downloading
    second_run = execute_spin(yaml=yaml, env=tmp_path, cmd="-v provision")
    assert f"using cached {tool}" in second_run.lower()
