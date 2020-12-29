import requests
import platform
from goodoldgalaxy.translation import _
from goodoldgalaxy.version import VERSION
from goodoldgalaxy.paths import DEFAULT_INSTALL_DIR

SUPPORTED_DOWNLOAD_LANGUAGES = [
    ["br", _("Brazilian Portuguese")],
    ["cn", _("Chinese")],
    ["da", _("Danish")],
    ["nl", _("Dutch")],
    ["en", _("English")],
    ["fi", _("Finnish")],
    ["fr", _("French")],
    ["de", _("German")],
    ["hu", _("Hungarian")],
    ["it", _("Italian")],
    ["jp", _("Japanese")],
    ["ko", _("Korean")],
    ["no", _("Norwegian")],
    ["pl", _("Polish")],
    ["pt", _("Portuguese")],
    ["ru", _("Russian")],
    ["es", _("Spanish")],
    ["sv", _("Swedish")],
    ["tr", _("Turkish")]
]

DOWNLOAD_LANGUAGES_TO_GOG_CODE = {
    _("Brazilian Portuguese"): "br",
    _("Chinese"): "cn",
    _("Danish"): "da",
    _("Dutch"): "nl",
    _("English"): "en",
    _("Finnish"): "fi",
    _("French"): "fr",
    _("German"): "de",
    _("Hungarian"): "hu",
    _("Italian"): "it",
    _("Japanese"): "jp",
    _("Korean"): "ko",
    _("Norwegian"): "no",
    _("Polish"): "pl",
    _("Portuguese"): "pt",
    _("Russian"): "ru",
    _("Spanish"): "es",
    _("Swedish"): "sv",
    _("Turkish"): "tr"
}

FEATURES = {
    "achievements": _("Achievements"),
    "cloud_saves": _("Cloud Saves"),
    "controller_support": _("Controller Support"),
    "coop": _("Co-op"),
    "in_development": _("In Development"),
    "leaderboards": _("Leaderboards"),
    "multi": _("Multi-player"),
    "overlay": _("Overlay"),
    "single": _("Single-player")
}

GENRES = {
    "action": _("Action"),
    "adventure": _("Adventure"),
    "arcade": _("Arcade"),
    "building": _("Building"),
    "chess": _("Chess"),
    "combat": _("Combat"),
    "comedy": _("Comedy"),
    "detective": _("Detective-mystery"),
    "economic": _("Economic"),
    "educational": _("Educational"),
    "espionage": _("Espionage"),
    "fantasy": _("Fantasy"),
    "fighting": _("Fighting"),
    "fpp": _("FPP"),
    "historical": _("Historical"),
    "horror": _("Horror"),
    "managerial": _("Managerial"),
    "metroidvania": _("Metroidvania"),
    "modern": _("Modern"),
    "mystery": _("Mystery"),
    "narrative": _("Narrative"),
    "naval": _("Naval"),
    "offroad": _("Off-road"),
    "openworld": _("Open World"),
    "pinball": _("Pinball"),
    "platformer": _("Platformer"),
    "pointandclick": _("Point-and-click"),
    "puzzle": _("Puzzle"),
    "racing": _("Racing"),
    "rally": _("Rally"),
    "realtime": _("Real-time"),
    "rougelike": _("Roguelike"),
    "rpg": _("Role-playing"),
    "sandbox": _("Sandbox"),
    "scifi": _("Sci-fi"),
    "shooter": _("Shooter"),
    "simulation": _("Simulation"),
    "soccer": _("Soccer"),
    "sports": _("Sports"),
    "stealth": _("Stealth"),
    "strategy": _("Strategy"),
    "survival": _("Survival"),
    "tactical": _("Tactical"),
    "teamsport": _("Team sport"),
    "touring": _("Touring"),
    "tpp": _("TPP"),
    "turnbased": _("Turn-based"),
    "virtuallife": _("Virtual life")
}

IETF_DOWNLOAD_LANGUAGES = {
    "br": _("Brazilian Portuguese"),
    "cn": _("Chinese"),
    "da": _("Danish"),
    "nl": _("Dutch"),
    "en": _("English"),
    "fi": _("Finnish"),
    "fr": _("French"),
    "de": _("German"),
    "hu": _("Hungarian"),
    "it": _("Italian"),
    "jp": _("Japanese"),
    "ko": _("Korean"),
    "no": _("Norwegian"),
    "pl": _("Polish"),
    "pt": _("Portuguese"),
    "ru": _("Russian"),
    "es": _("Spanish"),
    "sv": _("Swedish"),
    "tr": _("Turkish")
}

