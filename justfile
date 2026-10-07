venv_folder := ".venv"
uv := require("uv")

# Display this help message
help:
    @just --list --unsorted

# Install development environment
install: _buildout _pre-commit
    {{ venv_folder }}/bin/buildout

# Start the instance
start: _instance _pre-commit
    bin/instance fg

# Clean development environment
cleanall:
    rm -fr .git/hooks/pre-commit .installed.cfg .mr.developer.cfg .venv bin buildout.cfg develop-eggs downloads eggs include lib lib64 local parts pyvenv.cfg

# Run upgrade steps
upgrade-steps:
    bin/instance -O Plone run scripts/run_portal_upgrades.py

# Run pre-commit hooks
lint:
    uvx pre-commit run --all

# Initialise local Garage S3 storage (layout, key, bucket) for docker-compose
garage-init:
    #!/usr/bin/env bash
    set -euo pipefail
    set -a && . ./.env && set +a
    BUCKET=${S3_BUCKET_NAME:-zodb-blobs}
    garage() { docker compose exec -T garage /garage "$@"; }
    docker compose up -d garage
    sleep 2
    # Each step is skipped when already done, so the recipe can be re-run safely
    if garage layout show | grep -q "Current cluster layout version: 0"; then
        NODE=$(garage node id -q | cut -d@ -f1)
        garage layout assign -z dc1 -c 1G $NODE
        garage layout apply --version 1
    fi
    garage key info plone >/dev/null 2>&1 || garage key import --yes -n plone $S3_ACCESS_KEY $S3_SECRET_KEY
    garage bucket info $BUCKET >/dev/null 2>&1 || garage bucket create $BUCKET
    garage bucket allow --read --write --owner $BUCKET --key plone

# The private recipes below replace make's file targets: they only run when the file is missing

[private]
_venv:
    @[ -e {{ venv_folder }} ] || { echo "Creating virtual environment with uv"; {{ uv }} venv; }

[private]
_buildout-cfg:
    @[ -e buildout.cfg ] || ln -fs dev.cfg buildout.cfg

[private]
_buildout: _venv _buildout-cfg
    @[ -e {{ venv_folder }}/bin/buildout ] || { echo "Installing requirements with uv pip interface"; {{ uv }} pip install -r requirements.txt; }

[private]
_instance: _buildout
    @[ -e bin/instance ] || { echo "Bootstrapping environment with buildout"; {{ venv_folder }}/bin/buildout; }

[private]
_pre-commit: _venv
    @[ -e .git/hooks/pre-commit ] || { echo "Installing pre-commit hooks"; uvx pre-commit install; }
