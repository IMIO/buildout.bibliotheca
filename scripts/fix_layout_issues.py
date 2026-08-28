"""
Scan (and fix what's safe to fix) broken plone.app.blocks tile data.

Run with:
    bin/instance run scripts/fix_layout_issues.py

Handles two known issues introduced by the plone.app.standardtiles 3.2.3 ->
4.0.0 upgrade (Plone 6.1.5 -> 6.2.1), which made tile data deserialization
strict about schema validation:

1. ``view_template: ""`` on an ``existingcontent`` tile. The empty string
   used to be silently tolerated as "use default view"; the vocabulary now
   only accepts "default_layout" for that. Safe to fix automatically:
   rewrites the value in place.

2. ``content_uid`` on an ``existingcontent`` tile pointing to content that
   no longer exists (deleted). Not auto-fixed: reported only, since the
   correct fix (remove the tile vs. repoint it to replacement content)
   requires a human decision.
"""
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

TILEDATA_RE = re.compile(r"data-tile=(['\"])([^'\"]*)\1\s+data-tiledata=(['\"])(.*?)\3", re.DOTALL)

fixed_view_template = []
dangling_content_uid = []
unparsed = []

for brain in catalog.unrestrictedSearchResults(path="/"):
    try:
        obj = brain.getObject()
    except Exception:
        continue
    layout = ILayoutAware(obj, None)
    if layout is None:
        continue
    content = layout.content or ""
    if "existingcontent" not in content:
        continue

    path = "/".join(obj.getPhysicalPath())
    changed = False

    def repl(match):
        global changed
        quote, tile_url, data_quote, raw = (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
        )
        if "existingcontent" not in tile_url:
            return match.group(0)
        try:
            data = json.loads(raw)
        except ValueError:
            unparsed.append((path, tile_url, raw[:200]))
            return match.group(0)
        if not isinstance(data, dict):
            return match.group(0)

        local_changed = False
        if data.get("view_template") == "":
            data["view_template"] = "default_layout"
            local_changed = True

        uid = data.get("content_uid")
        if uid and not catalog.unrestrictedSearchResults(UID=uid):
            dangling_content_uid.append((path, tile_url, uid))

        if local_changed:
            changed = True
            new_raw = json.dumps(data)
            return f"data-tile={quote}{tile_url}{quote} data-tiledata={data_quote}{new_raw}{data_quote}"
        return match.group(0)

    new_content = TILEDATA_RE.sub(repl, content)
    if changed:
        layout.content = new_content
        fixed_view_template.append(path)

if fixed_view_template:
    transaction.commit()

print(f"Scanned {len(catalog)} catalog entries.\n")

if fixed_view_template:
    print(f"Fixed {len(fixed_view_template)} object(s) with an empty view_template:")
    for path in fixed_view_template:
        print(" -", path)
else:
    print("No empty view_template tiles found.")

print()
if dangling_content_uid:
    print(f"Found {len(dangling_content_uid)} existingcontent tile(s) referencing a missing content_uid (NOT auto-fixed):")
    for path, tile_url, uid in dangling_content_uid:
        print(f" - {path} :: {tile_url} -> missing UID {uid}")
else:
    print("No dangling content_uid references found.")

if unparsed:
    print(f"\nWARNING: {len(unparsed)} data-tiledata blob(s) failed to parse as JSON:")
    for path, tile_url, raw in unparsed:
        print(f" - {path} :: {tile_url} :: {raw}")
