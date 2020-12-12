import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from goodoldgalaxy.version import VERSION
from goodoldgalaxy.translation import _
from goodoldgalaxy.paths import LOGO_IMAGE_PATH, UI_DIR


@Gtk.Template.from_file(os.path.join(UI_DIR, "about.ui"))
class About(Gtk.AboutDialog):
    __gtype_name__ = "About"

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self, title=_("About"), parent=parent, modal=True)
        self.set_version(VERSION)
        new_image = GdkPixbuf.Pixbuf().new_from_file(LOGO_IMAGE_PATH)
        self.set_logo(new_image)
