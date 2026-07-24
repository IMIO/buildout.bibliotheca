# -*- coding: utf-8 -*-
"""Offline repair for the library.* -> bibliotheca.* rename.

Run with:  bin/instance run scripts/fix_rename.py

The existing ZODB was populated while the add-ons were named library.*.
After the rename to bibliotheca.* those dotted names are no longer importable,
which breaks:
  * the persisted patrimoine FTI schema string  -> RecursionError on lookupSchema
  * the plone.browserlayer local utility (ILibraryCoreLayer) -> startup warning

This script rewrites the stale references in place and commits.
"""
import transaction
from Acquisition import aq_base
from zope.component.hooks import setSite

OLD_PREFIX = "library."
NEW_PREFIX = "bibliotheca."


def iter_plone_sites(app):
    for obj in app.objectValues():
        # A Plone site has a portal_types tool; good enough and avoids imports.
        if getattr(aq_base(obj), "portal_types", None) is not None:
            yield obj


def fix_ftis(site):
    changed = []
    ptypes = site.portal_types
    for type_id in ptypes.objectIds():
        fti = ptypes[type_id]
        for attr in ("schema", "model_source"):
            value = getattr(fti, attr, None)
            if value and OLD_PREFIX in value:
                new_value = value.replace(OLD_PREFIX, NEW_PREFIX)
                setattr(fti, attr, new_value)
                changed.append((type_id, attr, value, new_value))
    return changed


def invalidate_schema_cache(changed):
    try:
        from plone.dexterity.schema import SCHEMA_CACHE
    except Exception as exc:  # pragma: no cover
        print("  ! could not import SCHEMA_CACHE: %s" % exc)
        return
    for type_id, attr, _old, _new in changed:
        if attr in ("schema", "model_source"):
            try:
                SCHEMA_CACHE.invalidate(type_id)
            except Exception as exc:
                print("  ! invalidate(%s) failed: %s" % (type_id, exc))
    # Also clear the whole cache to be safe.
    try:
        SCHEMA_CACHE.clear()
    except Exception:
        pass


def purge_stale_browserlayers(site):
    """Remove plone.browserlayer utilities whose interface can't be imported
    (Broken objects) and that come from the old library.* modules."""
    purged = []
    try:
        from plone.browserlayer.interfaces import ILocalBrowserLayerType
    except Exception as exc:  # pragma: no cover
        print("  ! could not import ILocalBrowserLayerType: %s" % exc)
        return purged
    sm = site.getSiteManager()
    # Snapshot registrations first (we mutate during iteration).
    regs = list(sm.registeredUtilities())
    for reg in regs:
        if reg.provided is not ILocalBrowserLayerType:
            continue
        iface = reg.component
        module = getattr(iface, "__module__", "") or ""
        name = getattr(iface, "__name__", "") or reg.name or ""
        if module.startswith(OLD_PREFIX) or name.startswith("ILibrary"):
            sm.unregisterUtility(
                component=iface,
                provided=ILocalBrowserLayerType,
                name=reg.name,
            )
            purged.append((reg.name, module, name))
    return purged


def register_new_browserlayers(site):
    """Run the browserlayer import step for the renamed profiles so
    IBibliothecaCoreLayer / IBibliothecaPolicyLayer get registered."""
    registered = []
    setup_tool = site.portal_setup
    for profile in (
        "profile-bibliotheca.core:default",
        "profile-bibliotheca.policy:default",
    ):
        try:
            setup_tool.runImportStepFromProfile(profile, "browserlayer")
            registered.append(profile)
        except Exception as exc:
            print("  ! browserlayer import failed for %s: %s" % (profile, exc))
    return registered


def main(app):
    total_changes = 0
    sites = list(iter_plone_sites(app))
    if not sites:
        print("No Plone site found under the application root.")
        return
    for site in sites:
        print("=== Site: /%s ===" % site.getId())
        setSite(site)

        changed = fix_ftis(site)
        for type_id, attr, old, new in changed:
            print("  FTI %-20s %s: %s -> %s" % (type_id, attr, old, new))
        if changed:
            invalidate_schema_cache(changed)

        purged = purge_stale_browserlayers(site)
        for name, module, iface_name in purged:
            print("  browserlayer purged: name=%r %s.%s" % (name, module, iface_name))

        registered = register_new_browserlayers(site)
        for profile in registered:
            print("  browserlayer imported from %s" % profile)

        total_changes += len(changed) + len(purged) + len(registered)

    if total_changes:
        transaction.commit()
        print("\nCommitted %d change(s)." % total_changes)
    else:
        transaction.abort()
        print("\nNothing to change.")


main(app)  # noqa: F821  (app is injected by `bin/instance run`)
