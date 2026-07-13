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

"""Fetches the VEX file for a given project from Dependency-Track."""

import json
import re
from dataclasses import dataclass

import requests
from click import STRING
from csspin import argument, config, die, info, mkdir, task, writetext
from csspin.tree import ConfigTree
from path import Path

FILENAME_FALLBACK = "vex.json"

# -- Spin task -----------------------------------------------------------------
defaults = config(
    project_name="{spin.project_name}",
    target_directory="{spin.project_root}",
    cyclonedx_version="1.6",
)


@task()
def fetch_vex(
    cfg: ConfigTree,
    project_version: argument(type=STRING, required=True),  # type: ignore[valid-type]
) -> None:
    """Automated VEX file download for Dependency-Track.

    Fetches the VEX data for the configured project from the configured
    Dependency-Track instance and stores it as a JSON located in the configured
    target directory."""

    # input validation
    required_inputs = (
        (cfg.fetch_vex.deptrack_url, "fetch_vex.deptrack_url"),
        (cfg.fetch_vex.deptrack_api_key, "fetch_vex.deptrack_api_key"),
        (cfg.fetch_vex.project_name, "fetch_vex.project_name"),
    )
    for value, desc in required_inputs:
        if not value:
            die(f"Required configuration value {desc} missing")

    target_project = Project(cfg.fetch_vex.project_name, project_version)
    deptrack = DepTrackAPI(
        cfg.fetch_vex.deptrack_url,
        cfg.fetch_vex.deptrack_api_key,
        cfg.fetch_vex.cyclonedx_version,
    )
    target_project.uuid = deptrack.get_uuid(target_project)
    info(
        f"Retrieved project UUID {target_project.uuid} "
        f"({target_project.name} {target_project.version}) from {deptrack.url}"
    )
    _write_vex(deptrack.get_vex(target_project), cfg.fetch_vex.target_directory)


# -- DepTrack API --------------------------------------------------------------
@dataclass
class Project:
    """Minimal representation of a Project as defined by Dependency-Track"""

    name: str
    version: str
    uuid: str | None = None


@dataclass
class DepTrackAPI:
    """Helper class to retrieve VEX data from Dependency-Track"""

    url: str
    api_key: str
    cyclonedx_version: str

    def get_uuid(self, project: Project) -> str:
        """Retrieves a project's UUID from DepTrack"""
        response = requests.get(
            f"{self.url}/api/v1/project/lookup",
            params={"name": project.name, "version": project.version},
            headers={"X-API-Key": self.api_key},
            timeout=10,
        )

        if not response.ok:
            die(f"Unable to get project UUID: ({response.status_code}) {response.text}")

        return response.json()["uuid"]  # type: ignore

    def get_vex(self, project: Project) -> dict:
        """Retrieves the project's VEX data as a dict"""
        response = requests.get(
            f"{self.url}/api/v1/vex/cyclonedx/project/{project.uuid}",
            params={"version": self.cyclonedx_version},
            headers={"X-API-Key": self.api_key},
            timeout=10,
        )

        if not response.ok:
            die(
                f"Unable to get VEX file from DepTrack: ({response.status_code}) {response.text}",
            )

        return response.json()  # type: ignore


# -- Internals -----------------------------------------------------------------
def _write_vex(vex_data: dict, target_dir: Path) -> None:
    """Serializes the VEX data to JSON and writes it to the given target directory.

    The file name is determined by :func:`_get_filename`. If the function cannot
    determine a filename based on the component metadata from the VEX data, a
    fallback will be used and an error will be logged."""
    filename = _get_filename(vex_data)
    info(f"Writing VEX data to {target_dir / filename}")

    mkdir(str(target_dir))
    writetext(filename, json.dumps(vex_data))

    if filename == FILENAME_FALLBACK:
        die(
            "Could not retrieve component metdata at /metadata/component."
            f"Please check your VEX file at {target_dir / filename} as it might be invalid."
        )


def _get_filename(vex_data: dict) -> str:
    """Generates the file name from the VEX data"""
    try:
        tracking_id: str = (
            f"{vex_data['metadata']['component']['name']}-"
            f"{vex_data['metadata']['component']['version']}"
        )
    except KeyError:
        return FILENAME_FALLBACK
    tracking_id = tracking_id.lower()
    tracking_id = re.sub(r"[^+\-a-z0-9]+", "_", tracking_id)
    return f"{tracking_id}.vex.json"
