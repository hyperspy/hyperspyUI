
Changelog
*********

v1.3.0 (2023-05-04)
+++++++++++++++++++
- Update release workflow to remove deprecated github actions and use pypi API token instead of user/password (`#211 <https://github.com/hyperspy/hyperspyUI/pull/211>`_)
- Fix dependabot error when parsing github workflow  (`#212 <https://github.com/hyperspy/hyperspyUI/pull/212>`_)
- Fix import marker hyperspy 2.0  (`#216 <https://github.com/hyperspy/hyperspyUI/pull/216>`_)
- Add explicit support for python 3.11 (`#218 <https://github.com/hyperspy/hyperspyUI/pull/218>`_)
- Bump version of pyqode dependencies to support pyflakes >=2.5 (`#218 <https://github.com/hyperspy/hyperspyUI/pull/218>`_)


v1.2.0 (2023-03-16)
+++++++++++++++++++
- Pin third party action and fix tests and documentation GitHub workflow (`#206 <https://github.com/hyperspy/hyperspyUI/pull/206>`_)
- Pin pyflakes to 2.4 to keep pyqode.python working (`#206 <https://github.com/hyperspy/hyperspyUI/pull/206>`_)
- Add support for HyperSpy 2.0 (`#207 <https://github.com/hyperspy/hyperspyUI/pull/207>`_)
- Improve code quality using GitHub CodeQL and fix bugs (`#208 <https://github.com/hyperspy/hyperspyUI/pull/208>`_)

v1.1.5 (2022-04-27)
+++++++++++++++++++
* Fix numpy deprecation warning (`#203 <https://github.com/hyperspy/hyperspyUI/pull/203>`_)
* Add support for python 3.10 (`#204 <https://github.com/hyperspy/hyperspyUI/pull/204>`_)

v1.1.4
++++++
* Fix doc warning add workflow to publish the code on tag (`#198 <https://github.com/hyperspy/hyperspyUI/pull/198>`_)
* Add support for matplotlib 3.4.0 and increase hyperspy, matplotlib minimum requirement (`#199 <https://github.com/hyperspy/hyperspyUI/pull/199>`_)
* Fix checking animation writer availability (`#201 <https://github.com/hyperspy/hyperspyUI/pull/201>`_)
* Drop support for python 3.6 (`#202 <https://github.com/hyperspy/hyperspyUI/pull/202>`_)

v1.1.3
++++++

This is a maintenance release and the main highlights are:

* Fix issue with qt 5.12 on MacOS Big Sur
* Run test suite on Github Actions
* Add Release workflow on Github Actions

For a detailed list of all the changes
see `the commits in the GITHUB milestones 1.1.3
<https://github.com/hyperspy/hyperspyUI/milestone/8?closed=1>`_.

v1.1.2
++++++

This is a maintenance release and the main highlights are:

* Fix issue with embedded console on windows and python 3.8.
* Fix issue with jupyter_client v6.0 and ipykernel <5.2.
* Documentation improvement.

For a detailed list of all the changes
see `the commits in the GITHUB milestones 1.1.2
<https://github.com/hyperspy/hyperspyUI/milestone/7?closed=1>`_.


v1.1.1
++++++


This is a maintenance release and the main highlights are:

* Fix issue with recent matplotlib release (>=3.1).
* Add support for EELS zlp "also align".
* Add support for linux desktop integratin.

For a detailed list of all the changes
see `the commits in the GITHUB milestones 1.1.1
<https://github.com/hyperspy/hyperspyUI/milestone/6?closed=1>`_.


v1.1.0
++++++

This is a maintenance release and the main highlights are:

* Add HyperSpyUI on conda-forge
* Improve installation instruction (from pip and conda).
* Add support for pyqt5.
* Add continuous integration for windows, linux and macosx.
* Fix saving hspy file with hyperspy >=1.3.
* Fix image rotation.
* Add style editor.
* Add Help menu.
* Fix icon on macosx


For a detailed list of all the changes
see `the commits in the GITHUB milestones 1.1.0
<https://github.com/hyperspy/hyperspyUI/milestone/2?closed=1>`_.


