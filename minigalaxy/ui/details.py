import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf,GLib
import os
import datetime
import webbrowser
import threading
import subprocess
from enum import Enum
from zipfile import BadZipFile
from minigalaxy.translation import _
from minigalaxy.htmlcleaner import HTMLCleaner
from minigalaxy.paths import CACHE_DIR, UI_DIR, ICON_WINDOWS_PATH, ICON_LINUX_PATH, ICON_MAC_PATH, ICON_WINDOWS_LIGHT_PATH, ICON_LINUX_LIGHT_PATH, ICON_MAC_LIGHT_PATH
from minigalaxy.api import Api
from minigalaxy.config import Config
from minigalaxy.launcher import start_game, config_game
from minigalaxy.installer import uninstall_game, install_game
from minigalaxy.css import CSS_PROVIDER
from minigalaxy.download import Download
from minigalaxy.download_manager import DownloadManager
from minigalaxy.constants import IETF_DOWNLOAD_LANGUAGES, DL_TYPES, BONUS_TYPES

@Gtk.Template.from_file(os.path.join(UI_DIR, "details.ui"))
class Details(Gtk.Viewport):
    __gtype_name__ = "Details"
    
    basebox = Gtk.Template.Child()
    background_image = Gtk.Template.Child()
    notebook = Gtk.Template.Child()
    changelog = Gtk.Template.Child()
    description_header = Gtk.Template.Child()
    description_label = Gtk.Template.Child()
    image_os_linux = Gtk.Template.Child()
    image_os_windows = Gtk.Template.Child()
    image_os_mac = Gtk.Template.Child()
    genres_header = Gtk.Template.Child()
    genres_label = Gtk.Template.Child()
    languages_header = Gtk.Template.Child()
    languages_label = Gtk.Template.Child()
    changelog = Gtk.Template.Child()
    release_date_header = Gtk.Template.Child()
    release_date_label = Gtk.Template.Child()
    installed_version_label = Gtk.Template.Child()
    button = Gtk.Template.Child()
    update_icon = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    menu_button_cancel = Gtk.Template.Child()
    menu_button_settings = Gtk.Template.Child()
    menu_button_store = Gtk.Template.Child()
    menu_button_update = Gtk.Template.Child()
    menu_button_support = Gtk.Template.Child()
    menu_button_uninstall = Gtk.Template.Child()
    menu_button_open = Gtk.Template.Child()
    screenshots_header = Gtk.Template.Child()
    screenshots_flowbox = Gtk.Template.Child()
    videos_header = Gtk.Template.Child()
    videos_flowbox = Gtk.Template.Child()
    downloads_header = Gtk.Template.Child()
    downloadstree = Gtk.Template.Child()
    goodies_header = Gtk.Template.Child()
    goodiestree = Gtk.Template.Child()
    downloads_header_box = Gtk.Template.Child()
    downloads_filter_os = Gtk.Template.Child()
    downloads_filter_lang = Gtk.Template.Child()
    ck_os_linux = Gtk.Template.Child()
    ck_os_windows = Gtk.Template.Child()
    ck_os_mac = Gtk.Template.Child()
    systembox = Gtk.Template.Child()
    languagebox = Gtk.Template.Child()
    
    state = Enum('state', 'DOWNLOADABLE INSTALLABLE UPDATABLE QUEUED DOWNLOADING INSTALLING INSTALLED NOTLAUNCHABLE UNINSTALLING UPDATING UPDATE_QUEUED UPDATE_DOWNLOADING UPDATE_INSTALLABLE')
    
    def __init__(self, parent, game, api: Api):
        Gtk.Viewport.__init__(self)
        self.parent = parent
        self.game = game
        self.api = api
        self.progress_bar = None
        self.download = None
        self.current_state = self.state.DOWNLOADABLE
        
        # Set folder for download installer
        self.download_dir = os.path.join(CACHE_DIR, "download")
        self.download_path = os.path.join(self.download_dir, self.game.name)
        
        # Set folder for update installer
        self.update_dir = os.path.join(CACHE_DIR, "update")
        self.update_path = os.path.join(self.update_dir, self.game.name)

        # Set folder if user wants to keep installer (disabled by default)
        self.keep_dir = os.path.join(Config.get("install_dir"), "installer")
        self.keep_path = os.path.join(self.keep_dir, self.game.name)

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        self.reload_state()

        # Icon if update is available
        self.update_icon.hide()
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.show()

        if not self.game.url:
            self.menu_button_store.hide()

        
        Gtk.StyleContext.add_provider(self.button.get_style_context(),
                                      CSS_PROVIDER,
                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        if ("linux" in game.supported_platforms):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_LINUX_PATH if self.__is_light_theme() else ICON_LINUX_LIGHT_PATH,20,20,True)
            self.image_os_linux.set_from_pixbuf(pixbuf)
            self.image_os_linux.show()
        if ("windows" in game.supported_platforms):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_WINDOWS_PATH if self.__is_light_theme() else ICON_WINDOWS_LIGHT_PATH,20,20,True)
            self.image_os_windows.set_from_pixbuf(pixbuf)
            self.image_os_windows.show()
        if ("mac" in game.supported_platforms):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_MAC_PATH if self.__is_light_theme() else ICON_MAC_LIGHT_PATH,20,20,True)
            self.image_os_mac.set_from_pixbuf(pixbuf)
            self.image_os_mac.show()
        
        genres = ""
        idx = 0
        glen = len(game.genres)
        for genre in game.genres:
            genres += genre
            if idx < glen - 1:
                genres += ", "
            idx += 1
        if idx > 0:
            self.genres_label.show()
            self.genres_header.show()
            self.genres_label.set_text(genres)
        
        if game.installed_version and game.installed_version is not None and game.installed_version != "":
            self.installed_version_label.show()
            self.installed_version_label.set_text(game.installed_version)
        
        languages = ""
        idx = 0
        glen = len(game.supported_languages)
        for language in game.supported_languages:
            languages += language
            if idx < glen - 1:
                languages += ", "
            idx += 1
        if idx > 0:
            self.languages_header.show()
            self.languages_label.show()
            self.languages_label.set_text(languages)
        
        if game.release_date is not None and game.release_date != "":
            dt = None
            if isinstance(game.release_date,str):
                dt = datetime.datetime.strptime(game.release_date, '%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(game.release_date,dict):
                dt = datetime.datetime.strptime(game.release_date["date"], '%Y-%m-%d %H:%M:%S.%f')
            if dt is not None:
                self.release_date_header.show()
                self.release_date_label.show()
                self.release_date_label.set_text(dt.strftime('%Y-%m-%d'))
        
        #self.title_label.set_text(game.name)
        # grab game details from api
        self.response = api.get_info(game)
        if "description" in self.response:
            self.description_header.show()
            self.description_label.show()
            self.description_label.set_property("use-markup",True)
            #self.description_lead_label.set_text(self.response["description"]["lead"])
            try:
                self.description_label.set_markup(self.__cleanup_html(self.response["description"]["full"]))
            except Exception as e:
                print(e)
                
        # changelog
        if "changelog" in self.response:
            try:
                text = self.__cleanup_html(self.response["changelog"])
                self.changelog.get_buffer().set_text(text)
            except Exception as e:
                print(e)
                
        # screenshots
        sidx = 0
        if "screenshots" in self.response:
            for screenshot in self.response["screenshots"]:
                sidx += 1
                image_id = screenshot["image_id"]
                template = screenshot["formatter_template_url"]
                image_url = template.replace("{formatter}","ggvgm").replace(".png",".jpg")
                self.__add_screenshot(image_id,image_url)
        if sidx == 0:
            self.screenshots_header.hide()
            self.screenshots_flowbox.hide()
        # videos
        vidx = 0
        if "videos" in self.response:
            for video in self.response["videos"]:
                thumbnail_url = video["thumbnail_url"]
                video_url = video["video_url"]
                self.__add_video(vidx, video_url,thumbnail_url)
                sidx += 1
        if sidx == 0:
            self.videos_header.hide()
            self.videos_flowbox.hide()
        
        # downloads
        didx=0
        gidx=0
        downloads_store = Gtk.ListStore(str,GdkPixbuf.Pixbuf,str,str,str,str)
        downloads_cols = [_("Name"),_("OS"),_("Language"),_("Type"),_("Size"),_("Version")]
        goodies_store = Gtk.ListStore(str,str,str,str,str)
        goodies_cols = [_("Name"),_("Category"),_("Type"),_("Size"),_("Count")]
        self.downloads_languages = set()
        self.downloads_os = []
        self.download_links = []
        self.goodies_links = []
        if "downloads" in self.response:
            downloads = self.response["downloads"]
            for dltype in downloads:
                is_goodies = True if dltype == "bonus_content" else False
                items = downloads[dltype]
                download_type = DL_TYPES[dltype]
                for item in items:
                    if is_goodies:
                        gidx += 1
                        links = self.__append_to_list_store_for_download(goodies_store,item,download_type,is_goodies)
                        for link in links:
                            self.goodies_links.append(link)
                    else:
                        didx += 1
                        links = self.__append_to_list_store_for_download(downloads_store,item,download_type)
                        for link in links:
                            self.download_links.append(link)
        if (didx > 0):
            self.downloads_filter = downloads_store.filter_new()
            self.downloads_filter.set_visible_func(self.__downloads_filter,data=None)
            self.downloadstree.set_model(self.downloads_filter)
            self.downloadstree.get_selection().connect("changed",self.__on_download_selected)
            self.__create_tree_columns(self.downloadstree,downloads_cols)
            for lang in self.downloads_languages:
                ck = Gtk.CheckButton(lang)
                ck.set_active(lang == IETF_DOWNLOAD_LANGUAGES[Config.get("lang")])
                ck.connect("toggled",self.downloads_filter_changed)
            self.languagebox.pack_start(ck,False,True,10)
            self.languagebox.show_all()
            self.downloads_header_box.show_all()
            self.downloadstree.show_all()
            # re-filter downloads
            self.downloads_filter.refilter()
        if (gidx > 0):
            self.goodiestree.set_model(goodies_store)
            self.goodiestree.get_selection().connect("changed",self.__on_goodie_selected)
            self.__create_tree_columns(self.goodiestree,goodies_cols,True)
            self.goodies_header.show()
            self.goodiestree.show_all()
        
        # load the background image 
        self.__load_background_image()
        
    def __get_download_platforms(self):
        platforms = []
        if self.ck_os_linux.get_active():
            platforms.append("linux")
        if self.ck_os_windows.get_active():
            platforms.append("windows")
        if self.ck_os_mac.get_active():
            platforms.append("mac")
        return platforms if len(platforms) > 0 else None
    
    def __get_download_languages(self):
        languages = []
        for child in self.languagebox.get_children():
            if child.get_active():
                languages.append(child.get_label())
        return languages if len(languages) > 0 else None
        
    def __downloads_filter(self,model,treeiter,data):
        platforms = self.__get_download_platforms()
        langs = self.__get_download_languages()
        idx = model[treeiter].path.get_indices()[0];
        if (platforms is None and langs is None):
            return True
        if (platforms is not None and self.downloads_os[idx] not in platforms):
            return False
        if (langs is not None and model[treeiter][2] not in langs):
            return False
        return True
    
    @Gtk.Template.Callback("downloads_filter_changed")
    def downloads_filter_changed(self,widget):
        self.downloads_filter.refilter()
    
    def __on_download_selected(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", self.download_links[model[treeiter].path.get_indices()[0]])
            
    def __on_goodie_selected(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", self.goodies_links[model[treeiter].path.get_indices()[0]])

    def __create_tree_columns(self,tree,columns,is_goodies=False):
        i = 0
        for column_title in columns:
            renderer = None
            column = None
            if i == 1 and is_goodies == False:
                renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(column_title, renderer, pixbuf=i)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            tree.append_column(column)
            i += 1
    
    def __append_to_list_store_for_download(self,store,item,download_type,is_goodie=False):
        download_name = item["name"];
        download_language = None
        download_version = None
        download_os = None
        bonus_type = None
        bonus_count = None
        if is_goodie:
            bonus_type = BONUS_TYPES[item["type"]]
            bonus_count = str(item["count"])
        else:
            download_language = IETF_DOWNLOAD_LANGUAGES[item["language"]]
            download_version = item["version"]
            download_os = item["os"]
            self.downloads_languages.add(IETF_DOWNLOAD_LANGUAGES[item["language"]])
        # but we actually need to list files
        links = []
        if "files" in item:
            files = item["files"]
            for file in files:
                links.append(file["downlink"])
                file_size = self.__sizeof_fmt(file["size"])
                if is_goodie:
                    store.append([download_name,bonus_type,download_type,file_size,bonus_count])
                else:
                    self.downloads_os.append(download_os)
                    os_image = self.__create_os_image(download_os)
                    store.append([download_name,os_image,download_language,download_type,file_size,download_version])
        return links
    
    def __create_os_image(self,os: str) -> GdkPixbuf.Pixbuf:
        if (os == "linux"):
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_LINUX_PATH if self.__is_light_theme() else ICON_LINUX_LIGHT_PATH,20,20,True)
        if (os == "windows"):
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_WINDOWS_PATH if self.__is_light_theme() else ICON_WINDOWS_LIGHT_PATH,20,20,True)
        if (os == "mac"):
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_MAC_PATH if self.__is_light_theme() else ICON_MAC_LIGHT_PATH,20,20,True)

    def __sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
        
    def __add_video(self,vidx,video_url,thumbnail_url):
        if self.__set_video(vidx, video_url):
            return True

        # Download the thumbnail
        img = os.path.join(self.game.cache_dir, "video_{}.jpg".format(vidx))

        download = Download(thumbnail_url, img, finish_func=self.__set_video, finish_func_args=(vidx,video_url))
        DownloadManager.download_now(download)
        return True
    
    def __set_video(self,vidx, video_url):
        img = os.path.join(self.game.cache_dir, "video_{}.jpg".format(vidx))
        if os.path.isfile(img) and os.path.exists(img):
            btn = Gtk.LinkButton(video_url)
            tile = Gtk.Image().new_from_file(img)
            tile.show()
            btn.add(tile)
            btn.show()
            self.videos_flowbox.add(btn)
            return True
        return False

    def __add_screenshot(self,image_id,image_url):
        if self.__set_screenshot(image_id):
            return True

        # Download the thumbnail
        img = os.path.join(self.game.cache_dir, "screenshot_{}_ggvgm.jpg".format(image_id))

        download = Download(image_url, img, finish_func=self.__set_screenshot, finish_func_args=image_id)
        DownloadManager.download_now(download)
        return True
    
    def __set_screenshot(self,image_id):
        img = os.path.join(self.game.cache_dir, "screenshot_{}_ggvgm.jpg".format(image_id))
        if os.path.isfile(img) and os.path.exists(img):
            tile = Gtk.Image().new_from_file(img)
            tile.show()
            self.screenshots_flowbox.add(tile)
            return True
        return False

    def __is_light_theme(self) -> bool:
        bgcolor = self.parent.get_style_context().get_background_color(Gtk.StateType.NORMAL)
        if (bgcolor.red <= 0.5 and bgcolor.green <= 0.5 and bgcolor.blue <= 0.5):
            return False
        return True 

    def __cleanup_html(self,html) -> str:
        cleaner = HTMLCleaner(html.strip().replace("\n","").replace("<br><br>","<br>"))
        return cleaner.get()
    
    def __load_background_image(self):
        if self.__set_background_image():
            return True
        if not self.game.background_url or not self.game.id:
            return False

        # Download the thumbnail
        image_url = "https:{}".format(self.game.background_url)
        img = os.path.join(self.game.cache_dir, "{}_background.jpg".format(self.game.id))

        download = Download(image_url, img, finish_func=self.__set_background_image)
        DownloadManager.download_now(download)
        return True
    
    def __set_background_image(self):
        img = os.path.join(self.game.cache_dir, "{}_background.jpg".format(self.game.id))
        if os.path.isfile(img) and os.path.exists(img):
            # minimum height 220
            width = self.basebox.get_allocation().width
            if (width < 640):
                width = 640
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img,width,-1,True)
            GLib.idle_add(self.background_image.set_from_pixbuf, pixbuf)
            return True
        return False
    
    @Gtk.Template.Callback("on_box_resize")
    def on_box_resize(self,container):
        self.__set_background_image()
        
    def __download_file(self) -> None:
        Config.set("current_download", self.game.id)
        GLib.idle_add(self.update_to_state, self.state.QUEUED)
        download_info = self.api.get_download_info(self.game)

        # Start the download for all files
        self.download = []
        download_path = self.download_path
        finish_func = self.__install
        for key, file_info in enumerate(download_info['files']):
            if key > 0:
                download_path = "{}-{}.bin".format(self.download_path, key)
            download = Download(
                url=self.api.get_real_download_link(file_info["downlink"]),
                save_location=download_path,
                finish_func=finish_func,
                progress_func=self.set_progress,
                cancel_func=self.__cancel_download,
                number=key+1,
                out_of_amount=len(download_info['files'])
            )
            self.download.append(download)

        DownloadManager.download(self.download)

    @Gtk.Template.Callback("on_button_clicked")
    def on_button_click(self, widget) -> None:
        dont_act_in_states = [self.state.QUEUED, self.state.DOWNLOADING, self.state.INSTALLING, self.state.UNINSTALLING]
        if self.current_state in dont_act_in_states:
            return
        elif self.current_state == self.state.INSTALLED or self.current_state == self.state.UPDATABLE:
            start_game(self.game, self.parent)
        elif self.current_state == self.state.INSTALLABLE:
            install_thread = threading.Thread(target=self.__install)
            install_thread.start()
        elif self.current_state == self.state.DOWNLOADABLE:
            download_thread = threading.Thread(target=self.__download_file)
            download_thread.start()

    @Gtk.Template.Callback("on_menu_button_cancel_clicked")
    def on_menu_button_cancel(self, widget):
        message_dialog = Gtk.MessageDialog(parent=self.parent.parent,
                                           flags=Gtk.DialogFlags.MODAL,
                                           message_type=Gtk.MessageType.WARNING,
                                           buttons=Gtk.ButtonsType.OK_CANCEL,
                                           message_format=_("Are you sure you want to cancel downloading {}?").format(self.game.name))
        response = message_dialog.run()

        if response == Gtk.ResponseType.OK:
            self.prevent_resume_on_startup()
            DownloadManager.cancel_download(self.download)
        message_dialog.destroy()

    @Gtk.Template.Callback("on_menu_button_settings_clicked")
    def on_menu_button_settings(self, widget):
        config_game(self.game)

    @Gtk.Template.Callback("on_menu_button_uninstall_clicked")
    def on_menu_button_uninstall(self, widget):
        message_dialog = Gtk.MessageDialog(parent=self.parent.parent,
                                           flags=Gtk.DialogFlags.MODAL,
                                           message_type=Gtk.MessageType.WARNING,
                                           buttons=Gtk.ButtonsType.OK_CANCEL,
                                           message_format=_("Are you sure you want to uninstall %s?" % self.game.name))
        response = message_dialog.run()

        if response == Gtk.ResponseType.OK:
            uninstall_thread = threading.Thread(target=self.__uninstall_game)
            uninstall_thread.start()
            message_dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            message_dialog.destroy()

    @Gtk.Template.Callback("on_menu_button_open_clicked")
    def on_menu_button_open_files(self, widget):
        subprocess.call(["xdg-open", self.__get_install_dir()])

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
        if self.current_state == self.state.UPDATE_INSTALLABLE:
            install_thread = threading.Thread(target=self.__update)
            install_thread.start()
        elif self.current_state == self.state.UPDATABLE or self.current_state == self.state.INSTALLED:
            download_thread = threading.Thread(target=self.__download_update)
            download_thread.start()

    def __install(self):
        GLib.idle_add(self.update_to_state, self.state.INSTALLING)
        self.game.install_dir = self.__get_install_dir()
        try:
            if os.path.exists(self.keep_path):
                install_game(self.game, self.keep_path, parent_window=self.parent)
            else:
                install_game(self.game, self.download_path, parent_window=self.parent)
        except (FileNotFoundError, BadZipFile):
            GLib.idle_add(self.update_to_state, self.state.DOWNLOADABLE)
            return
        GLib.idle_add(self.update_to_state, self.state.INSTALLED)

    def __cancel_download(self):
        GLib.idle_add(self.update_to_state, self.state.DOWNLOADABLE)
        GLib.idle_add(self.reload_state)

    def __download_update(self) -> None:
        Config.set("current_download", self.game.id)
        GLib.idle_add(self.update_to_state, self.state.UPDATE_QUEUED)
        download_info = self.api.get_download_info(self.game)

        # Start the download for all files
        self.download = []
        download_path = self.update_path
        finish_func = self.__update
        for key, file_info in enumerate(download_info['files']):
            if key > 0:
                download_path = "{}-{}.bin".format(self.update_path, key)
            download = Download(
                url=self.api.get_real_download_link(file_info["downlink"]),
                save_location=download_path,
                finish_func=finish_func,
                progress_func=self.set_progress,
                cancel_func=self.__cancel_update,
                number=key+1,
                out_of_amount=len(download_info['files'])
            )
            self.download.append(download)

        DownloadManager.download(self.download)
        
    def __update(self):
        GLib.idle_add(self.update_to_state, self.state.UPDATING)
        self.game.install_dir = self.__get_install_dir()
        try:
            if os.path.exists(self.keep_path):
                install_game(self.game, self.keep_path, parent_window=self.parent)
            else:
                install_game(self.game, self.update_path, parent_window=self.parent)
        except (FileNotFoundError, BadZipFile):
            GLib.idle_add(self.update_to_state, self.state.UPDATABLE)
            return
        # reset updates count flag
        self.game.updates = 0
        GLib.idle_add(self.update_to_state, self.state.INSTALLED)

    def __cancel_update(self):
        GLib.idle_add(self.update_to_state, self.state.UPDATABLE)
        GLib.idle_add(self.reload_state)

    def set_progress(self, percentage: int):
        if self.current_state == self.state.QUEUED:
            GLib.idle_add(self.update_to_state, self.state.DOWNLOADING)
        if self.current_state == self.state.UPDATE_QUEUED:
            GLib.idle_add(self.update_to_state, self.state.UPDATE_DOWNLOADING)
        if self.progress_bar:
            GLib.idle_add(self.progress_bar.set_fraction, percentage/100)

    def __uninstall_game(self):
        GLib.idle_add(self.update_to_state, self.state.UNINSTALLING)
        uninstall_game(self.game)
        GLib.idle_add(self.update_to_state, self.state.DOWNLOADABLE)
        GLib.idle_add(self.reload_state)

    def __create_progress_bar(self) -> None:
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_halign(Gtk.Align.CENTER)
        self.progress_bar.set_size_request(196, -1)
        self.progress_bar.set_hexpand(False)
        self.progress_bar.set_vexpand(False)
        self.set_center_widget(self.progress_bar)
        self.progress_bar.set_fraction(0.0)

    def __get_install_dir(self):
        if self.game.install_dir:
            return self.game.install_dir
        return os.path.join(Config.get("install_dir"), self.game.get_install_directory_name())
        
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
        if (self.current_state == self.state.INSTALLED or self.current_state == self.state.UPDATABLE):
            self.button.set_label(_("play"))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        elif (self.current_state == self.state.DOWNLOADABLE):
            self.button.set_label(_("download"))
        elif (self.current_state == self.state.DOWNLOADING or self.current_state == self.state.UPDATE_DOWNLOADING):
            self.button.set_label(_("downloading.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.state.QUEUED):
            self.button.set_label(_("in queue.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.state.UPDATE_QUEUED):
            self.menu_button_cancel.show()
        elif (self.current_state == self.state.INSTALLING):
            self.button.set_label(_("installing.."))
        elif (self.current_state == self.state.UNINSTALLING):
            self.button.set_label(_("uninstalling.."))
        elif (self.current_state == self.state.UPDATING):
            self.button.set_label(_("updating.."))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        # special cases 
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.show()
            # figure out if we should fetch or install the update
            if (self.current_state == self.state.UPDATABLE or self.current_state == self.state.INSTALLED):
                self.menu_button_update.set_label(_("Update"))
            elif (self.current_state == self.state.UPDATE_INSTALLABLE):
                self.menu_button_update.set_label(_("Install Update"))
            else:
                self.menu_button_update.set_label(_("Update"))
            self.menu_button_update.show()
        if not self.game.url:
            self.menu_button_store.hide()
        if self.game.platform == "windows":
            self.menu_button_settings.show()

    def reload_state(self):
        self.game.install_dir = self.__get_install_dir()
        dont_act_in_states = [self.state.QUEUED, self.state.DOWNLOADING, self.state.INSTALLING, self.state.UNINSTALLING, self.state.UPDATING, self.state.UPDATE_QUEUED, self.state.UPDATE_DOWNLOADING]
        if self.current_state in dont_act_in_states:
            return
        if self.game.install_dir and os.path.exists(self.game.install_dir):
            self.update_to_state(self.state.INSTALLED)
        elif os.path.exists(self.keep_path):
            self.update_to_state(self.state.INSTALLABLE)
        else:
            self.update_to_state(self.state.DOWNLOADABLE)
        self.update_options()

    def update_to_state(self, state):
        self.current_state = state
        if state == self.state.DOWNLOADABLE or state == self.state.INSTALLABLE or state == self.state.UPDATE_INSTALLABLE:
            self.button.set_sensitive(True)
            self.game.install_dir = ""
            if self.progress_bar:
                self.progress_bar.destroy()

        elif state == self.state.QUEUED or state == self.state.UPDATE_QUEUED:
            self.button.set_sensitive(False)
            self.__create_progress_bar()

        elif state == self.state.DOWNLOADING or state == self.state.UPDATE_DOWNLOADING:
            self.button.set_sensitive(False)
            if not self.progress_bar:
                self.__create_progress_bar()
            self.progress_bar.show_all()

        elif state == self.state.INSTALLING or state == self.state.UPDATING:
            self.button.set_sensitive(False)
            self.game.install_dir = self.__get_install_dir()
            if self.progress_bar:
                self.progress_bar.destroy()
            self.parent.filter_library()

        elif state == self.state.INSTALLED or state == self.state.UPDATABLE:
            # self.button.get_style_context().add_class("suggested-action")
            self.button.set_sensitive(True)
            self.game.install_dir = self.__get_install_dir()
            if self.progress_bar:
                self.progress_bar.destroy()

        elif state == self.state.UNINSTALLING:
            self.button.set_sensitive(False)
            self.game.install_dir = ""
            self.parent.filter_library()

        self.update_options()
        