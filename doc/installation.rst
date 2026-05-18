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

======================
Installation and setup
======================

`csspin`_ must be installed.

For leveraging plugins from within the ``csspin-tooling`` plugin-package for
``csspin``, the plugin-package must be added to the list of plugin-packages
within a project's ``spinfile.yaml``.

.. code-block:: yaml
    :caption: Example: ``spinfile.yaml`` setup to enable the sbomasm plugin

    plugin_packages:
        - csspin-python
        - csspin-tooling
    plugins:
        - csspin_tooling.sbomasm
    python:
        version: "3.11.9"

After the setup is done, the plugin-package can be provisioned by executing the
following command within the project's directory:

.. code-block:: console

    spin provision

The plugins and their tasks defined in the plugins section of the
``spinfile.yaml`` can now be used:

.. code-block:: console

    spin sbom:assemble --help
