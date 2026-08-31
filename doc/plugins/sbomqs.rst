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

.. _csspin_tooling.sbomqs:

=====================
csspin_tooling.sbomqs
=====================

The ``csspin_tooling.sbomqs`` plugin gates an SBOM against a quality policy.
It downloads and manages `sbomqs`_ and exposes two tasks against the project's
`CycloneDX`_ SBOM: ``sbomqs policy`` runs ``sbomqs policy``, and
``sbomqs comp-valid-licenses`` fails on components whose license sbomqs cannot
validate. Both exit non-zero on a violation, so they can be used as blocking
gates e.g., in CI.

How to set up the ``csspin_tooling.sbomqs`` plugin?
###################################################

For using the ``csspin_tooling.sbomqs`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_tooling.sbomqs``

    spin:
        project_name: mypkg
    plugin_packages:
        - csspin-tooling
    plugins:
        - csspin_tooling.sbomqs

Provisioning downloads sbomqs into the spin data directory and makes it
available for all subsequent tasks:

.. code-block:: console
    :caption: Provisioning the project including sbomqs

    spin provision

How to gate an SBOM?
####################

The ``sbomqs policy`` task gates the SBOM configured via ``sbomqs.input_file``
(default ``<project_name>.cdx.json``) against the policy. It is a standalone
command group, invoked after ``spin sbom`` has produced the SBOM:

.. code-block:: console
    :caption: Gate the SBOM

    spin sbomqs policy

When the SBOM violates the policy, the task terminates with a non-zero exit code.

How to check license validity?
##############################

The ``sbomqs comp-valid-licenses`` task fails when a component carries a license
that sbomqs cannot validate. It uses the ``comp_valid_licenses`` feature, which
checks each license for compliance with the SPDX license expression
specification (SPDX-listed IDs, ``LicenseRef-`` references, and
``AND``/``OR``/``WITH`` expressions) and rejects only those that are not
valid SPDX expressions:

.. code-block:: console
    :caption: Check component licenses

    spin sbomqs comp-valid-licenses

The task lists the offending components and terminates with a non-zero exit
code when any component has an invalid (or missing) license.

How to ignore a component's license findings?
#############################################

Some packages carry a deprecated license classifier or another
non-SPDX-compliant license value, which fails the check. Add the package name to
``sbomqs.comp_valid_licenses_ignored_components`` to suppress it:

.. code-block:: yaml
    :caption: Ignoring a component's license findings

    sbomqs:
      comp_valid_licenses_ignored_components:
        - aiofiles

This might be appropriate for some time. The recommendation is to inform the
maintainer about the fact that their project metadata is not compliant with PEP
639, so they become aware of that and may fix it soon, so the package can be
removed from the suppression list. The goal is to not have any package on this
suppression list.

How to use a custom policy?
###########################

When ``sbomqs.policy_file`` is unset, the plugin uses the policy bundled with
the package. The default blacklists copyleft licenses incompatible with
commercial distribution (``GPL-.*``, ``AGPL-.*``, ``EUPL-.*``, and the
``CC-BY-SA``/``CC-BY-NC``/``CC-BY-ND`` family; ``LGPL-*`` is exempt) and
requires every component to carry a ``name``, ``version``, and ``license``.

Set ``sbomqs.policy_file`` to a local path to replace the bundled default
entirely:

.. code-block:: bash
    :caption: Using a custom policy

    spin -p sbomqs.policy_file=/path/to/policy.yaml sbomqs policy

``csspin_tooling.sbomqs`` schema reference
##########################################

.. include:: sbomqs_schemaref.rst
