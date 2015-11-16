SHELL = /bin/bash


.PHONY: default
default:
	@echo "Available targets:"
	@echo "    make bootstrap  # Install requirements."
	@echo "    make build      # Generates html files in docs/_build/html."
	@echo "    make serve      # Runs a simple web server."


.PHONY: bootstrap
bootstrap:
	pip install -r requirements.txt


.PHONY: build
build:
	cd docs && sphinx-build . _build/html


.PHONY: serve
serve: build
	sphinx-autobuild docs docs/_build/html
