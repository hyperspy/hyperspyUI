Cut a Release
=============

Create a PR _from_ the upstream repository (this branch needs to live in the
upstream to access to the github secrets) and go through the following steps:

**Preparation**
- Update and check changelog in `CHANGES.rst`
- Bump version in `hyperspyui/version.py`

**Tag and release**
:warning: this is a point of no return point :warning:
- push tag (`vx.y.z`) to the upstream repository and the following will be triggered:
  - creation of a Github Release
  - build wheels and upload them to pypi
  - build the doc and push it to the `gh-pages` branch which will in turn publish
    it to https://hyperspy.org/hyperspyUI

**Post-release action**
- Increment the version and set it back to dev: `vx.y.z.dev0`
- Prepare `CHANGES.rst` for development
- Merge the PR

Follow-up
=========

- Tidy up and close corresponding milestone
- A PR to the conda-forge feedstock will be created by the conda-forge bot

