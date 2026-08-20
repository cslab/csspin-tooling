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

"""Shared helpers for the integration tests."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path as PathlibPath

YAMLS = "tests/integration/yamls"
YAML_SBOMQS = "sbomqs.yaml"
SBOMS = PathlibPath(__file__).parent / "sboms"


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
