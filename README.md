# Good Old Galaxy

A simple GOG client for Linux forked from [Minigalaxy](https://github.com/sharkwouter/minigalaxy).

![screenshot](screenshot.jpg?raw=true)

## Features

The most important features of Good Old Galaxy:

- Log in with your GOG account
- Download the Linux games you own on GOG
- Launch them

In addition to that, Good Old Galaxy also allows you to:

- Update your games
- Install and update DLC
- Download your goodies
- Select in which language you'd prefer to download your games
- Change where games are installed
- Create launcher icons on desktop
- Search your GOG Linux library
- Show all games or just the ones you've installed
- Filter your library by genre, operating system, language or tags
- View the error message if a game fails to launch
- Enable displaying the FPS in games
- Use the system's Scummvm or Dosbox installation
- Install Windows games using Wine

## Supported languages

Currently Good Old Galaxy can be displayed in the following languages:
- Brazilian Portuguese
- English
- Dutch
- French
- German
- Norwegian Bokmål
- Norwegian Nynorsk
- Polish
- Russian
- Simplified Chinese
- Spanish
- Taiwanese Mandarin
- Turkish

## System requirements

Good Old Galaxy should work on the following distributions:

- Debian Buster (10.0) or newer
- Ubuntu 18.10 or newer
- Arch Linux
- Manjaro
- Fedora 31+
- openSUSE Tumbleweed
- Gentoo
- MX Linux 19
- Solus

Good Old Galaxy does **not** ship for the following distributions because they do not contain the required version of PyGObject:

- Ubuntu 18.04
- Linux Mint 19.3
- openSUSE 15.1

Other Linux distributions may work as well. Good Old Galaxy requires the following dependencies:

- GTK+
- Python 3
- PyGObject 3.29.1+
- Webkit2gtk with API version 4.0 support
- Python Requests

## Installation

<details><summary>Other distributions</summary>

On other distributions Good Old Galaxy can be downloaded and started with the following commands:
<pre>
git clone https://github.com/mdgomes/goodoldgalaxy.git
cd goodoldgalaxy
bin/goodoldgalaxy
</pre>

This will be the development version. Alternatively a tarball of a specific release can be downloaded from the <a href="https://github.com/mdgomes/goodoldgalaxy/releases">releases page</a>.
</details>

## Support
Bugs reports and feature requests can also be made [here](https://github.com/mdgomes/goodoldgalaxy/issues).

## Contribute

Currently help is needed with the following:

- Reporting bugs in the [issue tracker](https://github.com/mdgomes/goodoldgalaxy/issues).
- Translating to different languages. Instructions [here](https://github.com/mdgomes/goodoldgalaxy/wiki/Translating-goodoldgalaxy).
- Testing issues with the ["needs testing"](https://github.com/mdgomes/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22needs+testing%22) tag. 
- Working on or giving input on issues with the ["help wanted"](https://github.com/mdgomes/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) or ["good first issue"](https://github.com/mdgomes/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) tag. Also check out the [the wiki](https://github.com/mdgomes/goodoldgalaxy/wiki/Developer-information) for developer information.

## Known issues

Expect to see the following issues:

* Some games will always show there is an update available.
* The option to open the store page for games doesn't work at the moment.

## Special thanks

Special thanks goes out to all contributors:

- sharkwouter for creating Minigalaxy on the first place
- makson96 for multiple code contributions
- Odelpasso for multiple code contributions
- SvdB-nonp for multiple code contributions
- tim77 for packaging minigalaxy for Fedora, Flathub and multiple code contributions
- larslindq for multiple code contributions
- BlindJerobine for translating to German and adding the support option
- JoshuaFern for packaging minigalaxy for NixOS and for contributing code
- sgn for fixing a bug
- s8321414 for translating to Taiwanese Mandarin
- fuzunspm for translating to Turkish
- thomansb22 for translating to French
- ArturWroblewski for translating to Polish
- kimmalmo for translating to Norwegian Bokmål
- EsdrasTarsis for translating to Brazilian Portuguese
- protheory8 for translating to Russian
- LordPilum for translating to Norwegian Nynorsk
- dummyx for translating to simplified Chinese
- juanborda for translating to Spanish
- jubalh for packaging minigalaxy for openSUSE
- gasinvein for packaging minigalaxy for flathub
- metafarion for packaging minigalaxy for Gentoo
- SwampRabbit and Steven Pusser for packaging minigalaxy for MX Linux
