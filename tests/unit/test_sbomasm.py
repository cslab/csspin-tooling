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

"""Unit tests for csspin_tooling.sbomasm._parse_authors"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mocking csspin modules to allow importing the sbomasm module without
# requiring a full csspin environment (@task does spin magic that needs to be
# mocked).
for _mod in (
    "csspin.tree",
    "csspin_python.python",
):
    sys.modules.setdefault(_mod, MagicMock())

from csspin_tooling.sbomasm import _parse_authors  # noqa: 402


@pytest.mark.parametrize(
    "author_name, author_email, expected",
    [
        pytest.param(
            # setup.py-like (if both set)
            "Employee",
            "employee@example.com",
            "Employee (employee@example.com)",
            id="setup.py-name-and-bare-email",
        ),
        pytest.param(
            # pyproject.toml-like: name + email in Author-email
            "",
            "Employee <employee@example.com>",
            "Employee (employee@example.com)",
            id="pyproject-single-name-email",
        ),
        pytest.param(
            # pyproject.toml-like: multiple name+email pairs
            "",
            "Employee <employee@example.com>, Other <other@example.com>",
            "Employee (employee@example.com), Other (other@example.com)",
            id="pyproject-multiple-name-email",
        ),
    ],
)
def test_parse_authors(author_name: str, author_email: str, expected: str) -> None:
    """Test that _parse_authors returns the expected result for valid inputs."""
    result = _parse_authors(author_name=author_name, author_email=author_email)
    assert result == expected


@pytest.mark.parametrize(
    "author_name, author_email",
    [
        pytest.param("", "", id="both-empty"),
        pytest.param("Employee", "", id="name-only-no-email"),
        pytest.param("", "employee@example.com", id="bare-email-no-name"),
        pytest.param(
            "",
            "employee@example.com, other@example.com",
            id="multiple-bare-emails-no-names",
        ),
        pytest.param(
            "",
            "Employee <employee@example.com>, other@example.com",
            id="mixed-named-and-bare",
        ),
        pytest.param("", "<employee@example.com>", id="angle-bracket-only-no-name"),
    ],
)
def test_parse_authors_dies(author_name: str, author_email: str) -> None:
    """Test that _parse_authors dies for invalid inputs."""
    with patch("csspin_tooling.sbomasm.die", side_effect=SystemExit(1)):
        with pytest.raises(SystemExit):
            _parse_authors(author_name=author_name, author_email=author_email)
