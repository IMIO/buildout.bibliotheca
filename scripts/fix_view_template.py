import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from Testing.makerequest import makerequest
from plone.app.blocks.layoutbehavior import ILayoutAware

app = makerequest(app)  # noqa: F821 (``app`` is injected by bin/instance run)
newSecurityManager(None, system_user)

site = app.Plone
catalog = site.portal_catalog

old = '"view_template": ""'
new = '"view_template": "default_layout"'

fixed = []

for brain in catalog.unrestrictedSearchResults():
    try:
        obj = brain.getObject()
    except Exception:
        continue
    layout = ILayoutAware(obj, None)
    if layout is None:
        continue
    content = layout.content or ""
    if old in content:
        layout.content = content.replace(old, new)
        fixed.append("/".join(obj.getPhysicalPath()))

if fixed:
    transaction.commit()
    print(f"Fixed {len(fixed)} object(s):")
    for path in fixed:
        print(" -", path)
else:
    print("No objects found with an empty view_template tile — no changes made.")
