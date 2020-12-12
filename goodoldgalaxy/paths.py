import os
import sys

LAUNCH_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
if LAUNCH_DIR == "/bin" or LAUNCH_DIR == "/sbin":
    LAUNCH_DIR = "/usr" + LAUNCH_DIR

CONFIG_DIR = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), "goodoldgalaxy")
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.json")
CACHE_DIR = os.path.join(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), "goodoldgalaxy")

THUMBNAIL_DIR = os.path.join(CACHE_DIR, "thumbnails")
DEFAULT_INSTALL_DIR = os.path.expanduser("~/GOG Games")

UI_DIR = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/ui"))
if not os.path.exists(UI_DIR):
    UI_DIR = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/ui"))

LOGO_IMAGE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/icons/192x192/io.github.mdgomes.goodoldgalaxy.png"))
if not os.path.exists(LOGO_IMAGE_PATH):
    LOGO_IMAGE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/icons/hicolor/192x192/apps/io.github.mdgomes.goodoldgalaxy.png"))

ICON_WINE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/winehq_logo_glass.png"))
if not os.path.exists(ICON_WINE_PATH):
    ICON_WINE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/winehq_logo_glass.png"))

ICON_WINDOWS_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/windows_icon.png"))
if not os.path.exists(ICON_WINDOWS_PATH):
    ICON_WINDOWS_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/windows_icon.png"))

ICON_LINUX_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/linux_icon.png"))
if not os.path.exists(ICON_LINUX_PATH):
    ICON_LINUX_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/linux_icon.png"))

ICON_MAC_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/mac_icon.png"))
if not os.path.exists(ICON_MAC_PATH):
    ICON_MAC_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/mac_icon.png"))

ICON_WINDOWS_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/windows_icon_light.png"))
if not os.path.exists(ICON_WINDOWS_LIGHT_PATH):
    ICON_WINDOWS_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/windows_icon_light.png"))

ICON_LINUX_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/linux_icon_light.png"))
if not os.path.exists(ICON_LINUX_LIGHT_PATH):
    ICON_LINUX_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/linux_icon_light.png"))

ICON_MAC_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/mac_icon_light.png"))
if not os.path.exists(ICON_MAC_LIGHT_PATH):
    ICON_MAC_LIGHT_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/mac_icon_light.png"))

ICON_UPDATE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/images/update_available.png"))
if not os.path.exists(ICON_UPDATE_PATH):
    ICON_UPDATE_PATH = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/images/update_available.png"))

LOCALE_DIR = os.path.abspath(os.path.join(LAUNCH_DIR, "../data/mo"))
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = os.path.abspath(os.path.join(LAUNCH_DIR, "../share/goodoldgalaxy/translations"))
