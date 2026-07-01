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
assembly and enrichment for CONTACT Elements-based projects. It downloads and
manages `sbomasm`_ and exposes two separate tasks: one to merge multiple
`CycloneDX`_ SBOM files into a single top-level SBOM, and one to enrich the
result with CONTACT Elements-specific metadata extracted from the Python
project configuration. A single SBOM is supported too — in that case the merge
step is a pass-through and only the enrichment step modifies the file.

The ``sbomasm`` plugin uses the ``csspin-python.python`` plugin to determine the
metadata for the enrichment step. These include the project name, version,
author, supplier, and license. Other sources of metadata are currently not
supported.

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

How to assemble and enrich an SBOM?
###################################

Both tasks hook into the ``sbomasm`` task group and the ``sbom`` workflow. If
`csspin-workflows.stdworkflows`_ is enabled, they run in the following order:

* ``sbomasm assemble`` collects all ``*.cdx.json`` files in the current
  directory (excluding the output file) and merges them into the output file.
  With a single input file the merge is a pass-through copy.
* ``sbomasm enrich`` then edits the output file in place, applying project
  metadata (name, version, author, supplier, license) to the primary component.
  The following fields must be present in the project's
  metadata (i.e. in defined via ``pyproject.toml``); the task aborts if any are
  missing:

  * ``name`` (e.g. ``customer.plm``)
  * ``version`` (e.g. ``v1.2.3``)
  * ``license`` — SPDX expression, e.g. ``MIT``
  * Author information — each author must have both a name and an email
    address. The expected format depends on the build backend:

    ``pyproject.toml`` (PEP 621):

    .. code-block:: toml

        [project]
        authors = [
            {name = "Good Employee", email = "good.employee@work.com"},
        ]

    ``setup.py`` / ``setup.cfg``:

    .. code-block:: python

        author = "Good Employee"
        author_email = "good.employee@work.com"

.. code-block:: console
    :caption: Assemble and enrich

    spin sbomasm assemble
    spin sbomasm enrich

The output file defaults to ``<project_name>.cdx.json``. Its location can be
overridden via the ``sbomasm.output_file`` option.

``csspin_tooling.sbomasm`` schema reference
###########################################

.. include:: sbomasm_schemaref.rst
