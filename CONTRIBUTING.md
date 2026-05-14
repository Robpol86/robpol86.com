# Contributing

Anyone that wants to contribute to this project should read this document.

## Bug Reports

If you're reporting a bug it's most helpful if you include steps to reproduce the issue. Include the following:

* Python version

## Pull Requests

If you plan on submitting a pull request and you want to develop your contribution locally you can setup your local
environment using the steps below.

### Setup Development Environment

This project uses [uv](https://github.com/astral-sh/uv). After cloning this repo install `uv` and then run the following
before working on your code change:

```bash
make deps  # Installs Python dependencies in the ./.venv VirtualEnv.
make test  # Runs unit tests.
make lint  # Runs linters.
```

## Create Stage

Notes for project maintainers.

1. https://members.nearlyfreespeech.net/robpol86/sites
1. Create a New Site > **Site Short Name**: rob86stage
1. **Canonical Name**: rob86stage.robpol86.com
1. **Setup DNS?**: No
1. **Server Type**: Apache 2.4 Static Content
1. **Site Plan**: Non-Production
1. Create This Site
1. Site Information > **HTTPS Redirection**: Off
1. Wait 10 minutes for Cloudflare to catch up

No further action needed. SSH keys are already pre-configured.

## Releases

These are the steps a maintainer will take to make a new release.

Releasing to stage is done automatically on every branch push.

To release to production:

1. https://github.com/Robpol86/robpol86.com/actions/workflows/release.yml
1. Run workflow > Fill out the release title
    1. This will also be the section title in the [CHANGELOG.md](CHANGELOG.md) entry
1. Run workflow
1. When it completes a new git tag, GitHub release, and CHANGELOG.md entry will be created
    1. The version will be auto-bumped in [pyproject.toml](pyproject.toml) as well
1. The workflow will also deploy the HTML to production

## Thank You!

Thanks for fixing bugs or adding features to the project!
