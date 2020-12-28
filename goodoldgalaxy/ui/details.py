import gi
from goodoldgalaxy import achievement
from mesonbuild.msubprojects import download
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf,GLib, Gdk
import os
import datetime
import webbrowser
import threading
import subprocess
from goodoldgalaxy.translation import _
from goodoldgalaxy.htmlcleaner import HTMLCleaner
from goodoldgalaxy.paths import CACHE_DIR, UI_DIR, ICON_WINDOWS_PATH, ICON_LINUX_PATH, ICON_MAC_PATH, ICON_WINDOWS_LIGHT_PATH, ICON_LINUX_LIGHT_PATH, ICON_MAC_LIGHT_PATH
from goodoldgalaxy.api import Api
from goodoldgalaxy.config import Config
from goodoldgalaxy.launcher import start_game, config_game
from goodoldgalaxy.css import CSS_PROVIDER
from goodoldgalaxy.download import Download
from goodoldgalaxy.download_manager import DownloadManager
from goodoldgalaxy.constants import IETF_DOWNLOAD_LANGUAGES, DL_TYPES, BONUS_TYPES, DOWNLOAD_LANGUAGES_TO_GOG_CODE
from goodoldgalaxy.ui.achievementrow import AchievementRow
from goodoldgalaxy.installer import install_game
from zipfile import BadZipFile

