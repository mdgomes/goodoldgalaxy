
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import os
from goodoldgalaxy.paths import UI_DIR
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager
from goodoldgalaxy.achievement import Achievement

@Gtk.Template.from_file(os.path.join(UI_DIR, "achievementrow.ui"))
class AchievementRow(Gtk.Box):
    __gtype_name__ = "AchievementRow"
    gogBaseUrl = "https://www.gog.com"

    image = Gtk.Template.Child()
    title_label = Gtk.Template.Child()
    description_label = Gtk.Template.Child()
    
    def __init__(self, parent, achievement: Achievement):
        Gtk.Frame.__init__(self)
        self.parent = parent
        self.achievement = achievement
        self.game = achievement.game
        self.thumbnail_set = False
        self.title_label.set_text(self.achievement.name)
        self.description_label.set_text(self.achievement.description)
        
        if achievement.date_unlocked is None:
            self.image.set_sensitive(False)

        self.load_icon()

    def __str__(self):
        return self.achievement.name

    def load_icon(self):
        if self.__set_image():
            return True
        if not self.achievement.image_url_unlocked or not self.achievement.achievement_id:
            return False

        # Download the thumbnail
        image_url = self.achievement.image_url_unlocked if self.achievement.date_unlocked is not None else self.achievement.image_url_locked
        icon = os.path.join(self.game.cache_dir, "achievement_{}_{}.jpg".format(self.achievement.achievement_id,"unlocked" if self.achievement.date_unlocked is not None else "locked"))

        download = Download(image_url, icon)
        download.register_finish_function(self.__set_image)
        DownloadManager.download_now(download)
        return True

    def __set_image(self):
        icon = os.path.join(self.game.cache_dir, "achievement_{}_{}.jpg".format(self.achievement.achievement_id,"unlocked" if self.achievement.date_unlocked is not None else "locked"))
        if os.path.isfile(icon) and os.path.exists(icon):
            GLib.idle_add(self.image.set_from_file, icon)
            return True
        return False