IETF_CODES = {
    "*": _("Neutral"),
    "ar-SA": _("Arabic"),
    "be-BY": _("Belarusian"),
    "bg-BG": _("Bulgarian"),
    "ca-ES": _("Catalan"),
    "cs-CZ": _("Czech"),
    "da-DK": _("Danish"),
    "de-DE": _("German"),
    "en-US": _("English"),
    "es-ES": _("Spanish"),
    "es-MX": _("Mexican Spanish"),
    "fa-IR": _("Persian"),
    "fi-FI": _("Finnish"),
    "fr-FR": _("French"),
    "el-GR": _("Greek"),
    "he-IL": _("Hebrew"),
    "hu-HU": _("Hungarian"),
    "is-IS": _("Icelandic"),
    "it-IT": _("Italian"),
    "iu-CA": _("Inuktitut"),
    "ja-JP": _("Japanese"),
    "ko-KR": _("Korean"),
    "nb-NO": _("Norwegian Bokmål"),
    "nl-NL": _("Dutch"),
    "no-NO": _("Norwegian"),
    "pl-PL": _("Polish"),
    "pt-BR": _("Brazilian Portuguese"),
    "pt-PT": _("Portuguese"),
    "ro-RO": _("Romanian"),
    "ru-RU": _("Russian"),
    "sr-RS": _("Serbian"),
    "sk-SK": _("Slovak"),
    "sv-SE": _("Swedish"),
    "th-TH": _("Thai"),
    "tr-TR": _("Turkish"),
    "uk-UA": _("Ukrainian"),
    "zh-CN": _("Chinese"),
    "zh-Hans-CN": _("Simplified Chinese"),
    "zh-Hant-CN": _("Traditional Chinese")
}

IETF_CODES_TO_DOWNLOAD_LANGUAGES = {
    "ar-SA": "ar",
    "be-BY": "be",
    "bg-BG": "bg",
    "ca-ES": "es",
    "cs-CZ": "cs",
    "da-DK": "da",
    "de-DE": "de",
    "en-US": "en",
    "en-GB": "en",
    "es-ES": "es",
    "es-MX": "es",
    "fa-IR": "fa",
    "fi-FI": "fi",
    "fr-FR": "fr",
    "el-GR": "gr",
    "he-IL": "he",
    "hu-HU": "hu",
    "is-IS": "is",
    "it-IT": "it",
    "iu-CA": "iu",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "nb-NO": "nb",
    "nl-NL": "nl",
    "no-NO": "no",
    "pl-PL": "pl",
    "pt-BR": "br",
    "pt-PT": "pt",
    "ro-RO": "ro",
    "ru-RU": "ru",
    "sr-RS": "sr",
    "sk-SK": "sk",
    "sv-SE": "sv",
    "th-TH": "th",
    "tr-TR": "tr",
    "uk-UA": "uk",
    "zh-CN": "cn",
    "zh-Hans-CN": "cn",
    "zh-Hant-CN": "cn"
}

PROD_TYPES = {
    "game": _("Game"),
    "movie": _("Movie"),
    "dlc": _("DLC"),
    "pack": _("Package")
}

DL_TYPES = {
    "installers": _("Installer"),
    "patches": _("Patch"),
    "language_packs": _("Language pack"),
    "bonus_content": _("Bonus")
}

BONUS_TYPES = {
    "manuals": _("Manuals"),
    "artworks": _("Artworks"),
    "avatars": _("Avatars"),
    "audio": _("Audio"),
    "guides & reference": _("Guides & Reference"),
    "wallpapers": _("Wallpapers"),
    "game add-ons": _("Game Add-ons"),
    "video": _("Videos")
}

# The default values for new configuration files
DEFAULT_CONFIGURATION = {
    "lang": "en",
    "install_dir": DEFAULT_INSTALL_DIR,
    "create_shortcuts": True,
    "keep_installers": False,
    "stay_logged_in": True,
    "show_fps": False,
    "show_windows_games": False
}

# Game IDs to ignore when received by the API
IGNORE_GAME_IDS = [
    1424856371,  # Hotline Miami 2: Wrong Number - Digital Comics
    1980301910,  # The Witcher Goodies Collection
    2005648906,  # Spring Sale Goodies Collection #1
]

DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB

# This is the file size needed for the download manager to consider resuming worthwhile
MINIMUM_RESUME_SIZE = 50 * 1024**2  # 50 MB

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'goodoldgalaxy/{} (Linux {})'.format(VERSION, platform.machine())})
