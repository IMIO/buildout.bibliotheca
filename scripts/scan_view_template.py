import json
import re
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from Testing.makerequest import makerequest
from plone.app.blocks.layoutbehavior import ILayoutAware

app = makerequest(app)  # noqa: F821 (``app`` is injected by bin/instance run)
newSecurityManager(None, system_user)

site = app.Plone
catalog = site.portal_catalog

TILEDATA_RE = re.compile(r"data-tiledata=(['\"])(.*?)\1", re.DOTALL)

hits = []
unparsed = []

for brain in catalog.unrestrictedSearchResults():
    try:
        obj = brain.getObject()
    except Exception:
        continue
    layout = ILayoutAware(obj, None)
    if layout is None:
        continue
    content = layout.content or ""
    if "view_template" not in content:
        continue
    for match in TILEDATA_RE.finditer(content):
        raw = match.group(2)
        try:
            data = json.loads(raw)
        except ValueError:
            unparsed.append((("/".join(obj.getPhysicalPath())), raw[:200]))
            continue
        if isinstance(data, dict) and data.get("view_template") == "":
            hits.append("/".join(obj.getPhysicalPath()))
            break

print(f"Scanned {len(catalog)} catalog entries.")
if hits:
    print(f"Found {len(hits)} object(s) with an empty view_template tile:")
    for path in hits:
        print(" -", path)
else:
    print("No other objects found with an empty view_template tile.")

if unparsed:
    print(f"\nWARNING: {len(unparsed)} data-tiledata blob(s) failed to parse as JSON:")
    for path, raw in unparsed:
        print(" -", path, ":", raw)
