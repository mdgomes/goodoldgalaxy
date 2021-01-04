import os
import platform
import gi
import threading
from typing import List
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from goodoldgalaxy.paths import UI_DIR
from goodoldgalaxy.api import Api
from goodoldgalaxy.game import Game
from goodoldgalaxy.config import Config
from goodoldgalaxy.library import Library
from goodoldgalaxy.ui.gamerow import GameRow
from goodoldgalaxy.ui.gametile import GameTile
from goodoldgalaxy.translation import _

@Gtk.Template.from_file(os.path.join(UI_DIR, "library.ui"))
class Library(Gtk.Viewport):
    __gtype_name__ = "Library"

    library_search = Gtk.Template.Child()
    library_mode_button = Gtk.Template.Child()
    menu_genre = Gtk.Template.Child()
    menu_system = Gtk.Template.Child()
    menu_tags = Gtk.Template.Child()
    menu_state = Gtk.Template.Child()
    library_window = Gtk.Template.Child()
    library_viewport = Gtk.Template.Child()
    image_view_as_list = Gtk.Template.Child()
    image_view_as_grid = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    flowbox = Gtk.Template.Child()
    genrebox = Gtk.Template.Child()
    tagsbox = Gtk.Template.Child()
    systembox = Gtk.Template.Child()
    ck_os_linux = Gtk.Template.Child()
    ck_os_windows = Gtk.Template.Child()
    ck_os_mac = Gtk.Template.Child()
    statesbox = Gtk.Template.Child()
    ck_state_installed = Gtk.Template.Child()
    ck_state_updated = Gtk.Template.Child()
    ck_state_hidden = Gtk.Template.Child()

    def __init__(self, parent, library: Library, api: Api):
        Gtk.Viewport.__init__(self)
        self.parent = parent
        self.api = api
        self.library = library
        self.library_mode = "list"
        self.show_installed_only = None
        
        # Set library view mode
        if (Config.get("viewas") == "list"):
            self.library_mode = "list"
            self.library_mode_button.set_image(self.image_view_as_grid)
            self.library_mode_button.set_tooltip_text(_("View as Grid"))
            self.library_viewport.add(self.listbox)
        else:
            self.library_mode = "grid"
            self.library_mode_button.set_image(self.image_view_as_list)
            self.library_mode_button.set_tooltip_text(_("View as List"))
            self.library_viewport.add(self.flowbox)
        # load library in background
        current_os = platform.system()
        if current_os == "Linux":
            self.ck_os_linux.set_active(True)
        elif current_os == "Windows":
            self.ck_os_windows.set_active(True)
        elif current_os == "Darwin":
            self.ck_os_mac.set_active(True)

    @Gtk.Template.Callback("on_library_mode_button_clicked")
    def change_view_mode(self, button):
        iconname = self.library_mode_button.get_image().get_icon_name().icon_name
        if (iconname == "view-list-symbolic"):
            Config.set("viewas","list")
            self.library_mode = "list"
            self.library_mode_button.set_image(self.image_view_as_grid)
            self.library_mode_button.set_tooltip_text(_("View as Grid"))
            self.view_as_list()
        else:
            Config.set("viewas","grid")
            self.library_mode = "grid"
            self.library_mode_button.set_image(self.image_view_as_list)
            self.library_mode_button.set_tooltip_text(_("View as List"))
            self.view_as_grid()
        self.sync_library()

    @Gtk.Template.Callback("on_library_changed")
    def library_changed(self, widget):
        if self.library_mode == "list":
            self.listbox.invalidate_filter()
        else:
            self.flowbox.invalidate_filter()

    def sync_library(self, _=""):
        if self.library.offline:
            self.parent.__authenticate()
        self.update_library()

    def reset(self):
        # remove all children from the viewport
        for child in self.library_viewport.get_children():
            self.library_viewport.remove(child)
            
    def __sort_library_func(self, child1, child2):
        tile1 = child1.get_children()[0].game
        tile2 = child2.get_children()[0].game
        return tile2 < tile1

    def get_filtered_games(self) -> List[Game]:
        # filters
        installed = True if self.library.offline else self.show_installed_only
        platforms = self.__get_selected_platforms()
        genres = self.__get_selected_genres()
        tags = self.__get_selected_tags()
        name = self.library_search.get_text().strip()
        states = self.__get_selected_states()
        # fetch from library
        return self.library.get_filtered_games(installed, platforms, genres, tags, states, name)
        
    def __update_popovers(self):
        # handle genres
        cats = self.library.genres
        tags = self.library.tags
        for child in self.genrebox.get_children():
            self.genrebox.remove(child)
        for child in self.tagsbox.get_children():
            self.tagsbox.remove(child)
        for cat in cats:
            ck = Gtk.CheckButton(cat)
            ck.connect("toggled",self.library_changed)
            self.genrebox.pack_start(ck,False,True,10)
        for tag in tags:
            ck = Gtk.CheckButton(tag)
            ck.connect("toggled",self.library_changed)
            self.tagsbox.pack_start(ck,False,True,10)
        self.genrebox.show_all()
        self.tagsbox.show_all()
        
    def find_grid_tile_for_game(self, game: Game) -> GameTile:
        """Finds the grid tile for a given game.
        
        Args:
            game (Game): Game for which we want the tile
        Returns:
            tile: Returns a GameTile or None if not found
        """
        if game is None or self.flowbox is None:
            return None
        
        for child in self.flowbox.get_children():
            if child.get_children()[0].game == game:
                return child.get_children()[0]
        
        return None

    def find_list_tile_for_game(self, game: Game) -> GameRow:
        """Finds the list tile for a given game.
        
        Args:
            game (Game): Game for which we want the tile
        Returns:
            tile (GameRow): Returns a GameRow or None if not found
        """
        if game is None:
            return None
        
        for child in self.listbox.get_children():
            if child.get_children()[0].game == game:
                return child.get_children()[0]
        
        return None

    def view_as_list(self):
        self.reset()
        # add it to the viewport
        self.library_viewport.add(self.listbox)
        # create list rows
        GLib.idle_add(self.__create_gamerow)
            
    def __create_gamerow(self) -> None:
        # remove any existing children from the listbox
        for child in self.listbox.get_children():
            self.listbox.remove(child)
        # get filtered games
        filtered_games = self.library.get_games()
        self.__update_popovers()
        # create rows
        for game in filtered_games:
            self.__add_gamerow(game)
            
        self.sort_library()
        self.listbox.show_all()

    def __add_gamerow(self, game):
        list_tile = GameRow(self, game, self.api)
        self.listbox.add(list_tile)
        
    def view_as_grid(self):
        self.reset()
        # add it to the viewport
        self.library_viewport.add(self.flowbox)
        # create list rows
        GLib.idle_add(self.__create_gametile)

    def __create_gametile(self) -> None:
        # remove any existing children from the listbox
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)
        # get filtered games
        filtered_games = self.library.get_games()
        self.__update_popovers()
        # create rows
        for game in filtered_games:
            self.__add_gametile(game)
        
        self.sort_library()
        self.flowbox.show_all()

    def __add_gametile(self, game):
        grid_tile = GameTile(self, game, self.api)
        self.flowbox.add(grid_tile)

    def update_library(self) -> None:
        library_update_thread = threading.Thread(target=self.__update_library)
        library_update_thread.daemon = True
        library_update_thread.start()

    def __update_library(self):
        GLib.idle_add(self.__load_game_states)
        # Get games from library
        if self.library_mode == "list":
            GLib.idle_add(self.__create_gamerow)
        else:
            GLib.idle_add(self.__create_gametile)
        GLib.idle_add(self.filter_library)

    def __load_game_states(self):
        if self.library_mode == "list":
            for child in self.listbox.get_children():
                row = child.get_children()[0]
                row.reload_state()
        else:
            for child in self.flowbox.get_children():
                tile = child.get_children()[0]
                tile.reload_state()

    def filter_library(self, widget: Gtk.Widget = None):
        self.__load_game_states()
        if self.library_mode == "list":
            self.listbox.set_filter_func(self.__filter_library_func)
        else:
            self.flowbox.set_filter_func(self.__filter_library_func)
    
    def __get_selected_platforms(self) -> List[str]:
        platforms = []
        if self.ck_os_linux.get_active():
            platforms.append("linux")
        if self.ck_os_windows.get_active():
            platforms.append("windows")
        if self.ck_os_mac.get_active():
            platforms.append("mac")
        return platforms if len(platforms) > 0 else None
    
    def __get_selected_genres(self) -> List[str]:
        genres = []
        for child in self.genrebox.get_children():
            if child.get_active():
                genres.append(child.get_label())
        return genres if len(genres) > 0 else None
    
    def __get_selected_tags(self) -> List[str]:
        tags = []
        for child in self.tagsbox.get_children():
            if child.get_active():
                tags.append(child.get_label())
        return tags if len(tags) > 0 else None
    
    def __get_selected_states(self) -> List[str]:
        states = []
        if self.ck_state_installed.get_active():
            states.append("installed")
        if self.ck_state_updated.get_active():
            states.append("updated")
        if self.ck_state_hidden.get_active():
            states.append("hidden")
        return states if len(states) > 0 else None

    def __filter_library_func(self, child):
        tile = child.get_children()[0]
        # filters
        installed=True if self.library.offline else self.show_installed_only
        platforms = self.__get_selected_platforms()
        genres = self.__get_selected_genres()
        tags = self.__get_selected_tags()
        states = self.__get_selected_states()
        name = self.library_search.get_text().strip()
        return self.library.is_game_filtered(tile.game, installed=installed, platform=platforms, genre=genres, tag=tags, state=states, name=name)

    def sort_library(self):
        if self.library_mode == "list":
            self.listbox.set_sort_func(self.__sort_library_func)
        elif self.library_mode == "grid":
            self.flowbox.set_sort_func(self.__sort_library_func)

    def __show_error(self, text, subtext):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            parent=self.parent,
            modal=True,
            buttons=Gtk.ButtonsType.CLOSE,
            text=text
        )
        dialog.format_secondary_text(subtext)
        dialog.run()
        dialog.destroy()
