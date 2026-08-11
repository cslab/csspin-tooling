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

.. This document contains the release notes for csspin-tooling. Each release is
   documented in a separate section, starting with the most recent release at
   the top.

   The release section must be renamed to the actual release tag with a prefixed
   "v". The date of the release must be in the format `Month Day, Year`/`"%B %d,
   %Y"`.

   At least one of these subsections must be present for each release:

   - Enhancements
   - Bug Fixes
   - Chores

   Each of these subsections must contain a bulleted list of changes made in the
   release. Each bullet must contain a short description of the change and a
   reference to the issue or merge request where the change was made.

   If required, the additional subsections can be added:

   - Breaking Changes
   - Migration Guide

=============
Release Notes
=============

v1.0.0
======

August 11, 2026

Enhancements
------------

- Add ``sbomasm`` plugin for assembling CycloneDX SBOMs
  (`!1 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/1>`_)
- Add ``fetch_vex`` plugin to download a project's VEX file from
  Dependency-Track (`!3
  <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/3>`_)
- Add ``sbomqs`` plugin as an SBOM quality gate
  (`!5 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/5>`_)
- ``fetch_vex`` now takes the project version directly via CLI instead of
  spin configuration (`!6
  <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/6>`_)

Chores
------

- Extend the primary SBOM instead of merging into a new root, and drop
  enrichment (`!4
  <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/4>`_)
- Update default sbomasm 2.0.3 -> 2.0.8
  (`!7 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/7>`_)
- Drop ``sbomasm.use`` and change ``sbomasm.install_dir``
  (`!8 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/8>`_)
- Add SonarQube analysis
  (`!9 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/9>`_)
- Update CI includes and stale references after move to pod/components
  (`!11
  <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/11>`_)

v1.0.0-rc1
===========

May 18, 2026

Enhancements
------------

- Add ``sbomasm`` plugin for assembling and enriching CycloneDX SBOMs
  (`!1 <https://code.contact.de/pod/components/csspin-tooling/-/merge_requests/1>`_)
