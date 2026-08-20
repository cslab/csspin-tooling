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

"""Unit tests for the csspin_tooling.sbomqs default policy handling."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Mocking csspin modules to allow importing the sbomqs module without
# requiring a full csspin environment (@task does spin magic that needs to be
# mocked).
for _mod in (
    "csspin.tree",
    "csspin_python.python",
):
    sys.modules.setdefault(_mod, MagicMock())

from csspin_tooling.sbomqs import configure, default_policy_file  # noqa: 402


def test_default_policy_file() -> None:
    """default_policy_file resolves to the bundled, existing default."""
    resolved = default_policy_file(MagicMock())
    assert resolved.name == "default.yaml"
    assert resolved.exists()


def test_configure_resolves_callable_default() -> None:
    """configure resolves the callable policy_file default to a concrete path."""
    cfg = MagicMock()
    cfg.sbomqs = {"policy_file": default_policy_file}
    configure(cfg)
    assert cfg.sbomqs["policy_file"] == default_policy_file(cfg)


def test_configure_keeps_override() -> None:
    """A configured policy_file is left untouched by configure."""
    cfg = MagicMock()
    cfg.sbomqs = {"policy_file": "/some/custom/policy.yaml"}
    configure(cfg)
    assert cfg.sbomqs["policy_file"] == "/some/custom/policy.yaml"
