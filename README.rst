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

Copy ``.env.example`` to ``.env`` (or add the ``PGJSONB_*`` and ``S3_*``
variables to your existing ``.env``) and initialise the local Garage S3
storage once::

    make garage-init

Finally start docker-compose::

    docker-compose up

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