@Gtk.Template.from_file(os.path.join(UI_DIR, "details.ui"))
class Details(Gtk.Viewport):
    __gtype_name__ = "Details"
    gogBaseUrl = "https://www.gog.com"
    
    basebox = Gtk.Template.Child()
    background_viewport = Gtk.Template.Child()
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
    media_bar = Gtk.Template.Child()
    media_flowbox = Gtk.Template.Child()
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
    achievements_box = Gtk.Template.Child()
    achievements_tab_header = Gtk.Template.Child()
    downloads_menu = Gtk.Template.Child()
    menu_button_install_content = Gtk.Template.Child()
    menu_button_uninstall_content = Gtk.Template.Child()
    menu_button_update_content = Gtk.Template.Child()
    menu_button_download_content = Gtk.Template.Child()
        
    def __init__(self, parent, game, api: Api):
        Gtk.Viewport.__init__(self)
        self.parent = parent
        self.game = game
        self.api = api
        self.progress_bar = None
        self.download = None
        self.current_state = self.game.state.DOWNLOADABLE
        
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
                image_url = template.replace("{formatter}","ggvgt_2x").replace(".png",".jpg")
                self.__add_screenshot(image_id,image_url)
        # videos
        vidx = 0
        if "videos" in self.response:
            for video in self.response["videos"]:
                thumbnail_url = video["thumbnail_url"]
                video_url = video["video_url"]
                self.__add_video(vidx,video_url,thumbnail_url)
                sidx += 1
                vidx += 1
        if sidx == 0:
            self.media_bar.hide()
            self.media_flowbox.hide()
        
        # downloads
        didx=0
        gidx=0
        downloads_store = Gtk.ListStore(str,GdkPixbuf.Pixbuf,str,str,str,str,str,str,int,int,str)
        downloads_cols = [_("Name"),_("OS"),_("Language"),_("Type"),_("Size"),_("Version"),_("State"),"Location","Id","File Size","Operating System"]
        goodies_store = Gtk.ListStore(str,str,str,str,str,str)
        goodies_cols = [_("Name"),_("Category"),_("Type"),_("Size"),_("Count"),_("Location")]
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
                        state = "N/A"
                        if self.game.installed == 1:
                            if self.game.installed_version == item["version"]:
                                state = _("Installed")
                            else:
                                state = _("Update Available")
                        links = self.__append_to_list_store_for_download(downloads_store,item,download_type,state=state,product_id=self.game.id, file_size=item["total_size"])
                        for link in links:
                            self.download_links.append(link)
        if "expanded_dlcs" in self.response:
            dlcs = self.response["expanded_dlcs"]
            for dlc in dlcs:
                downloads = dlc["downloads"]
                for dltype in downloads:
                    is_goodies = True if dltype == "bonus_content" else False
                    items = downloads[dltype]
                    download_type = DL_TYPES[dltype]
                    for item in items:
                        if is_goodies:
                            gidx += 1
                            links = self.__append_to_list_store_for_download(goodies_store,item,"DLC "+download_type,is_goodies)
                            for link in links:
                                self.goodies_links.append(link)
                        else:
                            didx += 1
                            state = self.game.get_dlc_status(item["name"],item["version"]) if self.game.installed > 0 else "N/A"
                            if state == "installed":
                                state = _("Installed")
                            elif state == "updatable":
                                state = _("Update Available")
                            elif state == "not-installed":
                                state = _("Install")
                            links = self.__append_to_list_store_for_download(downloads_store,item,"DLC "+download_type,state=state,product_id=dlc["id"], file_size=item["total_size"])
                            # add game to dlc list
                            self.game.add_dlc_from_json(dlc)
                            for link in links:
                                self.download_links.append(link)
        if (didx > 0):
            self.downloads_filter = downloads_store.filter_new()
            self.downloads_filter.set_visible_func(self.__downloads_filter,data=None)
            self.downloadstree.set_model(self.downloads_filter)
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
            self.__create_tree_columns(self.goodiestree,goodies_cols,True)
            self.goodies_header.show()
            self.goodiestree.show_all()
        
        # load the background image 
        self.__load_background_image()
        
        # handle achievements
        self.load_achievements()
    
    def load_achievements(self):
        sync_thread = threading.Thread(target=self.__load_achivements)
        sync_thread.start()
        
    def __load_achivements(self):
        achievements = self.api.get_game_achievements(self.game)
        for achievement in achievements:
            arow = AchievementRow(self,achievement)
            GLib.idle_add(self.achievements_box.add,arow)
        if len(achievements) == 0:
            # hide tab
            self.notebook.remove_page(2)

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
    
    @Gtk.Template.Callback("on_downloads_button_pressed")
    def on_downloads_button_pressed(self, widget: Gtk.Widget, event: Gdk.EventButton):
        if event.get_event_type() == Gdk.EventType.BUTTON_PRESS and event.get_button().button == Gdk.BUTTON_SECONDARY:
            # find out what was selected
            res = self.downloadstree.get_path_at_pos(event.x, event.y)
            state = None
            link = None
            fname = None
            ftype = None
            fsize = -1
            if res is not None:
                path = res[0]
                treeiter:Gtk.TreeIter = self.downloadstree.get_model().get_iter(path)
                fname = self.downloadstree.get_model().get_value(treeiter,0)
                ftype = self.downloadstree.get_model().get_value(treeiter,3)
                state = self.downloadstree.get_model().get_value(treeiter,6)
                link = self.downloadstree.get_model().get_value(treeiter,7)
                pid = self.downloadstree.get_model().get_value(treeiter,8)
                fsize = self.downloadstree.get_model().get_value(treeiter,9)
            # find out what was selected
            menu:Gtk.Menu = Gtk.Menu ()
            if state == _("Update Available"):
                update_item:Gtk.MenuItem = Gtk.MenuItem.new_with_label(_("Update"))
                menu.add(update_item)
            if ftype == _("Installer") and (state == _("Update Available") or state == _("Installed")):
                uninstall_item:Gtk.MenuItem = Gtk.MenuItem.new_with_label(_("Uninstall"))
                uninstall_item.connect("activate",self.on_menu_button_uninstall)
                menu.add(uninstall_item)
            if (ftype == _("Installer") or (ftype != _("Installer") and self.game.installed == 1)) and (state == None or state == _("N/A") or state == "" or state == "Install"):
                install_item:Gtk.MenuItem = Gtk.MenuItem.new_with_label(_("Install"))
                install_item.connect("activate",self.__install_file,link,ftype,pid,fsize,treeiter)
                menu.add(install_item)
            download_item:Gtk.MenuItem = Gtk.MenuItem.new_with_label(_("Download"))
            download_item.connect("activate",self.__download_file,link,fname)
            menu.add(download_item)
            menu.attach_to_widget(self.downloadstree)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)                
        return False
    
    @Gtk.Template.Callback("on_goodies_button_pressed")
    def on_goodies_button_pressed(self, widget: Gtk.Widget, event: Gdk.EventButton):
        if event.get_event_type() == Gdk.EventType.BUTTON_PRESS and event.get_button().button == Gdk.BUTTON_SECONDARY:
            # find out what was selected
            res = self.goodiestree.get_path_at_pos(event.x, event.y)
            link = None
            fname = None
            if res is not None:
                path = res[0]
                treeiter:Gtk.TreeIter = self.goodiestree.get_model().get_iter(path)
                link = self.goodiestree.get_model().get_value(treeiter,5)
                fname = self.goodiestree.get_model().get_value(treeiter,0)
            # find out what was selected
            menu:Gtk.Menu = Gtk.Menu ()
            download_item:Gtk.MenuItem = Gtk.MenuItem.new_with_label(_("Download"))
            download_item.connect("activate",self.__download_file,link,fname)
            menu.add(download_item)
            menu.attach_to_widget(self.goodiestree)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)                
        return False
    
    def __install_file(self,widget,link:str,ftype:str = None,product_id: int = None, fsize: int = 0, treeiter:Gtk.TreeIter = None):
        if (ftype == _("Installer")):
            # just follow the default path
            self.parent.download_game(self.game)
        elif ftype == "DLC "+_("Installer"):
            dlc = None
            if product_id is not None:
                for i in self.game.dlcs:
                    if i.id == product_id:
                        dlc = i
                        break
            
            if dlc is not None:
                dlc.platform = self.downloadstree.get_model().get_value(treeiter,10)
                dlc.language = DOWNLOAD_LANGUAGES_TO_GOG_CODE[self.downloadstree.get_model().get_value(treeiter,2)]
                dlc.available_version = self.downloadstree.get_model().get_value(treeiter,5) 
                download = Download(
                    url=self.api.get_real_download_link(link),
                    save_location=dlc.download_path,
                    title=dlc.name,
                    associated_object=dlc,
                    file_size=fsize
                )
            else:
                # fallback to game as source of generic information
                download = Download(
                    url=self.api.get_real_download_link(link),
                    save_location=self.game.download_path,
                    title=self.game.name,
                    associated_object=self.game,
                    file_size=fsize
                )
            download.register_finish_function(self.__finish_download,[treeiter,dlc])
            download.register_state_function(self.__state_func,treeiter)
            DownloadManager.download(download)
        print("Downloading: \"{}\"".format(link))

    def __state_func(self, state, treeiter:Gtk.TreeIter = None):
        if treeiter is None:
            return
        val = self.downloadstree.get_model().get_value(treeiter,6)
        if state == state.DOWNLOADING:
            val = _("Downloading")
        elif state == state.QUEUED:
            val = _("Queued")
        elif state == state.PAUSED:
            val = _("Paused")
        elif state == state.FINISHED:
            val = _("Installable")
        elif state == state.ERROR or state == state.CANCELED:
            val = _("Install")
        
        self.downloadstree.get_model().set_value(treeiter,6,val)

    def __finish_download(self, args):
        treeiter:Gtk.TreeIter = args[0] if len(args) > 0 else None
        dlc = args[1] if len(args) > 1 else None
        if treeiter is None or dlc is None:
            self.downloadstree.get_model().set_value(treeiter,6,_("Installable"))
            return
        self.downloadstree.get_model().set_value(treeiter,6,_("Installing"))
        if dlc is not None:
            # install DLC
            try:
                if os.path.exists(dlc.keep_path):
                    install_game(dlc, dlc.keep_path, main_window=self.parent)
                else:
                    install_game(dlc, dlc.download_path, main_window=self.parent)
            except (FileNotFoundError, BadZipFile):
                # error, revert state
                self.downloadstree.get_model().set_value(treeiter,6,_("Installable"))
                return
            # No error, install was successful, as such update information
            self.game.set_dlc_status(dlc.name, "installed" , dlc.available_version)
            self.downloadstree.get_model().set_value(treeiter,6,_("Installed"))

    def __download_file(self,widget,link:str,fname:str = None):
        dialog:Gtk.FileChooserDialog = Gtk.FileChooserDialog(_("Download"),self.parent,action=Gtk.FileChooserAction.SAVE,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        file_name = link[link.rfind("/")+1:] if fname is None else fname
        dialog.set_current_name(file_name)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            download = Download(
                url=self.api.get_real_download_link(link),
                save_location=dialog.get_filename()
            )
            DownloadManager.download(download)
            print("Downloading: \"{}\" to \"{}\"".format(link,dialog.get_filename()))
            
        dialog.destroy()
    
    @Gtk.Template.Callback("downloads_filter_changed")
    def downloads_filter_changed(self,widget):
        self.downloads_filter.refilter()
    
    def __on_download_selected(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][7])
            
    def __on_goodie_selected(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][5])

    def __create_tree_columns(self,tree,columns,is_goodies=False):
        i = 0
        last = len(columns) - 4
        for column_title in columns:
            renderer = None
            column = None
            if i == 1 and is_goodies == False:
                renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(column_title, renderer, pixbuf=i)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            if i >= last:
                column.set_visible(False)
            tree.append_column(column)
            i += 1
    
    def __append_to_list_store_for_download(self,store,item,download_type,is_goodie=False,state: str="", product_id: int = None, file_size: int = None):
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
                    store.append([download_name,bonus_type,download_type,file_size,bonus_count,file["downlink"]])
                else:
                    self.downloads_os.append(download_os)
                    os_image = self.__create_os_image(download_os)
                    store.append([download_name,os_image,download_language,download_type,file_size,download_version,state,file["downlink"],product_id,file["size"],item["os"]])
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

        download = Download(thumbnail_url, img)
        download.register_finish_function(self.__set_video,(vidx,video_url))
        DownloadManager.download_now(download)
        return True
    
    def __set_video(self,vidx, video_url):
        img = os.path.join(self.game.cache_dir, "video_{}.jpg".format(vidx))
        if os.path.isfile(img) and os.path.exists(img):
            btn = Gtk.LinkButton(video_url)
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img,-1,110,True)
            except Exception as ex:
                print("Could not process pixbuf for video_{}. Cause: {}".format(vidx,ex))
                return False
            tile = Gtk.Image().new_from_pixbuf(pixbuf)
            tile.show()
            btn.add(tile)
            btn.show()
            self.media_flowbox.add(btn)
            return True
        return False

    def __add_screenshot(self,image_id,image_url):
        if self.__set_screenshot(image_id):
            return True

        # Download the thumbnail
        img = os.path.join(self.game.cache_dir, "screenshot_{}_ggvgt_2x.jpg".format(image_id))

        download = Download(image_url, img)
        download.register_finish_function(self.__set_screenshot,image_id)
        DownloadManager.download_now(download)
        return True
    
    def __set_screenshot(self,image_id):
        img = os.path.join(self.game.cache_dir, "screenshot_{}_ggvgt_2x.jpg".format(image_id))
        if os.path.isfile(img) and os.path.exists(img):
            tile = Gtk.Image().new_from_file(img)
            tile.show()
            self.media_flowbox.add(tile)
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

        download = Download(image_url, img)
        download.register_finish_function(self.__set_background_image)
        DownloadManager.download_now(download)
        return True
    
    def __set_background_image(self):
        # minimum height 220
        width = self.parent.selection_window.get_allocation().width - 30
        if (width < 640):
            width = 640
        if self.background_image.get_pixbuf() is None:
            img = os.path.join(self.game.cache_dir, "{}_background.jpg".format(self.game.id))
            if os.path.isfile(img) and os.path.exists(img):
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img,width,-1,True)
                    GLib.idle_add(self.background_image.set_from_pixbuf, pixbuf)
                except Exception as ex:
                    print("Could not format background image. Cause: {}".format(ex))            
                return True
        else:
            pixbuf = self.background_image.get_pixbuf()
            try:
                pixbuf.scale_simple(width,-1,GdkPixbuf.InterpType.BILINEAR)
                self.background_image.set_from_pixbuf(pixbuf)
            except Exception as ex:
                print("Could not scale background image. Cause: {}".format(ex))            
            return True
        return False
    
    @Gtk.Template.Callback("on_box_resize")
    def on_box_resize(self,container):
        self.__set_background_image()
        return

    @Gtk.Template.Callback("on_button_clicked")
    def on_button_click(self, widget) -> None:
        dont_act_in_states = [self.game.state.QUEUED, self.game.state.DOWNLOADING, self.game.state.INSTALLING, self.game.state.UNINSTALLING]
        if self.current_state in dont_act_in_states:
            return
        elif self.current_state == self.game.state.INSTALLED or self.current_state == self.game.state.UPDATABLE:
            start_game(self.game, self.parent)
        elif self.current_state == self.game.state.INSTALLABLE:
            install_thread = threading.Thread(target=self.__install)
            install_thread.start()
        elif self.current_state == self.game.state.DOWNLOADABLE:
            download_thread = threading.Thread(target=self.__download_file)
            download_thread.start()

    @Gtk.Template.Callback("on_menu_button_cancel_clicked")
    def on_menu_button_cancel(self, widget):
        self.parent.cancel_download(self.game)

    @Gtk.Template.Callback("on_menu_button_settings_clicked")
    def on_menu_button_settings(self, widget):
        config_game(self.game)

    @Gtk.Template.Callback("on_menu_button_uninstall_clicked")
    def on_menu_button_uninstall(self, widget):
        if not self.parent.uninstall_game(self.game):
            return
        # user clicked on OK
        self.update_options()
        # reset status for downloads table
        for row in self.downloadstree.get_model():
            if row[3] == _("Installer"):
                row[6] = _("Install")
            else:
                row[6] = _("N/A")
            

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
                parent=self.parent,
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
        if self.current_state == self.game.state.UPDATE_INSTALLABLE:
            self.parent.update(self.game)
        elif self.current_state == self.game.state.UPDATABLE or self.current_state == self.game.state.INSTALLED:
            self.parent.download_update(self.game)

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
        if (self.current_state == self.game.state.INSTALLED or self.current_state == self.game.state.UPDATABLE):
            self.button.set_label(_("play"))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        elif (self.current_state == self.game.state.DOWNLOADABLE):
            self.button.set_label(_("download"))
            self.installed_version_label.set_text("")
        elif (self.current_state == self.game.state.DOWNLOADING or self.current_state == self.game.state.UPDATE_DOWNLOADING):
            self.button.set_label(_("downloading.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.state.QUEUED):
            self.button.set_label(_("in queue.."))
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.state.UPDATE_QUEUED):
            self.menu_button_cancel.show()
        elif (self.current_state == self.game.state.INSTALLING):
            self.button.set_label(_("installing.."))
        elif (self.current_state == self.game.state.UNINSTALLING):
            self.button.set_label(_("uninstalling.."))
        elif (self.current_state == self.game.state.UPDATING):
            self.button.set_label(_("updating.."))
            self.menu_button_uninstall.show()
            self.menu_button_open.show()
        # special cases 
        if self.game.installed == 1 and self.game.updates is not None and self.game.updates > 0:
            self.update_icon.show()
            # figure out if we should fetch or install the update
            if (self.current_state == self.game.state.UPDATABLE or self.current_state == self.game.state.INSTALLED):
                self.menu_button_update.set_label(_("Update"))
            elif (self.current_state == self.game.state.UPDATE_INSTALLABLE):
                self.menu_button_update.set_label(_("Install Update"))
            else:
                self.menu_button_update.set_label(_("Update"))
            self.menu_button_update.show()
        if not self.game.url:
            self.menu_button_store.hide()
        if self.game.platform == "windows":
            self.menu_button_settings.show()

    def reload_state(self):
        dont_act_in_states = [self.game.state.QUEUED, self.game.state.DOWNLOADING, self.game.state.INSTALLING, self.game.state.UNINSTALLING, self.game.state.UPDATING, self.game.state.UPDATE_QUEUED, self.game.state.UPDATE_DOWNLOADING]
        if self.current_state in dont_act_in_states:
            return
        if self.game.install_dir and os.path.exists(self.game.install_dir):
            self.update_to_state(self.game.state.INSTALLED)
        elif os.path.exists(self.keep_path):
            self.update_to_state(self.game.state.INSTALLABLE)
        else:
            self.update_to_state(self.game.state.DOWNLOADABLE)
        self.update_options()

    def update_to_state(self, state):
        self.current_state = state
        if state == self.game.state.DOWNLOADABLE or state == self.game.state.INSTALLABLE or state == self.game.state.UPDATE_INSTALLABLE or state == self.game.state.INSTALLED or state == self.game.state.UPDATABLE:
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

        self.update_options()
        