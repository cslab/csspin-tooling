.. -*- coding: utf-8 -*-
   Copyright (C) 2026 CONTACT Software GmbH
   https://www.contact-software.com/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

.. _csspin_tooling.fetch_vex:

========================
csspin_tooling.fetch_vex
========================

The ``csspin_tooling.fetch_vex`` plugin provides automated VEX downloads. The
tool connects to a given instance of Dependency-Track and retrieves the VEX
data for any given project. The target Dependency-Track instance and project
version can be configured via the configuration tree, so they can be adapted
via environment variables in pipeline jobs. The plugin is designed to
retrieve VEX files for production build pipelines, which can later be bundled
into the wheel that gets shipped to customers.

How to set up the ``csspin_tooling.fetch_vex`` plugin?
######################################################

For using the ``csspin_tooling.fetch_vex`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_tooling.fetch_vex``

    spin:
      project_name: "<your project name>"

    plugin_packages:
        - csspin-tooling
    plugins:
        - csspin_tooling.fetch_vex
    python:
        version: "3.11.9"
    fetch_vex:
        deptrack_url: "<your Dependency-Track URL>"
        deptrack_api_key: "<your Dependency-Track API key>"

Note that ``csspin_tooling.fetch_vex.deptrack_api_key`` is also required but
storing secrets in configuration files is highly discouraged. The API key should
be set via environment variable instead.

How to retrieve a VEX file?
###########################

To retrieve a VEX file, you will need an API key for the Dependency-Track
instance you are going to access. You also need the name of your project as it
is tracked in Dependency-Track and the project version you want to retrieve the
VEX file for. The project version is given directly via CLI.

For example, the required values can be set with environment variables:

.. code-block:: console
    :caption: Setting required configuration with environment variables

    export SPIN_TREE_FETCH_VEX__DEPTRACK_URL="<your Dependency-Track URL>"
    export SPIN_TREE_FETCH_VEX__DEPTRACK_API_KEY="<your API key>"

When everything is configured, call the plugin to download the VEX file:

.. code-block:: console
    :caption: Running the fetch_vex plugin

     spin fetch-vex <PROJECT_VERSION>

``csspin_tooling.fetch_vex`` schema reference
#############################################

.. include:: fetch_vex_schemaref.rst
