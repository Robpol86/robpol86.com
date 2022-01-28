# Robpol86.com

This is my personal website. It's built with [Sphinx](http://sphinx-doc.org/), hosted on
[NearlyFreeSpeech.NET](https://www.nearlyfreespeech.net/), using the
[Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/) theme.

SSL is provided for free by [CloudFlare](https://www.cloudflare.com/).

I use GitHub Actions to automatically build and push HTML files to NFSN.

## Releases

Deployments to production are done by GitHub Actions when a new tag matching the format YYYY-MM-DD is manually pushed. All
branch and tag pushes trigger a deployment to staging, whilst pull requests only trigger CI linting and testing.

## Local Development

I locally develop this project on an Ubuntu VM via Windows WSL2. To get started:

```bash
# Install Python and Poetry.
sudo apt-get update && sudo apt-get install python3
curl -sSL https://install.python-poetry.org | python3 -

# Setup local environment.
make distclean
make init
make deps

# Build and test.
make docs
make test
make lint
```
