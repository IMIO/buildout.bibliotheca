import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from Testing.makerequest import makerequest
from plone.app.blocks.layoutbehavior import ILayoutAware

app = makerequest(app)  # noqa: F821 (``app`` is injected by bin/instance run)
newSecurityManager(None, system_user)

site = app.Plone
front_page = site["front-page"]
layout = ILayoutAware(front_page)
content = layout.content

old = '"view_template": ""'
new = '"view_template": "default_layout"'

if old in content:
    layout.content = content.replace(old, new)
    transaction.commit()
    print("Fixed: replaced empty view_template with 'default_layout' on /Plone/front-page")
else:
    print("Pattern not found — no changes made. Dumping current content for inspection:")
    print(content)
