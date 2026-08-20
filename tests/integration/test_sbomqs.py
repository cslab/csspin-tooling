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

"""Integration tests for the csspin_tooling.sbomqs tasks.

These exercise the real sbomqs binary, since whether a license string counts as
a valid SPDX expression, or violates a policy, is sbomqs' verdict, not ours.
"""

from __future__ import annotations

import subprocess
from pathlib import Path as PathlibPath

import pytest

from .helpers import SBOMS, YAML_SBOMQS, execute_spin


def _run_task(task: str, sbom: str, env: PathlibPath) -> None:
    """Run ``spin sbomqs <task>`` against one of the fixture SBOMs.

    The SBOM path goes in as posix, since execute_spin splits its command with
    shlex, which would eat the backslashes of a Windows path.
    """
    execute_spin(
        yaml=YAML_SBOMQS,
        env=env,
        cmd=f"-p sbomqs.input_file={(SBOMS / sbom).as_posix()} sbomqs {task}",
    )


@pytest.mark.integration
def test_comp_valid_licenses_accepts_valid_licenses(sbomqs_env: PathlibPath) -> None:
    """The task passes on an SBOM whose licenses sbomqs can all validate."""
    _run_task("comp-valid-licenses", "valid-licenses.cdx.json", sbomqs_env)


@pytest.mark.integration
def test_comp_valid_licenses_rejects_invalid_license(sbomqs_env: PathlibPath) -> None:
    """The task dies on a license that is not a valid SPDX expression."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_task("comp-valid-licenses", "invalid-licenses.cdx.json", sbomqs_env)


@pytest.mark.integration
def test_policy_accepts_compliant_sbom(sbomqs_env: PathlibPath) -> None:
    """The task passes on an SBOM that violates none of the default policy rules."""
    _run_task("policy", "valid-licenses.cdx.json", sbomqs_env)


@pytest.mark.integration
def test_policy_rejects_prohibited_license(sbomqs_env: PathlibPath) -> None:
    """The task dies on a component carrying a blacklisted (GPL) license."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_task("policy", "policy-violation.cdx.json", sbomqs_env)
