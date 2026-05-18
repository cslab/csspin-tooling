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

import shlex
import subprocess
import sys
from pathlib import Path as PathlibPath

import pytest

YAMLS = "tests/integration/yamls"
SBOMASM_VERSION = "2.0.3"


def execute_spin(yaml: str, env: PathlibPath, cmd: str = "") -> str:
    """Run spin and return combined stdout; re-raise CalledProcessError with output."""
    base = [
        "spin",
        "-p",
        f"spin.data={env}",
        "-C",
        YAMLS,
        "--env",
        str(env),
        "-f",
        yaml,
    ]
    extra = shlex.split(cmd) if cmd else []
    try:
        return subprocess.check_output(
            base + extra,
            encoding="utf-8",
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as ex:
        print(ex.output)
        raise


def _binary(tmp_path: PathlibPath) -> PathlibPath:
    exe = "sbomasm.exe" if sys.platform == "win32" else "sbomasm"
    return tmp_path / "sbomasm" / SBOMASM_VERSION / exe


@pytest.mark.integration
def test_sbomasm_provision(tmp_path: PathlibPath) -> None:
    """Test the sbomasm provision task in various scenarios."""
    yaml = "sbomasm.yaml"
    execute_spin(yaml=yaml, env=tmp_path, cmd="cleanup")

    # 1. Check that when sbomasm.use is set, provision skips downloading the
    #    binary.
    execute_spin(
        yaml=yaml,
        env=tmp_path,
        cmd="-p sbomasm.use=sbomasm provision",
    )
    assert not _binary(
        tmp_path
    ).exists(), "Binary should not be downloaded when sbomasm.use is set"
    execute_spin(yaml=yaml, env=tmp_path, cmd="cleanup")

    # 2. Check that provision downloads sbomasm and that the binary is
    #    executable.
    execute_spin(yaml=yaml, env=tmp_path, cmd="provision")

    binary = _binary(tmp_path)
    assert binary.exists(), f"sbomasm binary not found at {binary}"
    output = subprocess.check_output(
        [str(binary), "version"], encoding="utf-8", stderr=subprocess.STDOUT
    )
    assert SBOMASM_VERSION in output

    # 3. Ensure that a second regular provision run uses the cached binary
    #    without re-downloading
    second_run = execute_spin(yaml=yaml, env=tmp_path, cmd="-v provision")
    assert "using cached sbomasm" in second_run.lower()
