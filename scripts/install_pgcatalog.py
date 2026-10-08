# -*- coding: utf-8 -*-
"""Install plone.pgcatalog on an existing site.

One-way: replaces portal_catalog with PlonePGCatalogTool and rebuilds it
(no uninstall profile). Back up the PostgreSQL database first, then run in
the instance container:

    bin/instance run scripts/install_pgcatalog.py

New sites get plone.pgcatalog from PLONE_EXTENSION_IDS at creation.
"""
from plone import api
from plone.pgcatalog.catalog import PlonePGCatalogTool
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest

import logging
import os
import sys
import transaction


logger = logging.getLogger('install_pgcatalog.py')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s',
                              '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)


def install(app):
    app = makerequest(app)
    setRequest(app.REQUEST)
    portal = app[os.getenv("SITE_ID", "Plone")]
    setSite(portal)
    if isinstance(portal.portal_catalog, PlonePGCatalogTool):
        logger.info("plone.pgcatalog already installed, nothing to do")
        return
    logger.info("Installing plone.pgcatalog (catalog rebuild may take a while)")
    with api.env.adopt_roles(["Manager"]):
        if not api.addon.install("plone.pgcatalog"):
            logger.error("plone.pgcatalog installation failed, aborting")
            transaction.abort()
            return
    transaction.commit()
    logger.info("plone.pgcatalog installed, portal_catalog is now %s",
                portal.portal_catalog.meta_type)


if __name__ == '__main__':
    install(app)  # noqa
