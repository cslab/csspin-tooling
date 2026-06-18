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

"""Unit test for csspin_tooling.fetch_vex._get_filename"""

import sys
from unittest.mock import MagicMock

# Mocking csspin modules to allow importing the sbomasm module without
# requiring a full csspin environment (@task does spin magic that needs to be
# mocked).
for _mod in (
    "csspin.tree",
    "csspin_python.python",
):
    sys.modules.setdefault(_mod, MagicMock())

import pytest  # noqa: 402

from csspin_tooling.fetch_vex import FILENAME_FALLBACK, _get_filename  # noqa: 402


@pytest.mark.parametrize(
    "vex_data, expected",
    [
        (
            {"metadata": {"component": {"name": "cs.foo", "version": "2026.2.0"}}},
            "cs_foo-2026_2_0.vex.json",
        ),
        (
            {"metadata": {"component": {"name": "CS.FOO", "version": "2026.2.0"}}},
            "cs_foo-2026_2_0.vex.json",
        ),
        ({}, FILENAME_FALLBACK),
        ({"metadata": {"component": {"name": "cs.foo"}}}, FILENAME_FALLBACK),
        ({"metadata": {"component": {"version": "2026.2.0"}}}, FILENAME_FALLBACK),
        ({"metadata": {"component": {}}}, FILENAME_FALLBACK),
        ({"metadata": {}}, FILENAME_FALLBACK),
    ],
)
def test_get_filename(vex_data, expected) -> None:
    """Tests that package metadata in the VEX file will be properly formatted as a file name."""
    assert _get_filename(vex_data) == expected
