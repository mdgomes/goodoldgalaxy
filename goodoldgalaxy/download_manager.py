import os
import shutil
import time
import threading
import queue
from requests.exceptions import ConnectionError
from goodoldgalaxy.config import Config
from goodoldgalaxy.constants import DOWNLOAD_CHUNK_SIZE, MINIMUM_RESUME_SIZE, SESSION
from goodoldgalaxy.download import Download


class __DownloadManger:
    """
    Download Manager implementation.
    
    Offers the following functionality:
    
    * Download files (as specified in Download objects)
    * Pauses downloads
    * Cancels downloads
    * Resumes downloads
    * Lists downloads
    """
    def __init__(self):
        self.__queue = queue.Queue()
        self.__current_download = None
        self.__cancel = False
        self.__paused = False
        self.__queue_wait = 0.1
        self.__completed = []
        self.__listeners = []

        download_thread = threading.Thread(target=self.__download_thread)
        download_thread.daemon = True
        download_thread.start()

    def register_listener(self,listener_func):
        """
        Register a listener function that wants to be let know about new downloads.
        
        Parameters:
        -----------
            listener_func: lambda -> Listener function to register that receives on argument that is a Download instance
        """
        if listener_func is None:
            return
        self.__listeners.append(listener_func)
        
    def unregister_listener(self,listener_func):
        """
        Unregister a listener function.
        
        Parameters:
        -----------
            listener_func: lambda -> Listener function to unregister
        """
        if listener_func is None:
            return 
        self.__listeners.remove(listener_func)

    def queue_wait(self) -> float:
        """
        Gets the queue wait value in seconds.
        
        Return:
        -------
            Queue wait time in seconds
        """
        return self.__queue_wait
    
    def set_queue_wait(self, queue_wait:float = 0.1):
        """
        Sets the queue wait value.
        
        Notes:
        ------
            Values smaller than 10 milliseconds (i.e. 0.01) are set to 0.01
        
        Parameters:
        -----------
            queue_wait : float Queue wait time in seconds
        """
        
        if (queue_wait < 0.01):
            queue_wait = 0.01
        self.__queue_wait = queue_wait
    
    def is_paused(self) -> bool:
        """
        Checks if file downloads are paused.
        
        Return:
        -------
            True if all downloads are paused, False otherwise
        """
        return self.__paused
        
    # Pause all downloads
    def pause(self):
        """Pause all file downloads"""
        self.__paused = True
        
    # Resume all downloads
    def resume(self):
        """Resumes all file downloads"""
        self.__paused = False
    
    def list(self) -> list:
        """
        Lists current downloads in the queue.
        
        Returns:
        --------
            List with Download objects
        """
        ret = []
        if (self.__current_download is not None):
            ret.append(self.__current_download)
        for i in self.__queue.queue:
            ret.append(i)
        for i in self.__completed:
            ret.append(i)
        return ret
    
    def clear_download(self, download):
        """
        Method used to clear a specific download from the completed list.
        
        Parameters:
        -----------
            download: Download to remove
        """
        if download is None:
            return
        if download in self.__completed:
            self.__completed.remove(download)

    def download(self, download):
        """
        Downloads either a file or a list of files.
        
        Parameters
        ----------
        download: Download or List
            File to download
        """
        if isinstance(download, Download):
            print("Added {} to the download queue".format(download.url))
            for listener_func in self.__listeners:
                listener_func(download)
            self.__queue.put(download)
        else:
            # Assume we've received a list of downloads
            for d in download:
                print("Added {} to the download queue".format(d.url))
                for listener_func in self.__listeners:
                    listener_func(d)
                self.__queue.put(d)

    def download_now(self, download):
        download.set_priority(-1);
        download_file_thread = threading.Thread(target=self.__download_file, args=(download,))
        download_file_thread.daemon = True
        download_file_thread.start()

    def cancel_download(self, downloads):
        # Make sure we're always dealing with a list
        if isinstance(downloads, Download):
            downloads = [downloads]

        for download in downloads:
            if download == self.__current_download:
                self.cancel_current_download()
            else:
                self.__paused = True
                new_queue = queue.Queue()
                while not self.__queue.empty():
                    queued_download = self.__queue.get()
                    if download == queued_download:
                        download.cancel()
                    else:
                        new_queue.put(queued_download)
                self.__queue = new_queue
                self.__paused = False

    def cancel_current_download(self):
        self.__cancel = True

    def cancel_all_downloads(self):
        while not self.__queue.empty():
            self.__queue.get()
        self.cancel_current_download()

        # wait for the download to be fully cancelled
        while self.__current_download:
            time.sleep(self.__queue_wait)

    def __download_thread(self):
        while True:
            if not self.__queue.empty() and not self.__paused:
                self.__current_download = self.__queue.get()
                if self.__current_download.is_paused():
                    # add to the end of the queue
                    self.__queue.put(self.__current_download)
                    # also wait a bit
                    time.sleep(self.__queue_wait)
                    continue
                self.__download_file(self.__current_download)
            time.sleep(self.__queue_wait)

    def __download_file(self, download):
        self.prepare_location(download.save_location)
        download_max_attempts = 5
        download_attempt = 0
        result = False
        while download_attempt < download_max_attempts:
            try:
                start_point, download_mode = self.get_start_point_and_download_mode(download)
                result = self.download_operation(download, start_point, download_mode)
                break
            except ConnectionError as e:
                print(e)
                download_attempt += 1
        # mark download as complete
        self.__mark_download_as_complete(download,result)
        # Successful downloads
        if result:
            if download.number == download.out_of_amount:
                finish_thread = threading.Thread(target=download.finish)
                finish_thread.start()
            if self.__queue.empty():
                Config.unset("current_download")
        # Unsuccessful downloads and cancels
        else:
            self.__cancel = False
            download.cancel()
            self.__current_download = None
            os.remove(download.save_location)

    def prepare_location(self, save_location):
        # Make sure the directory exists
        save_directory = os.path.dirname(save_location)
        if not os.path.isdir(save_directory):
            os.makedirs(save_directory, mode=0o755)

        # Fail if the file already exists
        if os.path.isdir(save_location):
            shutil.rmtree(save_location)
            print("{} is a directory. Will remove it, to make place for installer.".format(save_location))

    def get_start_point_and_download_mode(self, download):
        # Resume the previous download if possible
        start_point = 0
        download_mode = 'wb'
        if os.path.isfile(download.save_location):
            if self.__is_same_download_as_before(download):
                print("Resuming download {}".format(download.save_location))
                download_mode = 'ab'
                start_point = os.stat(download.save_location).st_size
            else:
                os.remove(download.save_location)
        return start_point, download_mode
    
    def __mark_download_as_complete(self, download, result: bool = None):
        # don't track these downloads
        if (download.priority() < 0):
            return
        self.__completed.append(download)

    def download_operation(self, download, start_point, download_mode):
        # Download the file
        download.set_queued(False)
        resume_header = {'Range': 'bytes={}-'.format(start_point)}
        download_request = SESSION.get(download.url, headers=resume_header, stream=True, timeout=30)
        downloaded_size = start_point
        file_size = -1
        if download_request.headers.get('content-length') is not None:
            file_size = int(download_request.headers.get('content-length'))
        result = True
        if downloaded_size < file_size:
            with open(download.save_location, download_mode) as save_file:
                for chunk in download_request.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    # Pause if needed
                    if (download.priority() >= 0):
                        while self.__paused:
                            time.sleep(0.1)
                    save_file.write(chunk)
                    downloaded_size += len(chunk)
                    download.set_downloaded(downloaded_size)
                    if self.__cancel:
                        self.__cancel = False
                        save_file.close()
                        download.cancel()
                        self.__current_download = None
                        result = False
                        break
                    if file_size > 0:
                        progress = int(downloaded_size / file_size * 100)
                        download.set_progress(progress)
                save_file.close()
        return result

    def __is_same_download_as_before(self, download):
        file_stats = os.stat(download.save_location)
        # Don't resume for very small files
        if file_stats.st_size < MINIMUM_RESUME_SIZE:
            return False

        # Check if the first part of the file
        download_request = SESSION.get(download.url, stream=True)
        size_to_check = DOWNLOAD_CHUNK_SIZE*5
        for chunk in download_request.iter_content(chunk_size=size_to_check):
            with open(download.save_location, "rb") as file:
                file_content = file.read(size_to_check)
                return file_content == chunk


DownloadManager = __DownloadManger()
