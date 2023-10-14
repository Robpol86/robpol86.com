# Robpol86.com

[![Github-CI][github-ci]][github-link]

[github-ci]: https://github.com/Robpol86/robpol86.com/actions/workflows/build.yml/badge.svg?branch=main
[github-link]: https://github.com/Robpol86/robpol86.com/actions/workflows/build.yml

My personal website.

Built with [Sphinx](http://sphinx-doc.org/), hosted on [NearlyFreeSpeech.NET](https://www.nearlyfreespeech.net/), using the
[Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/) theme. SSL is provided for free by
[CloudFlare](https://www.cloudflare.com/).

I use GitHub Actions to automatically build and push HTML files to NFSN.

## Metrics

Google Analytics is enabled on my website via a [CloudFlare app](https://www.cloudflare.com/apps/googleanalytics).

* [Google Analytics](https://analytics.google.com/analytics/web/#/p275999550/reports/intelligenthome)
* [Google Search Console](https://search.google.com/search-console?resource_id=https%3A%2F%2Frobpol86.com%2F)

## Releases

Releasing to stage is done automatically on every branch push.

To release to production:

1. https://github.com/Robpol86/robpol86.com/actions/workflows/release.yml
1. Run workflow > Fill out the release title
    1. This will also be the section title in the [CHANGELOG.md](CHANGELOG.md) entry
1. Run workflow
1. When it completes a new git tag, GitHub release, and CHANGELOG.md entry will be created
1. The workflow will also deploy the HTML to production
