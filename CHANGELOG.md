# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

- N/A

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
