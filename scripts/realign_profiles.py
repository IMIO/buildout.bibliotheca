# -*- coding: utf-8 -*-
"""Set the renamed profiles' last-applied versions (idempotent).

Run with:  bin/instance run scripts/realign_profiles.py

The library.* profile-version records were dropped in a first pass. This sets
the renamed bibliotheca.* profiles to the versions the library.* profiles had
recorded, so the add-ons show as installed and GenericSetup still offers any
genuine pending upgrade (e.g. bibliotheca.policy 1017 -> 1018, idempotent).
"""
import transaction
from zope.component.hooks import setSite

# renamed profile id -> version that its library.* predecessor last recorded.
TARGETS = {
    "bibliotheca.core:default": ("1005",),
    "bibliotheca.policy:default": ("1017",),
}


def main(app):
    total = 0
    for obj in app.objectValues():
        if getattr(obj, "portal_setup", None) is None:
            continue
        print("=== Site: /%s ===" % obj.getId())
        setSite(obj)
        setup_tool = obj.portal_setup

        for profile_id, version in TARGETS.items():
            current = setup_tool.getLastVersionForProfile(profile_id)
            if current == version:
                print("  %-40s already %s" % (profile_id, current))
                continue
            setup_tool.setLastVersionForProfile(profile_id, version)
            print("  %-40s %s -> %s" % (profile_id, current, version))
            total += 1

        print("  --- all records now ---")
        for pid in sorted(setup_tool._profile_upgrade_versions):
            print("    %-40s %s" % (pid, setup_tool._profile_upgrade_versions[pid]))

    if total:
        transaction.commit()
        print("\nCommitted: set %d profile version(s)." % total)
    else:
        transaction.abort()
        print("\nNothing to change.")


main(app)  # noqa: F821  (app injected by `bin/instance run`)
