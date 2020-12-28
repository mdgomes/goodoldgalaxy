import re
import os
import json
import datetime
import unicodedata
import string
from enum import Enum
from goodoldgalaxy.paths import CACHE_DIR
from goodoldgalaxy.config import Config
from goodoldgalaxy.constants import IETF_CODES_TO_DOWNLOAD_LANGUAGES

class Game:
    state = Enum('state', 'DOWNLOADABLE INSTALLABLE UPDATABLE QUEUED DOWNLOADING INSTALLING INSTALLED NOTLAUNCHABLE UNINSTALLING UPDATING UPDATE_QUEUED UPDATE_DOWNLOADING UPDATE_INSTALLABLE')
    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    char_limit = 255
    
    def __init__(self, 
                 name: str, 
                 url: str = None, 
                 game_id: int = 0
        ):
        self.name = name
        self.url = url
        self.id = game_id
        self.install_dir: str = None
        self.image_url: str = None
        self.icon_url: str = None
        self.sidebar_icon_url: str = None
        self.logo_url: str = None
        self.background_url: str = None
        self.platform: str = None
        self.supported_platforms: list[str] = []
        self.type : str = "game"
        self.genre: str = None
        self.genres: list[str] = []
        self.updates: int = 0
        self.dlc_count: int = 0
        self.dlcs = []
        self.tags: str = []
        self.release_date: str = None
        self.language: str = None
        self.supported_languages: list[str] = []
        self.installed: int = 0
        self.installed_version: str = None
        self.available_version: str = None
        self.state:Enum = self.state.INSTALLABLE
        self.cache_dir: str = os.path.join(CACHE_DIR, "game/{}".format(game_id))
        if os.path.exists(self.cache_dir) == False:
            os.makedirs(self.cache_dir)
        self.is_gog_game: int = 0
        self.sidebar_tile = None
        self.list_tile = None
        self.grid_tile = None
        self.safe_name = self.__clean_filename(self.name)

        self.dlc_status_list = ["not-installed", "installed", "updatable"]
        self.dlc_status_file_name = "goodoldgalaxy-dlc.json"
        self.dlc_status_file_path = ""
        
        # Set folder for download installer
        self.download_dir = os.path.join(CACHE_DIR, "download")
        self.download_path = os.path.join(self.download_dir, self.safe_name)
        
        # Set folder for update installer
        self.update_dir = os.path.join(CACHE_DIR, "update")
        self.update_path = os.path.join(self.update_dir, self.safe_name)

        # Set folder if user wants to keep installer (disabled by default)
        self.keep_dir = os.path.join(Config.get("install_dir"), "installer")
        self.keep_path = os.path.join(self.keep_dir, self.safe_name)

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        
        # available downloads
        self.__downloads = []

    def get_install_dir(self):
        if self.install_dir:
            return self.install_dir
        return os.path.join(Config.get("install_dir"), self.get_install_directory_name())
    
    def get_installers(self) -> list:
        """
        Gets the list of available installers.
        
        Return:
        -------
            List of available installers
        """
        return self.__downloads

    def set_installed(self, platform: str, install_dir:str , installed_version:str = None):
        self.installed = 1
        self.platform = platform
        self.install_dir = install_dir
        # set installed version if given
        if installed_version is not None:
            self.installed_version = installed_version
        # set game to installed
        self.state = self.state.INSTALLED
        # make sure platform is in supported platforms
        if platform is not None and platform not in self.supported_platforms:
            self.supported_platforms.append(platform)
        self.dlc_status_file_path = os.path.join(self.install_dir, self.dlc_status_file_name)

    def set_main_genre(self,genre:str):
        self.genre = genre
        # make sure genre is in genres
        if genre is not None and genre not in self.genres:
            self.genres.append(genre)

    def add_genre(self, genre:str):
        if self.genre is None:
            self.set_main_genre(genre)
            return
        self.genres.append(genre)

    def set_installed_language(self, language:str):
        self.language = language
        # make sure supported languages has this language
        if language is not None and language not in self.supported_languages:
            self.supported_languages.append(language)

    def add_language(self, language:str):
        if self.language is None:
            self.set_installed_language(language)
            return
        self.supported_languages.append(language)

    def get_stripped_name(self):
        return self.__strip_string(self.name)

    def get_install_directory_name(self):
        return re.sub('[^A-Za-z0-9 ]+', '', self.name)

    @staticmethod
    def __strip_string(string):
        return re.sub('[^A-Za-z0-9]+', '', string)

    def read_installed_version(self):
        if self.installed == 0:
            return
        gameinfo = os.path.join(self.install_dir, "gameinfo")
        gameinfo_list = []
        if os.path.isfile(gameinfo):
            with open(gameinfo, 'r') as file:
                gameinfo_list = file.readlines()
        if len(gameinfo_list) > 1:
            version = gameinfo_list[1].strip()
        else:
            version = ""
        self.installed_version = version
        self.dlc_status_file_path = os.path.join(self.install_dir, self.dlc_status_file_name)

    def validate_if_installed_is_latest(self, installers):
        self.read_installed_version()
        if not self.installed_version:
            is_latest = False
        else:
            current_installer = None
            for installer in installers:
                if installer["os"] == self.platform:
                    current_installer = installer
                    break
            if current_installer is not None and current_installer["version"] != self.installed_version:
                is_latest = False
            else:
                is_latest = True
        return is_latest

    def get_dlc_status(self, dlc_title, available_version):
        json_list = ["", ""]
        self.read_installed_version()
        status = self.dlc_status_list[0]
        if self.installed_version:
            if os.path.isfile(self.dlc_status_file_path):
                dlc_staus_file = open(self.dlc_status_file_path, 'r')
                json_list = json.load(dlc_staus_file)
                dlc_status_dict = json_list[0]
                dlc_staus_file.close()
                if dlc_title in dlc_status_dict:
                    status = dlc_status_dict[dlc_title]
                else:
                    status = self.dlc_status_list[0]
        if status == self.dlc_status_list[1]:
            installed_version_dcit = json_list[1]
            if dlc_title in installed_version_dcit:
                installed_version = installed_version_dcit[dlc_title]
                if available_version != installed_version:
                    status = self.dlc_status_list[2]
        return status
    
    def get_dlc_installed_version(self, dlc_title):
        json_list = ["", ""]
        self.read_installed_version()
        installed_version = None
        status = None
        if self.installed_version:
            if os.path.isfile(self.dlc_status_file_path):
                dlc_staus_file = open(self.dlc_status_file_path, 'r')
                json_list = json.load(dlc_staus_file)
                dlc_status_dict = json_list[0]
                dlc_staus_file.close()
                if dlc_title in dlc_status_dict:
                    status = dlc_status_dict[dlc_title]
                else:
                    status = self.dlc_status_list[0]
        if status == self.dlc_status_list[1]:
            installed_version_dcit = json_list[1]
            if dlc_title in installed_version_dcit:
                return installed_version_dcit[dlc_title]
        return installed_version

    def set_dlc_status(self, dlc_title, status, version):
        self.read_installed_version()
        dlc_status_dict = {}
        if self.installed_version:
            if os.path.isfile(self.dlc_status_file_path):
                dlc_staus_file = open(self.dlc_status_file_path, 'r')
                json_list = json.load(dlc_staus_file)
                dlc_status_dict = json_list[0]
                dlc_version = json_list[1]
                dlc_staus_file.close()
            else:
                dlc_status_dict = {}
                dlc_version = {}
            for dlc in self.dlcs:
                if dlc.name not in dlc_status_dict:
                    dlc_status_dict[dlc.name] = self.dlc_status_list[0]
            if status:
                dlc_status_dict[dlc_title] = self.dlc_status_list[1]
                dlc_version[dlc_title] = version
            else:
                dlc_status_dict[dlc_title] = self.dlc_status_list[0]
            dlc_status_file = open(self.dlc_status_file_path, 'w')
            json.dump([dlc_status_dict, dlc_version], dlc_status_file)
            dlc_status_file.close()

    def add_dlc_from_json(self, product, platform=None, language=None):
        if product is None:
            return
        for i in self.dlcs:
            if i.id == product["id"]:
                # dlc already exists, ignore
                return
        supported_platforms = []
        # this will probably say false to all, we will check later in the installers
        if product["content_system_compatibility"]["linux"]:
            supported_platforms.append("linux")
        if product["content_system_compatibility"]["windows"]:
            supported_platforms.append("windows")
        if product["content_system_compatibility"]["osx"]:
            supported_platforms.append("mac")
        release_date = None
        if "release_date" in product:
            release_date = datetime.datetime.strptime(product["release_date"], '%Y-%m-%dT%H:%M:%S%z')
        dlc = Game(name=product["title"], url=product["purchase_link"], game_id=product["id"])
        dlc.updates=0
        dlc.image_url = product["images"]["menuNotificationAv"]
        dlc.icon_url = product["images"]["icon"]
        dlc.sidebar_icon_url = product["images"]["sidebarIcon"]
        dlc.logo_url = product["images"]["logo"]
        dlc.background_url = product["images"]["background"]
        dlc.set_main_genre(self.genre)
        dlc.supported_platforms=supported_platforms
        dlc.release_date = release_date
        dlc.type = "dlc"
        dlc.install_dir = self.install_dir
        dlc.supported_languages = []
        # process languages
        if product["languages"]:
            for lang in product["languages"]:
                dlc.supported_languages.append(product["languages"][lang])
        # process installers to extract current version and supported platforms
        if product["downloads"] and product["downloads"]["installers"]:
            # clear downloads list
            dlc.__downloads = []
            installer_platforms = {}
            for installer in product["downloads"]["installers"]:
                dlc.__downloads.append(installer)
                # so each installer may report a different version
                if installer["os"] not in installer_platforms and installer["os"] not in dlc.supported_platforms:
                    dlc.supported_platforms.append(installer["os"])
                # if installer os is the same as the installed game platform (or the current platform if not installed) 
                # and the same language use that as the source for the version
                if self.installed > 0 and installer["os"] == self.platform and installer["language"] == IETF_CODES_TO_DOWNLOAD_LANGUAGES[self.language]:
                    dlc.available_version = installer["version"]
                elif self.installed == 0 and installer["os"] == "linux" and installer["language"] == Config.get("lang"):
                    dlc.available_version = installer["version"]
            if dlc.available_version is None:
                # loop again but this time be less picky
                for installer in product["downloads"]["installers"]:
                    # if installer os is the same as the installed game platform (or the current platform if not installed) 
                    # and the same language use that as the source for the version
                    if self.installed > 0 and installer["os"] == self.platform and installer["language"] == IETF_CODES_TO_DOWNLOAD_LANGUAGES[self.language]:
                        dlc.available_version = installer["version"]
                    elif self.installed == 0 and installer["os"] == "windows" and installer["language"] == Config.get("lang"):
                        dlc.available_version = installer["version"]
            if dlc.available_version is None:
                print("Failed all conditions to get DLC version!!")
        dlc.installed = 1 if self.get_dlc_status(dlc.name, dlc.available_version) == "installed" else 0
        dlc.installed_version = self.get_dlc_installed_version(dlc.name)
        if dlc.installed == 1:
            dlc.state = self.state.INSTALLED
            dlc.language = self.language
            dlc.platform = self.platform
            dlc.updates = 1 if dlc.installed_version != dlc.available_version else 0
        else:
            dlc.platform = platform
            dlc.language = language
        # add DLC to supported DLCs for this game
        if dlc.updates == 1:
            dlc.state = self.state.UPDATABLE
        self.dlcs.append(dlc)

    def __clean_filename(self, filename, whitelist=valid_filename_chars, replace=' '):
        # replace spaces
        for r in replace:
            filename = filename.replace(r,'_')
        
        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
        
        # keep only whitelisted chars
        cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
        if len(cleaned_filename)>self.char_limit:
            print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(self.char_limit))
        return cleaned_filename[:self.char_limit]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if self.id > 0 and other.id > 0:
            if self.id == other.id:
                return True
            else:
                return False
        if self.name == other.name:
            return True
        # Compare names with special characters and capital letters removed
        if self.get_stripped_name().lower() == other.get_stripped_name().lower():
            return True
        if self.install_dir and other.get_stripped_name() in self.__strip_string(self.install_dir):
            return True
        if other.install_dir and self.get_stripped_name() in self.__strip_string(other.install_dir):
            return True
        return False

    def __lt__(self, other):
        names = [str(self), str(other)]
        names.sort()
        if names[0] == str(self):
            return True
        return False
