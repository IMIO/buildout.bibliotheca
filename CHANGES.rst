CHANGELOG
=========

6.1.0-7 (unreleased)
--------------------

- Add ``scripts/`` helpers to repair items created before the
  ``library.*`` -> ``bibliotheca.*`` rename: ``fix_rename.py`` (rewrite stale
  FTI schema strings, purge orphaned browser layers, register the renamed
  layers) and ``realign_profiles.py`` (re-align GenericSetup profile versions).
  Run with ``bin/instance run scripts/<name>.py``.
  [remdub]

- bibliotheca.policy 3.1.2

  - Add upgrade step (1017 -> 1018) to fix ``library.*`` -> ``bibliotheca.*`` rename
    artifacts left in existing ZODBs: rewrite the stale ``patrimoine`` FTI schema
    string (fixes a ``RecursionError`` on ``lookupSchema``), purge the orphaned
    ``ILibraryCoreLayer`` / ``ILibraryPolicyLayer`` browser layers, and register
    the renamed ``IBibliothecaCoreLayer`` / ``IBibliothecaPolicyLayer`` layers so
    views/viewlets/tiles bound to them (e.g. the ``existingcontent`` tile) work.
    [remdub]

- bibliotheca.policy 3.1.1

  - Rename to bibliotheca.policy
    [bsuttor]

- bibliotheca.core 3.0.1

  - Rename to bibliotheca.core 
    [bsuttor]

- bibliotheca.policy 3.1.2

  - Add upgrade step (1017 -> 1018) to fix ``library.*`` -> ``bibliotheca.*`` rename
    artifacts left in existing ZODBs: rewrite the stale ``patrimoine`` FTI schema
    string (fixes a ``RecursionError`` on ``lookupSchema``), purge the orphaned
    ``ILibraryCoreLayer`` / ``ILibraryPolicyLayer`` browser layers, and register
    the renamed ``IBibliothecaCoreLayer`` / ``IBibliothecaPolicyLayer`` layers so
    views/viewlets/tiles bound to them (e.g. the ``existingcontent`` tile) work.
    [remdub]

- bibliotheca.policy 3.1.1

  - Rename to bibliotheca.policy
    [bsuttor]

- bibliotheca.core 3.0.1

  - Rename to bibliotheca.core 
    [bsuttor]


6.1.0-6 (2026-07-13)
--------------------

- pas.plugins.kimug 1.9.4

  - KEYC-132 : Use a lightweight endpoint for realm_exists method
    [remdub]


6.1.0-5 (2026-07-12)
--------------------

- library.policy 3.1.0

  - KEYC-132 : Set the modal property on the login action (portal_actions/user/login) at install and via an upgrade step
    [remdub]

  - KEYC-132 : Install pas.plugins.kimug by default and add an upgrade step to install it on existing sites
    [remdub]


6.1.0-4 (2026-07-08)
--------------------

- library.core 3.0.0

  - Switch to PEP 420 native namespace package.
    [remdub]

- library.policy 3.0.0

  - Switch to PEP 420 native namespace package.
    [remdub]

  - Migrate dev environment to Plone 6.1.5, buildout 5
    [remdub]

- Remove obsolete references to library.theme in buildout files
  [remdub]


6.1.0-3 (2026-07-07)
--------------------

- library.core 2.1.8

  - Use plone.app.discussion.behaviors.IAllowDiscussion
    plone.app.dexterity.behaviors.discussion.IAllowDiscussion has been deprecated
    [remdub]

  - Migrate dev environment to Plone 6.1.5 and buildout 5
    [remdub]

  - Migrate to Plone 6.1.4
    [boulch]

- Migrate to Plone 6.1.5
  [remdub]


6.1.0-2 (2026-03-24)
--------------------

- Migrate to Plone 6.1.4
  [boulch]


6.1.0-1 (2026-02-12)
--------------------

