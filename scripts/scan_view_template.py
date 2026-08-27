from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from Testing.makerequest import makerequest
from plone.app.blocks.layoutbehavior import ILayoutAware

app = makerequest(app)  # noqa: F821 (``app`` is injected by bin/instance run)
newSecurityManager(None, system_user)

site = app.Plone
catalog = site.portal_catalog

needle = '"view_template": ""'
hits = []

for brain in catalog.unrestrictedSearchResults():
    try:
        obj = brain.getObject()
    except Exception:
        continue
    layout = ILayoutAware(obj, None)
    if layout is None:
        continue
    content = layout.content or ""
    if needle in content:
        hits.append("/".join(obj.getPhysicalPath()))

print(f"Scanned {len(catalog)} catalog entries.")
if hits:
    print(f"Found {len(hits)} object(s) with an empty view_template tile:")
    for path in hits:
        print(" -", path)
else:
    print("No other objects found with an empty view_template tile.")
