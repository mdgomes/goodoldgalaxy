# goodoldgalaxy

A simple GOG client for Linux

![screenshot](screenshot.jpg?raw=true)

## Features

The most important features of goodoldgalaxy:

- Log in with your GOG account
- Download the Linux games you own on GOG
- Launch them

In addition to that, goodoldgalaxy also allows you to:

- Update your games
- Install and update DLC
- Select in which language you'd prefer to download your games
- Change where games are installed
- Search your GOG Linux library
- Show all games or just the ones you've installed
- View the error message if a game fails to launch
- Enable displaying the FPS in games
- Use the system's Scummvm or Dosbox installation
- Install Windows games using Wine

## Supported languages

Currently goodoldgalaxy can be displayed in the following languages:
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

goodoldgalaxy should work on the following distributions:

- Debian Buster (10.0) or newer
- Ubuntu 18.10 or newer
- Arch Linux
- Manjaro
- Fedora 31+
- openSUSE Tumbleweed
- Gentoo
- MX Linux 19
- Solus

goodoldgalaxy does **not** ship for the following distributions because they do not contain the required version of PyGObject:

- Ubuntu 18.04
- Linux Mint 19.3
- openSUSE 15.1

Other Linux distributions may work as well. goodoldgalaxy requires the following dependencies:

- GTK+
- Python 3
- PyGObject 3.29.1+
- Webkit2gtk with API version 4.0 support
- Python Requests

## Installation

<a href="https://repology.org/project/goodoldgalaxy/versions">
    <img src="https://repology.org/badge/vertical-allrepos/goodoldgalaxy.svg" alt="Packaging status" align="right">
</a>

<details><summary>Ubuntu/Debian</summary>

Download the latest deb package from the <a href="https://github.com/sharkwouter/goodoldgalaxy/releases">releases page</a> and install it.
</details>
<details><summary>Arch/Manjaro</summary>

Available the <a href="https://aur.archlinux.org/packages/goodoldgalaxy">AUR</a>. You can use an AUR helper or use the following set of commands to install goodoldgalaxy on Arch:
<pre>
git clone https://aur.archlinux.org/goodoldgalaxy.git
cd goodoldgalaxy
makepkg -si
</pre>
</details>

<details><summary>Fedora</summary>

Available in <a href="https://src.fedoraproject.org/rpms/goodoldgalaxy">official repos</a> (F31+)
<pre>
sudo dnf install goodoldgalaxy
</pre>
</details>

<details><summary>openSUSE</summary>

Available in official repos for openSUSE Tumbleweed. You can use the following set of commands to install goodoldgalaxy on openSUSE from the devel project on <a href="https://build.opensuse.org/package/show/games:tools/goodoldgalaxy">OBS</a>:
<pre>
sudo zypper ar -f obs://games:tools gamestools
sudo zypper ref
sudo zypper in goodoldgalaxy
</pre>
</details>

<details><summary>Gentoo</summary>

Available in the <a href="https://github.com/metafarion/metahax">in the Metahax overlay</a>. Follow the instructions in the link to install goodoldgalaxy on Gentoo.
</details>

<details><summary>MX Linux</summary>

Currently available in the <a href="http://mxrepo.com/mx/repo/pool/main/m/goodoldgalaxy/">official repository</a>.  Please use MX Package Installer or Synaptic instead of manually installing the .deb from the repo.
</details>
<details><summary>Solus</summary>
 
Available in the official repositories. You can use the following command to install goodoldgalaxy on Solus:
<pre>
sudo eopkg it goodoldgalaxy
</pre>
</details>

<details><summary>Other distributions</summary>

On other distributions goodoldgalaxy can be downloaded and started with the following commands:
<pre>
git clone https://github.com/sharkwouter/goodoldgalaxy.git
cd goodoldgalaxy
bin/goodoldgalaxy
</pre>

This will be the development version. Alternatively a tarball of a specific release can be downloaded from the <a href="https://github.com/sharkwouter/goodoldgalaxy/releases">releases page</a>.
</details>

## Support
If you need any help using goodoldgalaxy, feel free to join the [goodoldgalaxy Discord server](https://discord.gg/RC4cXVD).
Bugs reports and feature requests can also be made [here](https://github.com/sharkwouter/goodoldgalaxy/issues).

## Contribute

Currently help is needed with the following:

- Reporting bugs in the [issue tracker](https://github.com/sharkwouter/goodoldgalaxy/issues).
- Translating to different languages. Instructions [here](https://github.com/sharkwouter/goodoldgalaxy/wiki/Translating-goodoldgalaxy).
- Testing issues with the ["needs testing"](https://github.com/sharkwouter/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22needs+testing%22) tag. 
- Working on or giving input on issues with the ["help wanted"](https://github.com/sharkwouter/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) or ["good first issue"](https://github.com/sharkwouter/goodoldgalaxy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) tag. Also check out the [the wiki](https://github.com/sharkwouter/goodoldgalaxy/wiki/Developer-information) for developer information.

Feel free to join the [goodoldgalaxy Discord](https://discord.gg/RC4cXVD) if you would like to help out.

## Known issues

Expect to see the following issues:

* Some games will always show there is an update available.
* The option to open the store page for games doesn't work at the moment.

## Special thanks

Special thanks goes out to all contributors:

- makson96 for multiple code contributions
- Odelpasso for multiple code contributions
- SvdB-nonp for multiple code contributions
- tim77 for packaging goodoldgalaxy for Fedora, Flathub and multiple code contributions
- larslindq for multiple code contributions
- BlindJerobine for translating to German and adding the support option
- JoshuaFern for packaging goodoldgalaxy for NixOS and for contributing code
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
- jubalh for packaging goodoldgalaxy for openSUSE
- gasinvein for packaging goodoldgalaxy for flathub
- metafarion for packaging goodoldgalaxy for Gentoo
- SwampRabbit and Steven Pusser for packaging goodoldgalaxy for MX Linux
