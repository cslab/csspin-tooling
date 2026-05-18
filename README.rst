``csspin-tooling`` is maintained by `CONTACT Software GmbH`_ and provides
plugins for CONTACT Product Operations and Development (ConPod) workflows
using the `csspin`_ task runner.

The following plugins are available:

- ``csspin_tooling.sbomasm``: Assembles multiple CycloneDX SBOM files into a
  single enriched top-level SBOM using the `sbomasm`_ tool.

Prerequisites
-------------

`csspin`_ must be installed before using this package:

.. code-block:: console

   python -m pip install csspin

Using csspin-tooling
-------------------

Add the package and the desired plugins to your project's ``spinfile.yaml``:

.. code-block:: yaml

    spin:
      project_name: my_project

    plugin_packages:
      - csspin-python
      - csspin-tooling

    plugins:
      - csspin_tooling.sbomasm

    python:
      version: "3.11.9"

Provision the project to download sbomasm and install all dependencies:

.. code-block:: console

   spin provision

Assemble a top-level SBOM from all ``*.cdx.json`` files in the project root:

.. code-block:: console

   spin sbom --help

.. _`CONTACT Software GmbH`: https://contact-software.com
.. _`csspin`: https://pypi.org/project/csspin
.. _`sbomasm`: https://github.com/interlynk-io/sbomasm
