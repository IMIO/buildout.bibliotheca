"""Bibliotheca checks, run by `make test` after the generic image checks.

The fixtures (`site_url`, `admin`) come from the pytest plugin of
IMIO/gha plone-image-test-notify.
"""

import pytest

TIMEOUT = 60
HTML = {"Accept": "text/html"}


def create(admin, container_url, portal_type, title, **fields):
    response = admin.post(
        container_url,
        json={"@type": portal_type, "title": title, **fields},
        timeout=TIMEOUT,
    )
    assert response.status_code == 201, response.text
    return response.json()["@id"]


@pytest.mark.parametrize("portal_type", ["patrimoine", "Document", "Folder"])
def test_create_and_render(admin, site_url, portal_type):
    url = create(admin, site_url, portal_type, f"Test {portal_type}")
    response = admin.get(url, headers=HTML, timeout=TIMEOUT)
    assert response.status_code == 200
