Buildout Bibliotheca
====================
This buildout is used to build dev and production environment for imio iA.Bibliotheca app.

dev
---
Run these commands::

    make buildout
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

Second get eggs to build quickly and build image::

    make eggs
    docker-compose build

Finally start docker-compose::

    docker-compose up

and you can go to http://portal.localhost now

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
adds outbound HTTP child spans. SQL spans are not available here: the
instrumentor targets psycopg 3, while RelStorage uses psycopg2.

docker-compose runs a Jaeger collector with these variables set: browse
http://localhost:16686 to see the traces. To trace the dev instance too::

    docker compose up -d jaeger
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 OTEL_SERVICE_NAME=bibliotheca-dev bin/instance fg
