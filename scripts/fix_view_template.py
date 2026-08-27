import json
import re
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from Testing.makerequest import makerequest
from plone.app.blocks.layoutbehavior import ILayoutAware

app = makerequest(app)  # noqa: F821 (``app`` is injected by bin/instance run)
newSecurityManager(None, system_user)

site = app.Plone
catalog = site.portal_catalog

TILEDATA_RE = re.compile(r"data-tiledata=(['\"])(.*?)\1", re.DOTALL)

fixed = []
unparsed = []


def fix_content(content):
    changed = False

    def repl(match):
        nonlocal changed
        quote, raw = match.group(1), match.group(2)
        try:
            data = json.loads(raw)
        except ValueError:
            unparsed.append(raw[:200])
            return match.group(0)
        if isinstance(data, dict) and data.get("view_template") == "":
            data["view_template"] = "default_layout"
            changed = True
            new_raw = json.dumps(data)
            return f"data-tiledata={quote}{new_raw}{quote}"
        return match.group(0)

    new_content = TILEDATA_RE.sub(repl, content)
    return new_content, changed


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
    new_content, changed = fix_content(content)
    if changed:
        layout.content = new_content
        fixed.append("/".join(obj.getPhysicalPath()))

if fixed:
    transaction.commit()
    print(f"Fixed {len(fixed)} object(s):")
    for path in fixed:
        print(" -", path)
else:
    print("No objects found with an empty view_template tile — no changes made.")

if unparsed:
    print(f"\nWARNING: {len(unparsed)} data-tiledata blob(s) failed to parse as JSON:")
    for raw in unparsed:
        print(" -", raw)
