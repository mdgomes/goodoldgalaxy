
import gi
from goodoldgalaxy.game import Game
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import os
from goodoldgalaxy.translation import _
from goodoldgalaxy.paths import UI_DIR
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager


@Gtk.Template.from_file(os.path.join(UI_DIR, "downloadrow.ui"))
class DownloadRow(Gtk.Box):
    __gtype_name__ = "DownloadRow"
    gogBaseUrl = "https://www.gog.com"

    image = Gtk.Template.Child()
    title_label = Gtk.Template.Child()
    details_label = Gtk.Template.Child()
    download_action = Gtk.Template.Child()
    download_action_image = Gtk.Template.Child()
    progress_bar = Gtk.Template.Child()
    
    
    def __init__(self, parent, download:Download, api):
        Gtk.Frame.__init__(self)
        self.parent = parent
        self.download = download
        self.api = api
        self.thumbnail_set = False
        self.image.set_sensitive(True)
        self.title_label.set_text(self.download.title)
        self.__game = None
        if download.get_progress() >= 0:
            self.details_label.set_text("{} / {} ({}%)".format(self.__sizeof_fmt(download.get_downloaded()),self.__sizeof_fmt(download.file_size),download.get_progress()))
        elif download.file_size > 0:
            self.details_label.set_text("{} / {}".format(self.__sizeof_fmt(download.get_downloaded()),self.__sizeof_fmt(download.file_size)))
        self.load_icon()
        
        # set button icon
        self.set_state(download.state())
        # register functions to track download
        download.register_progress_function(self.set_progress)
        download.register_state_function(self.set_state)

    def __str__(self):
        return self.download.url

    def load_icon(self):
        if self.download.associated_object is None or type(self.download.associated_object) is not Game:
            return
        self.__game = self.download.associated_object
        if self.__set_image():
            return True
        if not self.__game.sidebar_icon_url or not self.__game.id:
            return False

        # Download the thumbnail
        image_url = "https:{}".format(self.__game.sidebar_icon_url)
        icon = os.path.join(self.__game.cache_dir, "{}_sbicon.png".format(self.__game.id))

        download = Download(image_url, icon)
        download.register_finish_function(self.__set_image)
        DownloadManager.download_now(download)
        return True

    def __set_image(self):
        icon = os.path.join(self.__game.cache_dir, "{}_sbicon.png".format(self.__game.id))
        if os.path.isfile(icon) and os.path.exists(icon) and os.path.getsize(icon) > 0:
            GLib.idle_add(self.image.set_from_file, icon)
            return True
        return False
    
    @Gtk.Template.Callback("on_donwload_action_clicked")
    def on_donwload_action_clicked(self, widget):
        # get the current download state
        state = self.download.state()
        if state == state.DOWNLOADING:
            self.download.pause()
        elif state == state.QUEUED:
            # nothing can be done in this state
            return
        elif state == state.PAUSED:
            self.download.resume()
        elif state == state.FINISHED or state == state.ERROR:
            DownloadManager.clear_download(self.download)
            for child in self.parent.get_children():
                if child.get_children()[0] == self:
                    self.parent.remove(child)
                    self.destroy()
                    return;
    
    def set_state(self, state):
        if state == state.DOWNLOADING:
            self.download_action_image.set_from_icon_name("media-playback-pause",4)
            self.download_action_image.set_tooltip_text(_("Pause"))
        elif state == state.QUEUED:
            self.download_action_image.set_from_icon_name("image-loading",4)
            self.download_action_image.set_tooltip_text(_("Queued"))
        elif state == state.PAUSED:
            self.download_action_image.set_from_icon_name("media-playback-start",4)
            self.download_action_image.set_tooltip_text(_("Resume"))
        else:
            self.download_action_image.set_from_icon_name("dialog-cancel",4)
            self.download_action_image.set_tooltip_text(_("Remove"))
    
    def set_progress(self, percentage: int):
        if not self.progress_bar:
            # create progress bar if not existing
            self.__create_progress_bar()
        if self.progress_bar:
            GLib.idle_add(self.progress_bar.set_fraction, percentage/100)
        GLib.idle_add(self.details_label.set_text,"{} / {} ({}%)".format(self.__sizeof_fmt(self.download.get_downloaded()),self.__sizeof_fmt(self.download.file_size),percentage))

    def __sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def __create_progress_bar(self) -> None:
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_halign(Gtk.Align.CENTER)
        self.progress_bar.set_size_request(self.get_allocated_width(), -1)
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_vexpand(False)
        self.set_center_widget(self.progress_bar)
        self.progress_bar.set_fraction(0.0)
