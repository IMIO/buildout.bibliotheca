"""
Run with: bin/instance run cleanup_profile_versions.py

Auto-detects and removes stale profile-version entries from portal_setup
for packages that are recorded as having installed a GS profile, but are
no longer importable (i.e. removed from the buildout/environment).

Uses the same detection logic as Products.CMFPlone.browser.admin.Upgrade.missing_packages.
"""

import transaction
from importlib import import_module
from importlib.metadata import PackageNotFoundError, distribution

# Known false positives: packages whose profile is intentionally left behind
# (e.g. cleaned up by upgrade steps in plone.app.upgrade), so don't nuke them.
IGNORE = {"Products.CMFFormController"}

DRY_RUN = False  # set to False once you've reviewed the output


def find_missing_packages(setup):
    installed = sorted(
        {k.split(":")[0] for k in setup._profile_upgrade_versions.keys()}
    )
    missing = []
    for package in installed:
        if package in IGNORE:
            continue
        try:
            distribution(package)
        except PackageNotFoundError:
            try:
                import_module(package)
            except ModuleNotFoundError:
                missing.append(package)
    return missing


for site_id in app.objectIds():
    site = app._getOb(site_id, None)
    setup = getattr(site, "portal_setup", None)
    if setup is None:
        continue

    stale_packages = find_missing_packages(setup)
    if not stale_packages:
        print(f"[{site_id}] nothing stale")
        continue

    keys_to_remove = [
        k
        for k in list(setup._profile_upgrade_versions.keys())
        if k.split(":")[0] in stale_packages
    ]

    print(f"[{site_id}] stale packages: {stale_packages}")
    for k in keys_to_remove:
        print(f"[{site_id}] {'would remove' if DRY_RUN else 'removing'} {k}")
        if not DRY_RUN:
            del setup._profile_upgrade_versions[k]

if DRY_RUN:
    print("DRY_RUN=True, nothing committed. Review output, set DRY_RUN=False, rerun.")
else:
    transaction.commit()
    print("Done.")
