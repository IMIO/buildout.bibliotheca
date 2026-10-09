Buildout Bibliotheca
====================
This buildout is used to build dev and production environment for imio iA.Bibliotheca app.

dev
---
Run these commands::

    just install
    ./bin/instance fg

prod
----

Production is build via Jenkins. A docker image is build in each commit and pushed on staging.
To run locally a production service, you can use docker-compose

First

Add imio user to your environment::

    sudo addgroup --gid 209 imio
    sudo usermod -a -G imio $USERNAME
    sudo chmod 664 -R var/filestorage/*
    sudo chown $USERNAME:imio -R var/filestorage

Copy ``.env.example`` to ``.env`` (or add the ``PGJSONB_*`` and ``S3_*``
variables to your existing ``.env``).

Finally build the image and start docker-compose::

    docker compose up --build

``--build`` rebuilds the local ``imiobibliotheca`` image, otherwise compose
keeps running an image built from an older checkout. The local Garage S3
storage creates its layout, access key and bucket from the ``S3_*``
variables on first start, and the instance waits for PostgreSQL and Garage
to be healthy.

and you can go to http://portal.localhost now

storage
-------

Production uses `zodb-pgjsonb <https://bluedynamics.github.io/zodb-pgjsonb/>`_:
ZODB objects are stored as JSONB in PostgreSQL, blobs smaller than 64KB in
PostgreSQL and larger ones in S3 (Garage locally). Configuration comes from
``PGJSONB_*`` and ``S3_*`` environment variables (see ``.env.example``).

To migrate an existing RelStorage database, set the ``RELSTORAGE_*`` variables
(source) and the ``PGJSONB_*`` / ``S3_*`` ones (destination, another database)
and run in the instance container::

    bin/zodb-convert -w 4 --background-blobs migrate.cfg

Pack the database with::

    bin/zodbpack pack.cfg

catalog
-------

Production uses `plone.pgcatalog <https://bluedynamics.github.io/plone-pgcatalog/>`_:
``portal_catalog`` is stored in PostgreSQL, in the same ``object_state`` table
as the zodb-pgjsonb objects (the dev buildout keeps the standard ZCatalog).
New sites get it from the ``plone.pgcatalog:default`` profile listed in
``PLONE_EXTENSION_IDS``.

Existing sites (including freshly migrated RelStorage databases) must be
converted once. This is one-way (there is no uninstall profile), so back up
the PostgreSQL database first, then run in the instance container::

    bin/instance run scripts/install_pgcatalog.py

tracing
-------

`plone.observability <https://plone.github.io/plone.observability/>`_ sends
OpenTelemetry traces (one root span per request, with publishing, catalog,
rendering and commit children) to an OTLP collector. Tracing is off until
``OTEL_EXPORTER_OTLP_ENDPOINT`` is set. The exporter speaks **gRPC**, so point
it at the collector's 4317 port (not the 4318 HTTP port)::

    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

The image already sets ``OTEL_SERVICE_NAME=bibliotheca`` and excludes the
``/ok`` healthcheck with ``OTEL_PYTHON_WSGI_EXCLUDED_URLS`` (comma-separated
regexes searched in the path). ``PLONE_OBSERVABILITY_OTEL_INSTRUMENTORS=1``
adds SQL (psycopg), S3 and outbound HTTP child spans; expect a lot more spans.

docker-compose runs a Jaeger collector with these variables set: browse
http://localhost:16686 to see the traces. To trace the dev instance too::

    docker compose up -d jaeger
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 OTEL_SERVICE_NAME=bibliotheca-dev bin/instance fg
