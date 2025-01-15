# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2025.1.15.43719]

Add desk photo in Mexico City

* bbfb5b1 Update deps (#275)
* 3258e50 Add desk photo in Mexico City (#274)

## [2025.1.1.185651]

Fix cities in updated NAS post

* 228751c Updating cities in NAS post (#273)
* f274a08 Disable Atom feeds (#272)

## [2024.12.31.212938]

Adding more GMKtec NAS photos

* 748e583 Adding more GMKtec NAS photos (#271)
* d0fa06d Update dependencies (#270)
* 52695da Update dependencies (#269)

## [2024.10.20.180601]

Update resume

* 5f82558 Update resume (#268)

## [2024.10.17.234534]

Enable RSS feeds

* 25b0006 Enable RSS feeds (#267)
* d1f8e9f Update dependencies (#266)
* 18417fb Add city to Travel NAS page (#265)

## [2024.10.7.32500]

New post: Travel NAS

* e0502b0 New post: Travel NAS (#264)

## [2024.10.6.221935]

New posts: desk photos

* 4b815ca New posts: desk photos (#261)
* f7d7146 Update README with latest project changes. (#259)
* c3782dd Enable Google Analytics (#258)

## [2024.10.4.210258]

Disable dark mode for Disqus

* b0b3abb Replace version bump sed with awk (#252)
* a8d6461 Revert (#251)
* dc44d65 2024.10.4.183649: Disable dark mode for Disqus
* 7fd0b43 Extended version/tag for more releases per day. (#250)
* 6c511bd Disable dark mode for Disqus (#249)

## [2024.10.4]

Migrated to ABlog

* ffe8923 Migrating to ABlog (#245)
* 83f939c Switching from :width: to list-table (#244)
* d2d1641 Remove some imgur-embed (#243)
* 1134a6d Reduce diff of rewrite. (#242)
* f2abe62 Removing sphinx-carousel (#241)
* 5277c56 Update dependencies (#240)
* 7ba4bf8 Taking git_status.txt into account (#239)
* b5ce1c7 Update deps/bp (#237)
* be527d2 Update CI dependencies (#234)
* f870d58 Unpin pygments (#232)
* f284684 Update additional dependencies (#231)
* 91bc624 Update sphinxcontrib-youtube (#230)
* 6a3fbe9 Updating some dependencies (#229)
* 6a0cced Fix linkcheck (#228)

## [2023.10.14]

Refactored GitHub Actions

* a7d9f5f Revert
* 5f0becc 2023.10.14: TODO
* e200ca5 sphinx_github_branch NEW_TAG (#227)
* 5b9f180 Ignore parts.vw.com again. (#226)
* 1521221 Document release process. (#225)
* 0d610c6 Production release workflow dispatch. (#223)
* 4c9e71e Deploy must be push: not PR (#224)
* 1bf3a25 Refactoring Deploy (Staging Only) (#221)
* 804be03 Refactor linkcheck (#222)
* f44cef3 Reducing complexity (#220)
* 65c218e Reusable Workflows: build and diff (#219)
* aaf635b Fix deploy and HTML diff false positive (#218)
* 3542d8d Revisit GitHub Action Workflows (#215)
* 2d7c64d Pinning dependencies for now. (#214)
* 1dc0ef7 Updating transitive dependencies. (#213)
* 8899f56 Update Dependencies (#212)
* 73c17a3 Fix the build. (#211)
* 5a13dc9 Update dependencies. (#209)
* 3c77bcd Update dependencies. (#208)
* c0202e4 Fix missing backslash. (#207)

## [2022.12.11]

New post: Clutch Bleeder Block Replacement

## [2022.10.30]

New post: Snapmaker Enclosure Door Reversal

## [2022.10.27]

Alltrack page: Jack Pads

## [2022.9.10]

Alltrack page: Manually linking to related posts

## [2022.8.24]

New post: OEMTools 24938 Gauge Mod

## [2022.8.21]

Updated Windows 11 on a Mac

- Touched up instructions on Windows 11 on a Mac page. Also clarifying it's for Intel Macs.

## [2022.8.4]

Updated Windows 11 on a Mac

- Increasing temporary size of Windows 11 Mac ISO for NTLite users. Also added alternative install instructions.
- Fixed newly broken link. Looks like Travla is out of business or something.

## [2022.7.15]

New post: Snapmaker 2.0 A350T Teflon Tube

## [2022.6.30]

New post: Server Cabinet June 2022

## [2022.6.5]

HomeLink Rearview Mirror

- Renamed fixes.css to aside_margin.css to keep CSS files scoped.
- Moved extra_navbar from conf.py into _templates/extra_navbar.html.
- Refactored `legacy.render_robots_txt` into `move_static.move_to_root`.
- Fixing tags: using relative links instead of relying on html_baseurl.
- Using Sphinx's linkcheck builder in Makefile and CI.
- First "blog" post: HomeLink mirror install

## [2022.5.23]

Sphinx Carousel

- Switching from old-style iframes to the sphinx extension in the Atrix Lapdock page.
- Replacing single-image Imgur embeds into figures.
- Using [Sphinx Carousel](https://sphinx-carousel.readthedocs.io/).

## [2022.5.21]

Latest Sphinx Book Theme and refactored repo

- Updated repo boilerplate to match sphinx-carousel.
- Refactored and restyled deploy and HTML diff workflows.
- Latest myst-parser.
- Dropping Python 3.7 support after updating Python in desktop WSL.
- Moving code from `conf.py` into `robpol86_com` package.
- Disabling GitHub page link when building locally, no more faking.
- Using real versions similar to semver but date-based.
- Latest book theme.
- Removing download and fullscreen buttons.
- Templatizing `html_theme_options["extra_navbar"]`.

## [2022.4.1]

Installing Windows 11 on a Mac: WSL2 ssh-agent steps

- Moved WSL2 ssh-agent steps from gist to here since steps were split between the two before.
- Removed software steps out of here since they're out of scope.

## [2022.3.30]

Installing Windows 11 on a Mac: Removing more bloatware

- Latest version of sphinx-book-theme with performance enhancements.
- Implemented support for tagging documents using a slightly customized Sphinx `index` directive.
- Using sphinx_external_toc to support future blog posts.
- Updated Windows 11 on Macs page to remove more bloat along with some tweaks.

## [2022.1.28]

Franklin T9: Auto Reboot

- Added Auto Reboot section to Franklin T9 page.
- De-duplicating steps in multiple GitHub Actions workflows by defining my own composite action in this same repo.
- Optimizing GitHub Actions by only installing dev dependencies in ci.yml and not deploy/diff.
- Linting CHANGELOG.md file in CI via pytest.

## [2022.1.4]

New page: MIB2 Hacking

- Added MIB2 Composition Media Hacking with some initial findings.

## [2022.1.2]

Alltrack page: MIB2 Developer Mode

- Added MIB2 Developer Mode section to Alltrack page.

## [2021.12.31]

Alltrack page: Forums links

- Enabling MyST `fieldlist` extension for future use.
- Added forums post links to latest Alltrack page entries.
- Resolved Pygments dependency TODO now that v2.11 has been released.

## [2021.12.24]

Euro Tail Lights, license links, diff HTML files

- Diffing HTML files between workflow build and current production.
- Added Euro Tail Lights section to Alltrack page.
- Added Tweaks and Software section to Windows 11 on a Mac page.
- Moved all images to Imgur now that sphinx-imgur works fine with OpenGraph.
- Added link to LICENSE file in the left sidebar.

## [2021.12.13]

Windows 11 on a Mac: BIOS and EFI bootable

- Restyled commands in Windows 11 on Mac page.
- Made Windows 11 Boot Camp ISO bootable on traditional BIOS and UEFI PCs.

## [2021.12.11]

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

## [2021.12.7]

Style consistency

- Made resume link style consistent with the other links within the admonition in index.md.
- Split custom.css into two scoped files.
- Reordered Tutorials TOC list.

## [2021.12.5]

Background image and autobiography

- TOCTree: Reorganized and grouped into new names.
- Converted index.rst into index.md.
- GitHub button at the top no longer is a mouseover menu. Links directly to `/blob/` like the RTD theme.
- Stop creating `_sources` directory, source files already on public GitHub.
- Adding a background image to every page.
- Adding a short autobiography.

## [2021.12.3]

Latest Imgur extension with OpenGraph support

- Using rsync `--delete-after` to avoid race condition where files are removed before index.html is updated.
- Switch from old and crap-patched to new and proper [sphinx-imgur](https://sphinx-imgur.readthedocs.io/) extension. Fixes
  compatibility with opengraph extension.
- Fixed image alignments in some documents where two or three images are supposed to sit side by side flush with each other.
- Updating photo albums with new (old) rack cabinet albums.
- Changed OpenGraph type from "article" to "website". They look the same in Discord and article has a bunch of extra tags
  that I won't be using: https://ogp.me/#no_vertical

## [2021.11.25]

Franklin T9 page updates, dependency updates

- Added Flash Dumps, lsusb, and fastboot output sections.
- Large opengraph images when posting to Discord.
- Using unreleased pygments with dts syntax highlighting fix.
- Using newer unreleased sphinxcontrib-youtube extension.
- Updated opengraph extension with absolute path fix.

## [2021.11.12]

Franklin T9 page updates and changes

- Added pictures of circuit board without RF shields.
- Using subsections under Interesting Information section.
- Moving large command outputs into external files instead of embedding in franklin_t9.md.
- Changed order of Interesting Info section.
- Added device tree, full kernel config, datasheets, notes section, uname, lsmod, dmesg, and build.prop.
- Added steps on how to use SSH key authentication.

## [2021.11.9]

New sections for Franklin T9 Hacking

- Added new sections: Fastboot, ADB, Automatic Power On, and Interesting Information.

## [2021.11.5]

New page: T-Mobile Franklin T9 Hacking

- Remove "documentation" from every `<title />`.
- Generate a sitemap.xml file and reference it in a now-dynamic robots.txt file.
- Setting baseline natural language to "en" for assistive technology.
- Remove tests since they're all disabled and one (docker) has a [security issue](https://github.com/docker/docker-py/issues/2902).
- Update 404 page with a Lemmings iframe.

## [2021.10.25]

Updating Monoprice Maker Select v2 and Golf Alltrack SE, better date formatting

- Using "Oct `21" datestamps instead of "21-10" to make it more human-readable.
- Adding EcoHitch Install and Upgrading Parts posts.

## [2021.10.21]

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

## [2021.9.10]

Moving Google Analytics to Cloudflare

## [2021.9.9]

Updating Golf Alltrack SE

- Added Rear Dashcam Pair section
- Using definition list instead of glossary for duplicates

## [2021.9.6]

Updating Golf Alltrack SE

- Adding OBDeleven mods with some pictures.
- Split Dashcam section into two parts.

## [2021.8.28]

Updating Golf Alltrack SE

- Embedding drag race youtube video.

## [2021.8.27]

Added Golf Alltrack SE

- Updated Python dependencies.
- Adding new page: Golf Alltrack SE

## [2021.6.15]

Refreshed Website

- Recent version of Sphinx and other Python libraries.
- Using new Sphinx theme.
- New vector-based favicon.
- Deploy from GitHub Actions.
- Dropped SCVersioning.
- Using Python Poetry instead of setuptools and tox.
