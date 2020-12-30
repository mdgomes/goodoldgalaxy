import shutil
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import os
import webbrowser
import subprocess
from goodoldgalaxy.translation import _
from goodoldgalaxy.paths import THUMBNAIL_DIR, UI_DIR
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager
from goodoldgalaxy.launcher import start_game, config_game

from goodoldgalaxy.css import CSS_PROVIDER


@Gtk.Template.from_file(os.path.join(UI_DIR, "gamerow.ui"))
class GameRow(Gtk.Box):
    __gtype_name__ = "GameRow"
    gogBaseUrl = "https://www.gog.com"

    image = Gtk.Template.Child()
    update_icon = Gtk.Template.Child();
    title_label = Gtk.Template.Child()
    genre_label = Gtk.Template.Child()
    button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child();
    menu_button_details = Gtk.Template.Child()
    menu_button_settings = Gtk.Template.Child()
    menu_button_store = Gtk.Template.Child()
    menu_button_update = Gtk.Template.Child()
    menu_button_support = Gtk.Template.Child()
    menu_button_uninstall = Gtk.Template.Child()
    menu_button_open = Gtk.Template.Child()
    menu_button_cancel = Gtk.Template.Child()

    def __init__(self, parent, game, api):
        Gtk.Frame.__init__(self)
        Gtk.StyleContext.add_provider(self.menu_button.get_style_context(),
                                      CSS_PROVIDER,
                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        Gtk.StyleContext.add_provider(self.title_label.get_style_context(),
                                      CSS_PROVIDER,
                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.parent = parent
        self.game = game
        self.api = api
        self.progress_bar = None
        self.thumbnail_set = False
        self.download = None
        self.current_state = game.__state
        self.title_label.set_text(self.game.name)

        self.image.set_tooltip_text(self.game.name)
        
        if self.game.genre is not None:
            self.genre_label.set_label(self.game.genre)
        else:
            self.genre_label.hide()

        self.reload_state()
        self.load_thumbnail()

        # Icon if update is available
        self.update_icon.hide()
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.show()
        

    def __str__(self):
        return self.game.name
    
    @Gtk.Template.Callback("on_menu_button_details_clicked")
    def on_menu_button_details_clicked(self, widget) -> None:
        self.parent.parent.show_game_details(self.game)

    @Gtk.Template.Callback("on_button_clicked")
    def on_button_click(self, widget) -> None:
        dont_act_in_states = [self.game.__state.QUEUED, self.game.__state.DOWNLOADING, self.game.__state.INSTALLING, self.game.__state.UNINSTALLING, self.game.__state.UPDATING]
        if self.current_state in dont_act_in_states:
            return
        elif self.current_state == self.game.__state.INSTALLED or self.current_state == self.game.__state.UPDATABLE:
            start_game(self.game, self.parent)
        elif self.current_state == self.game.__state.INSTALLABLE:
            self.parent.parent.install_game(self.game)
        elif self.current_state == self.game.__state.DOWNLOADABLE:
            self.parent.parent.download_game(self.game)

    def set_progress(self, percentage: int):
        if self.current_state == self.game.__state.QUEUED:
            GLib.idle_add(self.update_to_state, self.game.__state.DOWNLOADING)
        if self.current_state == self.game.__state.UPDATE_QUEUED:
            GLib.idle_add(self.update_to_state, self.game.__state.UPDATE_DOWNLOADING)
        if self.progress_bar:
            GLib.idle_add(self.progress_bar.set_fraction, percentage/100)

    def __create_progress_bar(self) -> None:
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_halign(Gtk.Align.CENTER)
        self.progress_bar.set_size_request(self.get_allocated_width(), -1)
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_vexpand(False)
        self.set_center_widget(self.progress_bar)
        self.progress_bar.set_fraction(0.0)

    @Gtk.Template.Callback("on_menu_button_cancel_clicked")
    def on_menu_button_cancel(self, widget):
        self.parent.parent.cancel_download(self.game)

    @Gtk.Template.Callback("on_menu_button_settings_clicked")
    def on_menu_button_settings(self, widget):
        config_game(self.game)

    @Gtk.Template.Callback("on_menu_button_uninstall_clicked")
    def on_menu_button_uninstall(self, widget):
        self.parent.parent.uninstall_game(self.game)

    @Gtk.Template.Callback("on_menu_button_open_clicked")
    def on_menu_button_open_files(self, widget):
        subprocess.call(["xdg-open", self.game.get_install_dir()])

    @Gtk.Template.Callback("on_menu_button_support_clicked")
    def on_menu_button_support(self, widget):
        try:
            webbrowser.open(self.api.get_info(self.game)['links']['support'], new=2)
        except:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                parent=self.parent.parent,
                modal=True,
                buttons=Gtk.ButtonsType.OK,
                text=_("Couldn't open support page")
            )
            dialog.format_secondary_text(_("Please check your internet connection"))
            dialog.run()
            dialog.destroy()

    @Gtk.Template.Callback("on_menu_button_store_clicked")
    def on_menu_button_store(self, widget):
        webbrowser.open(self.gogBaseUrl + self.game.url)
        
    @Gtk.Template.Callback("on_menu_button_update_clicked")
    def on_menu_button_update(self, widget):
        if self.current_state == self.game.__state.UPDATE_INSTALLABLE:
            self.parent.parent.update(self.game)
        elif self.current_state == self.game.__state.UPDATABLE or self.current_state == self.game.__state.INSTALLED:
            self.parent.parent.download_update(self.game)

    def load_thumbnail(self):
        if self.__set_image():
            return True
        if not self.game.image_url or not self.game.id:
            return False

        # Download the thumbnail
        image_url = "https:{}_100.jpg".format(self.game.image_url)
        thumbnail = os.path.join(THUMBNAIL_DIR, "{}_100.jpg".format(self.game.id))

        download = Download(image_url, thumbnail)
        download.register_finish_function(self.__set_image)
        DownloadManager.download_now(download)
        return True

    def __set_image(self):
        thumbnail_install_dir = os.path.join(self.game.get_install_dir(), "thumbnail_100.jpg")
        thumbnail_cache_dir = os.path.join(THUMBNAIL_DIR, "{}_100.jpg".format(self.game.id))
        if os.path.isfile(thumbnail_install_dir):
            GLib.idle_add(self.image.set_from_file, thumbnail_install_dir)
            return True
        elif os.path.isfile(thumbnail_cache_dir):
            GLib.idle_add(self.image.set_from_file, thumbnail_cache_dir)
            # Copy image to
            if os.path.isdir(os.path.dirname(thumbnail_install_dir)):
                shutil.copy2(thumbnail_cache_dir, thumbnail_install_dir)
            return True
        return False

    def update_options(self):
        # hide all menu buttons
        self.menu_button_update.hide()
        self.menu_button_store.show()
        self.menu_button_support.show();
        self.menu_button_settings.hide()
        self.menu_button_open.hide()
        self.menu_button_uninstall.hide()
        self.menu_button_cancel.hide()
        self.update_icon.hide()
        # configure button label and available options
        if (self.current_state == self.game.__state.INSTALLED or self.current_state == self.game.__state.UPDATABLE):
            self.button.set_label(_("play"))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        elif (self.current_state == self.game.__state.DOWNLOADABLE):
            self.button.set_label(_("download"))
        elif (self.current_state == self.game.__state.DOWNLOADING or self.current_state == self.game.__state.UPDATE_DOWNLOADING):
            self.button.set_label(_("downloading.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.__state.QUEUED):
            self.button.set_label(_("in queue.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.__state.UPDATE_QUEUED):
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.__state.INSTALLING):
            self.button.set_label(_("installing.."))
        elif (self.current_state == self.game.__state.UNINSTALLING):
            self.button.set_label(_("uninstalling.."))
        elif (self.current_state == self.game.__state.UPDATING):
            self.button.set_label(_("updating.."))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        # special cases 
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.show()
            # figure out if we should fetch or install the update
            if (self.current_state == self.game.__state.UPDATABLE or self.current_state == self.game.__state.INSTALLED):
                self.menu_button_update.set_label(_("Update"))
            elif (self.current_state == self.game.__state.UPDATE_INSTALLABLE):
                self.menu_button_update.set_label(_("Install Update"))
            else:
                self.menu_button_update.set_label(_("Update"))
            self.menu_button_update.show()
        if not self.game.url:
            self.menu_button_store.hide()
        if self.game.platform == "windows":
            self.menu_button_settings.show()

    def reload_state(self):
        dont_act_in_states = [self.game.__state.QUEUED, self.game.__state.DOWNLOADING, self.game.__state.INSTALLING, self.game.__state.UNINSTALLING, self.game.__state.UPDATING, self.game.__state.UPDATE_QUEUED, self.game.__state.UPDATE_DOWNLOADING]
        if self.current_state in dont_act_in_states:
            return
        if self.game.install_dir and os.path.exists(self.game.install_dir):
            self.update_to_state(self.game.__state.INSTALLED)
        elif os.path.exists(self.game.keep_path):
            self.update_to_state(self.game.__state.INSTALLABLE)
        else:
            self.update_to_state(self.game.__state.DOWNLOADABLE)
        self.update_options()

    def update_to_state(self, state):
        self.current_state = state
        if state == self.game.__state.DOWNLOADABLE or state == self.game.__state.INSTALLABLE or state == self.game.__state.UPDATE_INSTALLABLE:
            self.button.set_sensitive(True)
            self.image.set_sensitive(False)

            if self.progress_bar:
                self.progress_bar.destroy()

        elif state == self.game.__state.QUEUED or state == self.game.__state.UPDATE_QUEUED:
            self.button.set_sensitive(False)
            self.image.set_sensitive(False)
            self.__create_progress_bar()

        elif state == self.game.__state.DOWNLOADING or state == self.game.__state.UPDATE_DOWNLOADING:
            self.button.set_sensitive(False)
            self.image.set_sensitive(False)
            if not self.progress_bar:
                self.__create_progress_bar()
            self.progress_bar.show_all()

        elif state == self.game.__state.INSTALLING or state == self.game.__state.UPDATING:
            self.button.set_sensitive(False)
            self.image.set_sensitive(True)

            if self.progress_bar:
                self.progress_bar.destroy()

            self.parent.filter_library()

        elif state == self.game.__state.INSTALLED or state == self.game.__state.UPDATABLE:
            # self.button.get_style_context().add_class("suggested-action")
            self.button.set_sensitive(True)
            self.image.set_sensitive(True)

            if self.progress_bar:
                self.progress_bar.destroy()

        elif state == self.game.__state.UNINSTALLING:
            self.button.set_sensitive(False)
            self.image.set_sensitive(False)

            self.parent.filter_library()

        self.update_options()
