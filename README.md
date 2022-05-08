# Robpol86.com

[![Github-CI][github-ci]][github-link]
[![Code style: black][black-badge]][black-link]

[github-ci]: https://github.com/Robpol86/sphinx-carousel/actions/workflows/ci.yml/badge.svg?branch=main
[github-link]: https://github.com/Robpol86/sphinx-carousel/actions/workflows/ci.yml
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black

My personal website.

Built with [Sphinx](http://sphinx-doc.org/), hosted on [NearlyFreeSpeech.NET](https://www.nearlyfreespeech.net/), using the
[Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/) theme. SSL is provided for free by
[CloudFlare](https://www.cloudflare.com/).

I use GitHub Actions to automatically build and push HTML files to NFSN.

## Releases

Deployments to production are done by GitHub Actions when a new tag matching the format YYYY-MM-DD is manually pushed. All
branch and tag pushes trigger a deployment to staging, whilst pull requests only trigger CI linting and testing.
