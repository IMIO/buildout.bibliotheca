VENV_FOLDER=.venv

ifeq (, $(shell which uv ))
  $(error "[ERROR] The 'uv' command is missing from your PATH. Install it from: https://docs.astral.sh/uv/getting-started/installation/")
endif

.PHONY: help
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: $(VENV_FOLDER)/bin/buildout .git/hooks/pre-commit ## Install development environment
	$(VENV_FOLDER)/bin/buildout

.PHONY: start
start: bin/instance .git/hooks/pre-commit ## Start the instance
	bin/instance fg

.PHONY: cleanall
cleanall: ## Clean development environment
	rm -fr .git/hooks/pre-commit .installed.cfg .mr.developer.cfg .venv bin buildout.cfg develop-eggs downloads eggs include lib lib64 local parts pyvenv.cfg

.PHONY: upgrade-steps
upgrade-steps: ## Run upgrade steps
	bin/instance -O Plone run scripts/run_portal_upgrades.py

.PHONY: lint
lint: ## Run pre-commit hooks
	uvx pre-commit run --all

.PHONY: garage-init
garage-init: ## Initialise local Garage S3 storage (layout, key, bucket) for docker-compose
	docker compose up -d garage
	@sleep 2
	NODE=$$(docker compose exec -T garage /garage node id -q | cut -d@ -f1) && \
	docker compose exec -T garage /garage layout assign -z dc1 -c 1G $$NODE && \
	docker compose exec -T garage /garage layout apply --version 1
	set -a && . ./.env && set +a && \
	docker compose exec -T garage /garage key import --yes -n plone $$S3_ACCESS_KEY $$S3_SECRET_KEY && \
	docker compose exec -T garage /garage bucket create $${S3_BUCKET_NAME:-zodb-blobs} && \
	docker compose exec -T garage /garage bucket allow --read --write --owner $${S3_BUCKET_NAME:-zodb-blobs} --key plone

.venv:
	@echo "Creating virtual environment with uv"
	uv venv

buildout.cfg:
	ln -fs dev.cfg buildout.cfg

$(VENV_FOLDER)/bin/buildout: .venv buildout.cfg
	@echo "Installing requirements with uv pip interface"
	uv pip install -r requirements.txt

bin/instance: $(VENV_FOLDER)/bin/buildout
	@echo "Bootstrapping environment with buildout"
	$(VENV_FOLDER)/bin/buildout

.git/hooks/pre-commit: .venv
	@echo "Installing pre-commit hooks"
	uvx pre-commit install