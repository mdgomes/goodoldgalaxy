'''
Created on 11/06/2020

@author: fahrenheit
'''
import os
from minigalaxy.game import Game
from minigalaxy.paths import CACHE_DIR

class Achievement:
    
    def __init__(self, game: Game, achievement_id: str, achievement_key: str):
        self.game = game
        self.achievement_id = achievement_id
        self.achievement_key = achievement_key
        self.visible = False
        self.name = None
        self.description = None
        self.image_url_unlocked = None
        self.image_url_locked = None
        self.locked_image = None
        self.unlocked_image = None
        self.date_unlocked = None
        # cache dir
        self.cache_dir: str = os.path.join(CACHE_DIR, "game/{}".format(game.id))
        if os.path.exists(self.cache_dir) == False:
            os.makedirs(self.cache_dir)
    