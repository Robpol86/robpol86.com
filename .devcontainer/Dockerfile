# https://github.com/microsoft/vscode-dev-containers/tree/v0.233.0/containers/python-3/.devcontainer/base.Dockerfile

ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends \
    pv \
    vim

# RUN curl -sSL https://install.python-poetry.org |python3 -
