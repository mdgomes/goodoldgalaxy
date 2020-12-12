import os
import time
from urllib.parse import urlencode
import json
import math
from typing import List
from goodoldgalaxy.game import Game
from goodoldgalaxy.achievement import Achievement
from goodoldgalaxy.constants import IGNORE_GAME_IDS, SESSION
from goodoldgalaxy.paths import CACHE_DIR
from goodoldgalaxy.config import Config
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager
from goodoldgalaxy import achievement

class NoDownloadLinkFound(BaseException):
    pass


class Api:
    def __init__(self):
        self.login_success_url = "https://embed.gog.com/on_login_success"
        self.redirect_uri = "https://embed.gog.com/on_login_success?origin=client"
        self.client_id = "46899977096215655"
        self.client_secret = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
        self.debug = os.environ.get("MG_DEBUG")

    # use a method to authenticate, based on the information we have
    # Returns an empty string if no information was entered
    def authenticate(self, login_code: str = None, refresh_token: str = None) -> str:
        if refresh_token:
            return self.__refresh_token(refresh_token)
        elif login_code:
            return self.__get_token(login_code)
        else:
            return ''

    # Get a new token with the refresh token received when authenticating the last time
    def __refresh_token(self, refresh_token: str) -> str:
        request_url = "https://auth.gog.com/token"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        response = SESSION.get(request_url, params=params)

        response_params = response.json()
        self.active_token = response_params['access_token']
        expires_in = response_params["expires_in"]
        self.active_token_expiration_time = time.time() + int(expires_in)

        return response_params['refresh_token']

    # Get a token based on the code returned by the login screen
    def __get_token(self, login_code: str) -> str:
        request_url = "https://auth.gog.com/token"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': login_code,
            'redirect_uri': self.redirect_uri,
        }
        response = SESSION.get(request_url, params=params)

        response_params = response.json()
        self.active_token = response_params['access_token']
        expires_in = response_params["expires_in"]
        self.active_token_expiration_time = time.time() + int(expires_in)

        return response_params['refresh_token']

    # Get all Linux games in the library of the user. Ignore other platforms and movies
    def get_library(self):
        if not self.active_token:
            return

        games = []
        current_page = 1
        all_pages_processed = False
        url = "https://embed.gog.com/account/getFilteredProducts"
        
        tags = {}

        while not all_pages_processed:
            params = {
                'mediaType': 1,  # 1 means game
                'page': current_page,
            }
            response = self.__request(url, params=params)
            total_pages = response["totalPages"]
            
            if response["tags"]:
                for tag in response["tags"]:
                    tags[tag["id"]] = tag["name"]

            for product in response["products"]:
                try:
                    if product["id"] not in IGNORE_GAME_IDS:
                        if not product["url"]:
                            print("{} ({}) has no store page url".format(product["title"], product['id']))
                        supported_platforms = []
                        if product["worksOn"]["Linux"]:
                            supported_platforms.append("linux")
                        if product["worksOn"]["Windows"]:
                            supported_platforms.append("windows")
                        if product["worksOn"]["Mac"]:
                            supported_platforms.append("mac")
                        ptags = []
                        if product["tags"]:
                            for tag in product["tags"]:
                                ptags.append(tags[tag])
                        release_date = None
                        if "releaseDate" in product:
                            release_date = product["releaseDate"]
                        game = Game(name=product["title"], url=product["url"], game_id=product["id"])
                        game.updates=0
                        game.image_url = product["image"]
                        game.installed = 0
                        game.tags=ptags if len(ptags) > 0 else None
                        game.set_main_genre(product["category"])
                        game.supported_platforms=supported_platforms
                        game.release_date = release_date
                        games.append(game)
                except Exception as e:
                    print(e)
            if current_page == total_pages:
                all_pages_processed = True
            current_page += 1
        return games

    def get_owned_products_ids(self):
        if not self.active_token:
            return
        url2 = "https://embed.gog.com/user/data/games"
        response2 = self.__request(url2)
        return response2["owned"]

    # Generate the URL for the login page for GOG
    def get_login_url(self) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'layout': 'client2',
        }
        return "https://auth.gog.com/auth?" + urlencode(params)

    def get_redirect_url(self) -> str:
        return self.redirect_uri

    # Get Extrainfo about a game
    def get_info(self, game: Game) -> tuple:
        request_url = "https://api.gog.com/products/{}?expand=downloads,expanded_dlcs,description,screenshots,videos," \
                      "related_products,changelog ".format(str(game.id))
        game_dir = os.path.join(CACHE_DIR, "game/{}".format(game.id))
        if os.path.exists(game_dir) == False:
            os.makedirs(game_dir)
        file_path = os.path.join(game_dir,"info.json")
        do_request = True;
        if os.path.exists(file_path) == True and time.time() - os.path.getmtime(file_path) < 60 * 60 * 24:
            do_request = False
        if do_request == True:
            response = self.__request(request_url)
            with open(file_path,'w') as outfile:
                json.dump(response, outfile)
        else:
            with open(file_path,'r') as infile:
                response = json.load(infile)
        return response
    
    # Get user achievements for a given game
    def get_game_achievements(self, game: Game) -> List[Achievement]:
        request_url = "https://gameplay.gog.com/clients/" + str(game.id) + "/users/"+str(Config.get("user_id"))+"/achievements"
        game_dir = os.path.join(CACHE_DIR, "game/{}".format(game.id))
        if os.path.exists(game_dir) == False:
            os.makedirs(game_dir)
        file_path = os.path.join(game_dir,"achievements.json")
        do_request = True;
        if os.path.exists(file_path) == True and time.time() - os.path.getmtime(file_path) < 60 * 60 * 24:
            do_request = False
        if do_request == True:
            response = self.__request(request_url)
            with open(file_path,'w') as outfile:
                json.dump(response, outfile)
        else:
            with open(file_path,'r') as infile:
                response = json.load(infile)
        
        achievements = []
        for item in response["items"]:
            try:
                achievement = Achievement(game,item["achievement_id"],item["achievement_key"])
                achievement.visible = item["visible"]
                achievement.name = item["name"]
                achievement.description = item["description"]
                achievement.image_url_unlocked = item["image_url_unlocked"]
                achievement.image_url_locked = item["image_url_locked"]
                achievement.date_unlocked = item["date_unlocked"]
                achievements.append(achievement)
            except Exception as e:
                print(e)
        return achievements
    
    # Get Extrainfo about several games
    def get_infos(self, games: List[Game]) -> tuple:
        glen = len(games)
        if glen <= 50:
            return self.__get_infos(games)
        else:
            pages = math.ceil(glen / 50.0)
            page = 0
            response = []
            while page <= pages:
                start = page * 50
                end = start + 50 
                resp = self.__get_infos(games[start:end])
                for idx in resp:
                    response.append(idx)
                page += 1
            return response
    
    # Get Extrainfo about several games
    def __get_infos(self, games: List[Game]) -> tuple:
        ids = ""
        idx = 0
        glen = len(games)
        found = 0
        bypass_cache = False
        cache_validity = 60 * 60 * 24
        # compose ids and figure out if we can serve from cache
        for game in games:
            game_dir = os.path.join(CACHE_DIR, "game/{}".format(game.id))
            if os.path.exists(game_dir) == False:
                os.makedirs(game_dir)
            file_path = os.path.join(game_dir,"info.json")
            if os.path.exists(file_path) == True:
                found += 1
                if time.time() - os.path.getmtime(file_path) > cache_validity:
                    bypass_cache = True
            ids += str(game.id)
            if idx < glen - 1:
                ids += ","
            idx += 1
        request_url = "https://api.gog.com/products?ids=" + ids + "&expand=downloads,expanded_dlcs,description," \
                                                                       "screenshots,videos,related_products,changelog"
        # can we serve this from cache
        if found == glen and bypass_cache == False:
            # load from individual cached files
            response = []
            for game in games:
                game_dir = os.path.join(CACHE_DIR, "game/{}".format(game.id))
                file_path = os.path.join(game_dir,"info.json")
                with open(file_path,'r') as infile:
                    response.append(json.load(infile))
            return response
        # execute the request and store individual files
        response = self.__request(request_url)
        for g in response:
            gid = g["id"]
            game_dir = os.path.join(CACHE_DIR, "game/{}".format(gid))
            if os.path.exists(game_dir) == False:
                os.makedirs(game_dir)
            file_path = os.path.join(game_dir,"info.json")
            with open(file_path,'w') as outfile:
                json.dump(g, outfile)
        return response

    # This returns a unique download url and a link to the checksum of the download
    def get_download_info(self, game: Game, operating_system="linux", dlc=False, dlc_installers="") -> tuple:
        if dlc:
            installers = dlc_installers
        else:
            response = self.get_info(game)
            installers = response["downloads"]["installers"]
        possible_downloads = []
        for installer in installers:
            if installer["os"] == operating_system:
                possible_downloads.append(installer)
        if not possible_downloads:
            if operating_system == "linux":
                return self.get_download_info(game, "windows")
            else:
                raise NoDownloadLinkFound("Error: {} with id {} couldn't be installed".format(game.name, game.id))

        download_info = possible_downloads[0]
        for installer in possible_downloads:
            if installer['language'] == Config.get("lang"):
                download_info = installer
                break
            if installer['language'] == "en":
                download_info = installer

        # Return last entry in possible_downloads. This will either be English or the first langauge in the list
        # This is just a backup, if the preferred language has been found, this part won't execute
        return download_info

    def get_real_download_link(self, url):
        return self.__request(url)['downlink']

    def get_user_info(self,finish_fn = None) -> str:
        username = Config.get("username")
        userid = Config.get("user_id")
        avatar = None
        if userid is not None:
            user_dir = os.path.join(CACHE_DIR, "user/{}".format(userid))
            if os.path.exists(user_dir) == False:
                os.makedirs(user_dir)
            avatar = os.path.join(user_dir, "avatar_menu_user_av_small.jpg")
            if not (os.path.isfile(avatar) and os.path.exists(avatar)):
                avatar = None
            if (avatar is not None and finish_fn is not None):
                finish_fn()
        if not username or not avatar:
            url = "https://embed.gog.com/userData.json"
            response = self.__request(url)
            username = response["username"]
            userid = response["userId"]
            Config.set("user_id", userid)
            Config.set("username", username)
            user_dir = os.path.join(CACHE_DIR, "user/{}".format(userid))
            if os.path.exists(user_dir) == False:
                os.makedirs(user_dir)
            avatar = os.path.join(user_dir, "avatar_menu_user_av_small.jpg")
            download = Download(response["avatar"]+"_menu_user_av_small.jpg", avatar, finish_func=finish_fn)
            DownloadManager.download_now(download)
        return username


    def can_connect(self) -> bool:
        url = "https://embed.gog.com"
        try:
            SESSION.get(url, timeout=10)
        except Exception as ex:
            print("Could not validate that connection with GOG is possible. Cause: {}".format(ex))
            return False
        return True

    # Make a request with the active token
    def __request(self, url: str = None, params: dict = None) -> tuple:
        # Refresh the token if needed
        if self.active_token_expiration_time < time.time():
            print("Refreshing token")
            refresh_token = Config.get("refresh_token")
            Config.set("refresh_token", self.__refresh_token(refresh_token))

        # Make the request
        headers = {
            'Authorization': "Bearer " + self.active_token,
        }
        response = SESSION.get(url, headers=headers, params=params)
        if self.debug:
            print("Request: {}".format(url))
            print("Return code: {}".format(response.status_code))
            print("Response body: {}".format(response.text))
            print("")
        return response.json()
