
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import os
from goodoldgalaxy.translation import _
from goodoldgalaxy.paths import UI_DIR
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager
from goodoldgalaxy.game import Game


@Gtk.Template.from_file(os.path.join(UI_DIR, "installedrow.ui"))
class InstalledRow(Gtk.Box):
    __gtype_name__ = "InstalledRow"
    gogBaseUrl = "https://www.gog.com"

    image = Gtk.Template.Child()
    update_icon = Gtk.Template.Child();
    title_label = Gtk.Template.Child()
    last_played_label = Gtk.Template.Child()
    
    def __init__(self, parent, game: Game, api):
        Gtk.Frame.__init__(self)
        self.parent = parent
        self.game = game
        self.api = api
        self.progress_bar = None
        self.thumbnail_set = False
        self.title_label.set_text(self.game.name)
        self.current_state = self.game.get_state()
        # register state listeners
        self.game.register_state_listener(self.__game_state_listener)
        
        self.last_played_label.set_text(_("Not yet played"))

        self.load_icon()

        # Icon if update is available
        self.update_options()
        
    def update_progress(self, percentage: int):
        """Updates the download progress.
        
        Args:
            percentage (int): Current download percentage
        """
        if not self.progress_bar:
            # create progress bar if not existing
            self.__create_progress_bar()
        if self.progress_bar:
            GLib.idle_add(self.progress_bar.set_fraction, percentage/100)
            
    def update_download_state(self, state):
        """Updates the download state progress.
        
        Args:
            state (Enum): Current download state
        """
        if state == state.FINISHED or state == state.CANCELED or state == state.ERROR:
            # remove the progress bar
            if self.progress_bar:
                self.progress_bar.destroy() 
        
    def __game_state_listener(self, game: Game, state):
        if game != self.game:
            return
        # unregister listeners
        if state == game.state.DOWNLOADABLE:
            self.game.unregister_state_listener(self.__game_state_listener)
        self.update_to_state(state)

    def load_icon(self):
        if self.__set_image():
            return True
        if not self.game.sidebar_icon_url or not self.game.id:
            return False

        # Download the thumbnail
        image_url = "https:{}".format(self.game.sidebar_icon_url)
        icon = os.path.join(self.game.cache_dir, "{}_sbicon.png".format(self.game.id))

        download = Download(image_url, icon)
        download.register_finish_function(self.__set_image)
        DownloadManager.download_now(download)
        return True

    def __set_image(self):
        icon = os.path.join(self.game.cache_dir, "{}_sbicon.png".format(self.game.id))
        if os.path.isfile(icon) and os.path.exists(icon) and os.path.getsize(icon) > 0:
            GLib.idle_add(self.image.set_from_file, icon)
            return True
        return False

    @Gtk.Template.Callback("on_row_button_release")
    def on_row_button_release(self, widget, event):
        self.parent.show_game_details(self.game)

    def __create_progress_bar(self) -> None:
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_halign(Gtk.Align.FILL)
        self.progress_bar.set_size_request(-1, -1)
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_vexpand(False)
        self.set_center_widget(self.progress_bar)
        self.progress_bar.set_fraction(0.0)

    def update_to_state(self, state):
        self.current_state = state
        if state == self.game.state.QUEUED or state == self.game.state.UPDATE_QUEUED:
            self.image.set_sensitive(False)
            self.__create_progress_bar()
        elif state == self.game.state.DOWNLOADING or state == self.game.state.UPDATE_DOWNLOADING:
            self.image.set_sensitive(False)
            if not self.progress_bar:
                self.__create_progress_bar()
            self.progress_bar.show_all()
        else:
            self.image.set_sensitive(True)
            if self.progress_bar:
                self.progress_bar.destroy()
        self.update_options()

    def update_options(self):
        # special cases 
        self.update_icon.hide()
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.set_from_icon_name("gtk-refresh",4)
            self.update_icon.show()
        else:
            self.update_icon.hide()
               
    def reload_state(self):
        dont_act_in_states = [self.game.state.QUEUED, self.game.state.DOWNLOADING, self.game.state.INSTALLING, self.game.state.UNINSTALLING, self.game.state.UPDATING, self.game.state.UPDATE_QUEUED, self.game.state.UPDATE_DOWNLOADING]
        if self.current_state in dont_act_in_states:
            self.image.set_sensitive(True)
            return
        if self.game.install_dir and os.path.exists(self.game.install_dir):
            self.update_to_state(self.game.state.INSTALLED)
        elif os.path.exists(self.keep_path):
            self.update_to_state(self.game.state.INSTALLABLE)
        else:
            self.update_to_state(self.game.state.DOWNLOADABLE)
        self.update_options()
        
    def __str__(self):
        return self.game.name

