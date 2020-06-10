import re
import os
from enum import Enum
from minigalaxy.paths import CACHE_DIR
from minigalaxy.config import Config

class Game:
    state = Enum('state', 'DOWNLOADABLE INSTALLABLE UPDATABLE QUEUED DOWNLOADING INSTALLING INSTALLED NOTLAUNCHABLE UNINSTALLING UPDATING UPDATE_QUEUED UPDATE_DOWNLOADING UPDATE_INSTALLABLE')
    
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
        self.genre: str = None
        self.genres: list[str] = []
        self.updates: int = 0
        self.dlc_count: int = 0
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
        
                # Set folder for download installer
        self.download_dir = os.path.join(CACHE_DIR, "download")
        self.download_path = os.path.join(self.download_dir, self.name)
        
        # Set folder for update installer
        self.update_dir = os.path.join(CACHE_DIR, "update")
        self.update_path = os.path.join(self.update_dir, self.name)

        # Set folder if user wants to keep installer (disabled by default)
        self.keep_dir = os.path.join(Config.get("install_dir"), "installer")
        self.keep_path = os.path.join(self.keep_dir, self.name)

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
            
        self.download = []
        
    def get_install_dir(self):
        if self.install_dir:
            return self.install_dir
        return os.path.join(Config.get("install_dir"), self.get_install_directory_name())

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
        self.supported_platforms.append(language)

    def get_stripped_name(self):
        return self.__strip_string(self.name)

    def get_install_directory_name(self):
        return re.sub('[^A-Za-z0-9 ]+', '', self.name)

    def __strip_string(self, string):
        return re.sub('[^A-Za-z0-9]+', '', string)

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
