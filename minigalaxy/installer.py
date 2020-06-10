import os
import shutil
import subprocess
import stat
import gi
from xdg.DesktopEntry import DesktopEntry
from os import path
import re
import xdg
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from minigalaxy.translation import _
from minigalaxy.paths import CACHE_DIR, THUMBNAIL_DIR
from minigalaxy.config import Config
from minigalaxy.gogextract import extract_installer
from minigalaxy.game import Game

def copytree(src, dst, symlinks = False, ignore = None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.chmod(d, mode, follow_symlinks=False)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def install_freedesktop_menuitem(game: Game):
    icon = os.path.join(game.install_dir,"support/icon.png")
    play = os.path.join(game.install_dir,"start.sh")
    # create a new desktop entry
    entry_name = re.sub('[^A-Za-z0-9_]+', '', game.name.replace(" ","_"))
    entry = DesktopEntry(os.path.join("~/.local/share/applications/","gog_com-"+entry_name+".desktop"))
    entry.set("Encoding", "UTF-8")
    entry.set("Value", "1.0")
    entry.set("Type", "Application")
    entry.set("Name", game.name)
    entry.set("GenericName", game.name)
    entry.set("Comment", game.name)
    entry.set("Icon",icon)
    entry.set("Exec","\""+play+"\" \"\"")
    entry.set("Categories", "Game;")
    entry.set("Path",game.install_dir)
    
def install_freedesktop_desktopitem(game: Game):
    icon = os.path.join(game.install_dir,"support/icon.png")
    play = os.path.join(game.install_dir,"start.sh")
    # create a new desktop entry
    entry_name = re.sub('[^A-Za-z0-9_]+', '', game.name.replace(" ","_"))
    # find out desktop location
    cp = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True)
    desktop_dir=cp.stdout.decode().strip()+"/"
    
    entry = DesktopEntry(os.path.join(desktop_dir,"gog_com-"+entry_name+".desktop"))
    entry.set("Encoding", "UTF-8")
    entry.set("Value", "1.0")
    entry.set("Type", "Application")
    entry.set("Name", game.name)
    entry.set("GenericName", game.name)
    entry.set("Comment", game.name)
    entry.set("Icon",icon)
    entry.set("Exec",play)
    entry.set("Categories", "Game;")
    entry.set("Path",game.install_dir)
    

def create_shortcuts(game: Game):
    if game.platform != "linux":
        return
    install_freedesktop_menuitem(game)
    install_freedesktop_desktopitem(game)

def install_game(game, installer, parent_window=None, main_window=None) -> None:
    if not os.path.exists(installer):
        GLib.idle_add(__show_installation_error, game, _("{} failed to download.").format(installer), parent_window, main_window)
        raise FileNotFoundError("The installer {} does not exist".format(installer))

    if game.platform == "linux":
        if not __verify_installer_integrity(installer):
            GLib.idle_add(__show_installation_error, game, _("{} was corrupted. Please download it again.").format(installer), parent_window, main_window)
            os.remove(installer)
            raise FileNotFoundError("The installer {} was corrupted".format(installer))
        
        # Make sure the install directory exists
        library_dir = Config.get("install_dir")
        if not os.path.exists(library_dir):
            os.makedirs(library_dir)

        # Make a temporary empty directory for extracting the installer
        temp_dir = os.path.join(CACHE_DIR, "extract/{}".format(game.id))
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir)
        
        subprocess.call(["unzip", "-qq", installer, "-d", temp_dir])
        if len(os.listdir(temp_dir)) == 0:
            GLib.idle_add(__show_installation_error, game, _("{} could not be unzipped.").format(installer), parent_window, main_window)
            raise CannotOpenZipContent(_("{} could not be unzipped.").format(installer))
        

        # Copy the game files into the correct directory
        tmp_noarch_dir=os.path.join(temp_dir, "data/noarch")
        copytree(tmp_noarch_dir, game.install_dir)
        
        if Config.get("create_shortcuts") == True:
            create_shortcuts(game)

        # Remove the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

    elif game.platform == "windows":
        # Set the prefix for Windows games
        prefix_dir = os.path.join(game.install_dir, "prefix")
        if not os.path.exists(prefix_dir):
            os.makedirs(prefix_dir)

        os.environ["WINEPREFIX"] = prefix_dir

        # It's possible to set install dir as argument before installation
        command = ["wine", installer, "/dir=" + game.install_dir]
        subprocess.run(command)
    else:
        GLib.idle_add(__show_installation_error, game, _("{} platform not supported.").format(installer), parent_window, main_window)
        raise Exception("Platform not supported")

    thumbnail_small = os.path.join(THUMBNAIL_DIR, "{}_100.jpg".format(game.id))
    thumbnail_medium = os.path.join(THUMBNAIL_DIR, "{}_196.jpg".format(game.id))
    if os.path.exists(thumbnail_small):
        shutil.copyfile(thumbnail_small,os.path.join(game.install_dir, "thumbnail_100.jpg"))
    if os.path.exists(thumbnail_medium):
        shutil.copyfile(thumbnail_medium,os.path.join(game.install_dir, "thumbnail_196.jpg"))

    if Config.get("keep_installers"):
        keep_dir = os.path.join(Config.get("install_dir"), "installer")
        download_dir = os.path.join(CACHE_DIR, "download")
        update_dir = os.path.join(CACHE_DIR, "update")
        if not os.path.exists(keep_dir):
            os.makedirs(keep_dir)
        try:
            # It's needed for multiple files
            for file in os.listdir(download_dir):
                shutil.move(download_dir + '/' + file, keep_dir + '/' + file)
        except Exception as ex:
            print("Encountered error while copying {} to {}. Got error: {}".format(installer, keep_dir, ex))
        try:
            # It's needed for multiple files
            for file in os.listdir(update_dir):
                shutil.move(update_dir + '/' + file, keep_dir + '/' + file)
        except Exception as ex:
            print("Encountered error while copying {} to {}. Got error: {}".format(installer, keep_dir, ex))
    else:
        os.remove(installer)


def __show_installation_error(game, message, parent_window=None, main_window = None):
    error_message = [_("Failed to install {}").format(game.name), message]
    print("{}: {}".format(error_message[0], error_message[1]))
    parent = main_window if main_window is not None else parent_window.parent
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        parent=parent,
        modal=True,
        buttons=Gtk.ButtonsType.CLOSE,
        text=error_message[0]
    )
    dialog.format_secondary_text(error_message[1])
    dialog.run()
    dialog.destroy()


class CannotOpenZipContent(Exception):
    pass


def __verify_installer_integrity(installer):
    try:
        print("Executing integrity check for {}".format(installer))
        os.chmod(installer, 0o744)
        result = subprocess.run([installer, "--check"])
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as ex:
        # Any exception means the archive doesn't work, so we don't care with the error is
        print("Error, exception encountered: {}".format(ex))
        return False


def uninstall_game(game):
    shutil.rmtree(game.install_dir, ignore_errors=True)
