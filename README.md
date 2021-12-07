# Robpol86.com

This is my personal website. It's built with [Sphinx](http://sphinx-doc.org/), hosted on
[NearlyFreeSpeech.NET](https://www.nearlyfreespeech.net/), using the
[Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/) theme.

SSL is provided for free by [CloudFlare](https://www.cloudflare.com/).

I use GitHub Actions to automatically build and push HTML files to NFSN.

## Releases

Deployments to production are done by GitHub Actions when a new [release](https://github.com/Robpol86/robpol86.com/releases)
is manually created. All branch and tag pushes trigger a deployment to staging, whilst pull requests only trigger CI linting.

## Local Development

I locally develop this project on an Ubuntu VM via Windows WSL2. To get started:

```bash
# Install Python and Poetry.
sudo apt-get update && sudo apt-get install python3
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

# Setup local environment.
make distclean
make init
make deps

# Build.
make lint
make docs
```
