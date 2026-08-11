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

.. _csspin_tooling.sbomasm:

======================
csspin_tooling.sbomasm
======================

The ``csspin_tooling.sbomasm`` plugin provides SBOM (Software Bill of Materials)
assembly for CONTACT Elements-based projects. It downloads and manages
`sbomasm`_ and exposes a task that extends a primary `CycloneDX`_ SBOM with
every other SBOM found alongside it.

How to set up the ``csspin_tooling.sbomasm`` plugin?
####################################################

For using the ``csspin_tooling.sbomasm`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_tooling.sbomasm``

    plugin_packages:
        - csspin-python
        - csspin-tooling
    plugins:
        - csspin_tooling.sbomasm
    python:
        version: "3.11.9"

Provisioning downloads sbomasm into the spin data directory and makes it
available for all subsequent tasks:

.. code-block:: console
    :caption: Provisioning the project including sbomasm

    spin provision

How to assemble an SBOM?
########################

The ``sbomasm assemble`` task hooks into the ``sbomasm`` task group and the
``sbom`` workflow. It resolves the primary SBOM from the
``sbomasm.primary_sbom`` glob and merges every other ``*.cdx.json`` file in the
current directory (excluding the output file) into it. A glob matching nothing
is a hard error but if it matches several files, the first (sorted) one is the
primary and the rest are merged in as regular inputs. With only the primary
present, the merge is a pass-through copy.

.. code-block:: console
    :caption: Assemble

    spin sbomasm assemble

The output file defaults to ``<project_name>.cdx.json``. Its location can be
overridden via the ``sbomasm.output_file`` option.

``csspin_tooling.sbomasm`` schema reference
###########################################

.. include:: sbomasm_schemaref.rst
