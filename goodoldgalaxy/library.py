'''
Created on 07/05/2020

@author: Miguel Gomes <alka.setzer@gmail.com>
'''
import os
import re
import json
import time
from typing import List
from goodoldgalaxy.api import Api
from goodoldgalaxy.config import Config
from goodoldgalaxy.game import Game

class Library():

    def __init__(self, api: Api):
        self.api = api
        self.games = []
        self.genres = []
        self.tags = []
        self.offline = False
        self.last_api_check = 0
        self.fetching = 0
        
    def __get_installed_games(self) -> List[Game]:
        games = []
        directories = os.listdir(Config.get("install_dir"))
        for directory in directories:
            full_path = os.path.join(Config.get("install_dir"), directory)
            # Only scan directories
            if not os.path.isdir(full_path):
                continue
            # Make sure the gameinfo file exists
            gameinfo = os.path.join(full_path, "gameinfo")
            if os.path.isfile(gameinfo):
                with open(gameinfo, 'r') as file:
                    name = file.readline().strip()
                    version = file.readline().strip()
                    version_dev = file.readline().strip()
                    language = file.readline().strip()
                    game_id = file.readline().strip()
                    if not game_id:
                        game_id = 0
                    else:
                        game_id = int(game_id)
                game = Game(name=name, game_id=game_id)
                game.set_installed("linux", full_path, version)
                game.set_installed_language(language)
                games.append(game)
            else:
                game_files = os.listdir(full_path)
                for file in game_files:
                    if re.match(r'^goggame-[0-9]*\.info$', file):
                        with open(os.path.join(full_path, file), 'r') as info_file:
                            info = json.loads(info_file.read())
                            game = Game(name=info["name"], game_id=int(info["gameId"]))
                            game.set_installed("windows",full_path)
                            game.set_installed_language(info["language"])
                            for lang in info["languages"]:
                                game.add_language(lang)
                            games.append(game)
        return games
    
    def __validate_if_installed_is_latest(self,game,info) -> bool:
        if (game.installed_version is None or len(game.installed_version) == 0):
            return False
        installers = info["downloads"]["installers"];
        current_installer = None
        for installer in installers: 
            if (installer["os"] != game.platform):
                continue;
            current_installer = installer
            break            
        # validate if we have the latest version
        return (current_installer is not None and current_installer["version"] == game.installed_version)
    
    def __get_games_from_api(self):
        try:
            retrieved_games = self.api.get_library()
            self.offline = False
        except:
            self.offline = True
            return
        # complete information with api calls
        ginfos = self.api.get_infos(retrieved_games)
        gmap = {}
        for product in ginfos:
            gmap[str(product["id"])] = product
        cats = set()
        tags = set()
        langs = {}
        for game in retrieved_games:
            # add genres
            if game.genre is not None and len(game.genre) > 0:
                cats.add(game.genre)
            # add tags
            if game.tags is not None:
                for tag in game.tags:
                    if len(tag) > 0:
                        tags.add(tag)
            if game in self.games:
                # Make sure the game id is set if the game is installed
                for installed_game in self.games:
                    if game == installed_game:
                        game.installed = installed_game.installed
                        game.is_gog_game = 1
                        game.install_dir = installed_game.install_dir
                        game.installed_version = installed_game.installed_version
                        game.platform = installed_game.platform
                        game.language = installed_game.language
                        game.sidebar_tile = installed_game.sidebar_tile
                        game.list_tile = installed_game.list_tile
                        game.grid_tile = installed_game.grid_tile
                        # also check if we have the most up to date version or not
                        try:
                            resp=gmap[str(game.id)]
                            if resp is None:
                                resp = self.api.get_info(game)
                            game.updates = 0 if self.__validate_if_installed_is_latest(game,resp) == True else 1
                            game.sidebar_icon_url = resp["images"]["sidebarIcon"]
                            game.logo_url = resp["images"]["logo"]
                            game.icon_url = resp["images"]["icon"]
                            game.background_url = resp["images"]["background"]
                            supported_languages=[]
                            if resp["languages"]:
                                for lang in resp["languages"]:
                                    langs[lang] = resp["languages"][lang]
                                    supported_languages.append(resp["languages"][lang])
                            game.supported_languages=supported_languages
                        except:
                            print("Could not fetch current information about {}".format(game.name))
                        self.games.remove(installed_game)
                        break
            self.games.append(game)
        # handle self installed games that may exist on gog
        for game in self.games:
            if game.is_gog_game == 1:
                continue
            try:
                resp = self.api.get_info(game)
                game.updates = 0 if self.__validate_if_installed_is_latest(game,resp) == True else 1
                game.sidebar_icon_url = resp["images"]["sidebarIcon"]
                game.logo_url = resp["images"]["logo"]
                game.icon_url = resp["images"]["icon"]
                game.background_url = resp["images"]["background"]
                supported_languages=[]
                if resp["languages"]:
                    for lang in resp["languages"]:
                        langs[lang] = resp["languages"][lang]
                        supported_languages.append(resp["languages"][lang])
                    game.supported_languages=supported_languages
            except:
                print("Could not fetch current information about {}".format(game.name))
        # reset genres and tags and use the new information we got
        self.genres = []
        for cat in cats:
            self.genres.append(cat)
        self.genres.sort()
        self.tags = []
        for tag in tags:
            self.tags.append(tag)
        self.tags.sort()
        self.last_api_check = time.time()
        
    def update_dlcs_for_game(self, game: Game):
        """
        Update DLCs for a given game.
        
        Parameters:
        -----------
            game: Game -> Game for which we want to know about dlc's
        """
        if game is None:
            return
        response = self.api.get_info(game)
        if "expanded_dlcs" in response:
            dlcs = response["expanded_dlcs"]
            for dlc in dlcs:
                downloads = dlc["downloads"]
                for dltype in downloads:
                    if dltype == "bonus_content":
                        continue
                    items = downloads[dltype]
                    for item in items:
                        # add game to dlc list
                        game.add_dlc_from_json(dlc)
        
    
    def get_installed_games(self) -> List[Game]:
        return self.__get_installed_games()
    
    def get_games(self,forced: bool = False) -> List[Game]:
        if self.fetching == 1:
            return self.games
        # wait a some time before calling the API again
        if (forced == False and time.time() - self.last_api_check < 30):
            return self.games;
        # rebuild list
        self.fetching = 1
        self.games = self.__get_installed_games()
        self.__get_games_from_api()
        self.fetching = 0
        return self.games

    def get_sorted_games(self, key="game", reverse=False, sortfn = None) -> List[Game]:
        if (sortfn is None):
            return sorted(self.games, key, reverse)
        else:
            return sortfn(self.games, key, reverse)

    def get_filtered_games(self, installed = None, platform = None, genre = None, tag = None, state = None, name = None) -> List[Game]:
        if self.fetching == 1:
            return self.games
        games = []
        for game in self.games:
            if (self.is_game_filtered(game, installed, platform, genre, tag, state, name) == False):
                continue
            games.append(game)
        return games
        
    def is_game_filtered(self, game, installed = None, platform = None, genre = None, tag = None, state = None, name = None) -> bool:
        if (installed == True and game.installed == 0):
            return False
        if (platform is not None):
            # string
            if isinstance(platform,str) and platform not in game.platforms:
                return False
            elif isinstance(platform, list):
                found = False
                for plat in platform:
                    if plat in game.supported_platforms:
                        found = True
                        break
                if found == False:
                    return False
        if (genre is not None):
            # string
            if isinstance(genre,str) and genre not in game.genres:
                return False
            elif isinstance(genre, list):
                found = False
                for cat in genre:
                    if cat in game.genres:
                        found = True
                        break
                if found == False:
                    return False
        if (tag is not None):
            # string
            if isinstance(tag,str) and tag not in game.ags:
                return False
            elif isinstance(tag, list):
                found = False
                for t in tag:
                    if t in game.tags:
                        found = True
                        break
                if found == False:
                    return False
        if (state is not None):
            # string
            if isinstance(state,str) and ((state == "installed" and game.installed == 0) or (state == "updated" and game.updates == 0)):
                return False
            elif isinstance(state, list):
                # state handles as an AND of state instead of an OR like the other filters 
                found = 0
                for stat in state:
                    if (stat == "installed" and game.installed > 0) or (stat == "updated" and game.updates > 0):
                        found = found + 1
                        break
                if found < len(state):
                    return False
        if (name is not None):
            try:
                game.name.lower().index(name.lower())
            except ValueError:
                return False
        return True