- Upgrade plone.app.upgrade to 3.3.1
    - Fix upgrading TinyMCE plugins with invalid/outdated plugins. @petschki (#351)
  [boulch]

- collective.upgrade in auto-checkout
  [remdub]

- library.core 2.1.7

    - BIBLIBDC-134 : Fix select2 display taxonomy term identifier instead of term label
      [boulch]

- Migrate to Plone 6.1.3
  [boulch]


6.0.9-10 (2025-10-10)
---------------------

- Demo for PyCon Finland 2025.
  [bsuttor, remdub]


6.0.9-9 (2025-07-01)
--------------------

- library.policy 2.0.6

  - BIBLI-81 : Improve installation (Faceted, Taxonomies)
    [boulch]


6.0.9-8 (2025-06-24)
--------------------

- library.policy 2.0.5

  - Remove obsolete `library.theme` completely
    All themes reside in https://github.com/IMIO/imio_library_themes/
    [laulaz]

  - Move viewlets registrations from obsolete `library.theme` to `library.policy`
    [laulaz]


6.0.9-7 (2025-06-23)
--------------------

- library.policy 2.0.4

  - Uninstall obsolete `library.theme` (it will later be removed)
    [boulch, laulaz]

  - Ensure unused `plone.patternslib` is not installed as it causes errors
    [boulch, laulaz]


6.0.9-6 (2025-06-18)
--------------------

- library.core 2.1.6

  - Fix collective.behavior.gallery.behaviors.folderish_gallery interface for patrimoine
    [boulch]


6.0.9-5 (2025-05-26)
--------------------

- library.policy 2.0.3

  - BIBLIBDC-125 : Set "banner" (instead of "preview") as default scale for collective.behavior.banner "banner_scale" [boulch]
    [boulch]

- Update to Plone 6.0.14
  [boulch]


6.0.9-4 (2025-02-04)
--------------------

- BIBLI-76 : Update plone.app.discussion from 4.0.2 to 4.1.2 (Fix recaptcha validation)
  [boulch]


6.0.9-3 (2025-01-14)
--------------------

- library.core 2.1.5

  - BIBLI-75 : Ignore displaying each items if not necessary to display it when rendering a "patrimoine" content
    [boulch]

- library.core 2.1.4

  - BIBLI-75 : Ignore displaying some items when rendering a "patrimoine" content
    [boulch]

- library.policy 2.0.2

  - Reinstall collective.behavior.gallery
    [boulch]

- library.core 2.1.3

  - Remove picture from comments. That don't work!
    [boulch]


6.0.9-2 (2024-12-17)
--------------------

- Update waitress 3.0.2
  [remdub]


6.0.9-1 (2024-12-16)
--------------------

- library.policy 2.0.1

  - BIBLI-73 : Let deprecated old library.theme. Need to be uninstall manually TTW.
    [boulch]

- Get released versions of library.policy and library.core for production
  [boulch]

- library.core 2.1.2

  - BIBLI-73 : Fix js for map
    [boulch, tlambert, laulaz]

- library.core 2.1.1

  - BIBLI-73 : Add monkeypatch to fix TTW resource calling
    [boulch]

- library.core 2.1.0

  - BIBLI-73 : Update to Plone6 (6.0.9)
    [boulch]

- library.policy 2.0.0

  - BIBLI-73 : Update to Plone6 (6.0.9)
    [boulch]

  - BIBLI-73 : Change default faceted view for "explorer" folders
    [boulch]

  - Migrate to Plone 6. Next steps!
    [boulch]

  - Migration to Plone6
    [boulch]

- Update to Plone 6.0.9
  [bsuttor]

- Update collective.plausible to 1.0a3
  [remdub]

- library.policy 1.1.17

  - WEB-4074 : Install collective.plausible
    [remdub]


5.2.3-10 (2023-12-15)
---------------------

- library.core 2.0.15

  - MBIBLIHAVA-3 : Fix "Impossible to add/save existing content tile" (view_template field : required must be False) issue : plone/plone.app.standardtiles#149
    [boulch]


5.2.3-9 (2023-11-21)
--------------------

- Update Plone from 5.2.5 to 5.2.8
  [boulch]

- library.policy 1.1.13

  - Add collective.big.bang dependency
    [boulch]


5.2.3-3-quick (2021-10-29)
--------------------------

- Fix rundeck links.
  [bsuttor]

5.2.3-2 (2021-10-27)
--------------------

- Remove useless (since Plone 5.2.2) Products.PloneHotfix20200121 = 1.1
  Removing this Hotfix with Plone 5.2.5 fix a char encoging in navigation menu.
  [boulch]


5.2.3-1 (2021-09-16)
--------------------

- library.core 2.0.14

  - Add an honeypot field to comment form 
    [boulch]

- iaweb.mosaic 1.1.0

  - MWEBIMI-25: Hide slides after the first one to improve page loading
    [mpeeters]

- library.policy 1.1.12

  - Add iaweb.mosaic as a requirement (to add slider in bibliotheca). 
    [boulch]

- Initial release
