# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

- N/A

## 2022-04-01

Installing Windows 11 on a Mac: WSL2 ssh-agent steps

- Moved WSL2 ssh-agent steps from gist to here since steps were split between the two before.
- Removed software steps out of here since they're out of scope.

## 2022-03-30

Installing Windows 11 on a Mac: Removing more bloatware

- Latest version of sphinx-book-theme with performance enhancements.
- Implemented support for tagging documents using a slightly customized Sphinx `index` directive.
- Using sphinx_external_toc to support future blog posts.
- Updated Windows 11 on Macs page to remove more bloat along with some tweaks.

## 2022-01-28

Franklin T9: Auto Reboot

- Added Auto Reboot section to Franklin T9 page.
- De-duplicating steps in multiple GitHub Actions workflows by defining my own composite action in this same repo.
- Optimizing GitHub Actions by only installing dev dependencies in ci.yml and not deploy/diff.
- Linting CHANGELOG.md file in CI via pytest.

## 2022-01-04

New page: MIB2 Hacking

- Added MIB2 Composition Media Hacking with some initial findings.

## 2022-01-02

Alltrack page: MIB2 Developer Mode

- Added MIB2 Developer Mode section to Alltrack page.

## 2021-12-31

Alltrack page: Forums links

- Enabling MyST `fieldlist` extension for future use.
- Added forums post links to latest Alltrack page entries.
- Resolved Pygments dependency TODO now that v2.11 has been released.

## 2021-12-24

Euro Tail Lights, license links, diff HTML files

- Diffing HTML files between workflow build and current production.
- Added Euro Tail Lights section to Alltrack page.
- Added Tweaks and Software section to Windows 11 on a Mac page.
- Moved all images to Imgur now that sphinx-imgur works fine with OpenGraph.
- Added link to LICENSE file in the left sidebar.

## 2021-12-13

Windows 11 on a Mac: BIOS and EFI bootable

- Restyled commands in Windows 11 on Mac page.
- Made Windows 11 Boot Camp ISO bootable on traditional BIOS and UEFI PCs.

## 2021-12-11

New page: Installing Windows 11 on a Mac

- Speed up CI/CD by caching .venv in GitHub Actions.
- Automatically purge Cloudflare cache on deploy.
- Open browser to localhost instead of 127.0.0.1 on autobuild to fix broken Imgur images.
- Updated dependencies: New MyST version.
- PNG version of site logo only for OpenGraph since there's no SVG support.
- Remove left/right margin for figure captions to reduce wrapping.
- Partially revert background hacking. Avoiding "inherit" for background since it breaks assumptions made by theme.
- Imgur links defaults to full size image (though Imgur redirects visitors to the old page unless they click through first).
- Added new page: Installing Windows 11 on a Mac. Including BitLocker instructions.

## 2021-12-07

Style consistency

- Made resume link style consistent with the other links within the admonition in index.md.
- Split custom.css into two scoped files.
- Reordered Tutorials TOC list.

## 2021-12-05

Background image and autobiography

- TOCTree: Reorganized and grouped into new names.
- Converted index.rst into index.md.
- GitHub button at the top no longer is a mouseover menu. Links directly to `/blob/` like the RTD theme.
- Stop creating `_sources` directory, source files already on public GitHub.
- Adding a background image to every page.
- Adding a short autobiography.

## 2021-12-03

Latest Imgur extension with OpenGraph support

- Using rsync `--delete-after` to avoid race condition where files are removed before index.html is updated.
- Switch from old and crap-patched to new and proper [sphinx-imgur](https://sphinx-imgur.readthedocs.io/) extension. Fixes
  compatibility with opengraph extension.
- Fixed image alignments in some documents where two or three images are supposed to sit side by side flush with each other.
- Updating photo albums with new (old) rack cabinet albums.
- Changed OpenGraph type from "article" to "website". They look the same in Discord and article has a bunch of extra tags
  that I won't be using: https://ogp.me/#no_vertical

## 2021-11-25

Franklin T9 page updates, dependency updates

- Added Flash Dumps, lsusb, and fastboot output sections.
- Large opengraph images when posting to Discord.
- Using unreleased pygments with dts syntax highlighting fix.
- Using newer unreleased sphinxcontrib-youtube extension.
- Updated opengraph extension with absolute path fix.

## 2021-11-12

Franklin T9 page updates and changes

- Added pictures of circuit board without RF shields.
- Using subsections under Interesting Information section.
- Moving large command outputs into external files instead of embedding in franklin_t9.md.
- Changed order of Interesting Info section.
- Added device tree, full kernel config, datasheets, notes section, uname, lsmod, dmesg, and build.prop.
- Added steps on how to use SSH key authentication.

## 2021-11-09

New sections for Franklin T9 Hacking

- Added new sections: Fastboot, ADB, Automatic Power On, and Interesting Information.

## 2021-11-05

New page: T-Mobile Franklin T9 Hacking

- Remove "documentation" from every `<title />`.
- Generate a sitemap.xml file and reference it in a now-dynamic robots.txt file.
- Setting baseline natural language to "en" for assistive technology.
- Remove tests since they're all disabled and one (docker) has a [security issue](https://github.com/docker/docker-py/issues/2902).
- Update 404 page with a Lemmings iframe.

## 2021-10-25

Updating Monoprice Maker Select v2 and Golf Alltrack SE, better date formatting

- Using "Oct `21" datestamps instead of "21-10" to make it more human-readable.
- Adding EcoHitch Install and Upgrading Parts posts.

## 2021-10-21

Adding Monoprice Maker Select v2, updating Golf Alltrack SE

- Adding new 3D printer project page.
- Removing AirTag section (occasionally caused issues with radar system).
- Updated fire extinguisher section.
- Renaming "Experiments" section to "Projects".
- Enabling edit page button that points to `/blob/` URLs.

### Behind the Scenes

- Updated from Python 3.9 to 3.10 in CI.
- Added CHANGELOG file.
- Updated Python dependencies.

## 2021-09-10

Moving Google Analytics to Cloudflare

## 2021-09-09

Updating Golf Alltrack SE

- Added Rear Dashcam Pair section
- Using definition list instead of glossary for duplicates

## 2021-09-06

Updating Golf Alltrack SE

- Adding OBDeleven mods with some pictures.
- Split Dashcam section into two parts.

## 2021-08-28

Updating Golf Alltrack SE

- Embedding drag race youtube video.

## 2021-08-27

Added Golf Alltrack SE

- Updated Python dependencies.
- Adding new page: Golf Alltrack SE

## 2021-06-15

Refreshed Website

- Recent version of Sphinx and other Python libraries.
- Using new Sphinx theme.
- New vector-based favicon.
- Deploy from GitHub Actions.
- Dropped SCVersioning.
- Using Python Poetry instead of setuptools and tox.
