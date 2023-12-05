# Releasing a new HyperSpyUI version

To publish a new exSpy release do the following steps:

## Preparation

- In a pull request, prepare the release by running the `prepare_release.py` python script (e.g. `python prepare_release.py 2.0`) , which will do the following:
  - update the release notes in `CHANGES.rst` by running `towncrier`,
  - update the `setuptools_scm` fallback version in `pyproject.toml` (for a patch release, this will stay the same).
- Check release notes

**Tag and release**

- Create a tag e.g. `git tag -a v0.1.1 -m "HoloSpy version 0.1.1"`. The holospy version will
  be set at build time from the tag by `setuptools_scm`.
- Push tag to user fork for a test run `git push origin v0.1.1`. Will run the release
  workflow without uploading to PyPi
- :warning: this is a point of no return :warning: Push tag to HoloSpy repository to
  trigger release `git push upstream v0.1.1`:
  - The `release` workflow will run and upload the sdist and wheel to `pypi.org`
  - A Github release will be created
  - build the doc and push it to the `gh-pages` branch which will in turn publish
    it to https://hyperspy.org/hyperspyUI

**Post-release action**
- Merge the PR

Follow-up
=========

- Tidy up and close corresponding milestone
- A PR to the conda-forge feedstock will be created by the conda-forge bot
