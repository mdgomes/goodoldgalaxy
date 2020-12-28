from enum import Enum
from zipfile import BadZipFile

class Download:
    __state = Enum('state', 'QUEUED DOWNLOADING PAUSED FINISHED CANCELED ERROR')
    """
    Definition of a downloadable object.
    
    These objects require a target URL and a save location at the very least.
    Providing a title is also useful.
    """
    
    def __init__(self, 
                 url, 
                 save_location,
                 title=None,
                 associated_object=None,
                 download_row=None,
                 number=1, 
                 out_of_amount=1,
                 file_size=-1
            ):
        self.url = url
        self.save_location = save_location
        self.download_row = download_row
        self.associated_object = associated_object
        self.file_size = file_size
        self.__priority = 0
        self.__completed: bool = None
        # create a title
        if title is None:
            if url.find('?') > 0:
                title = url[url.rfind('/')+1:url.find('?')]
            else:
                title = url[url.rfind('/')+1:]
        self.title = title
        self.__finish_funcs = []
        self.__progress_funcs = []
        self.__cancel_funcs = []
        self.__error_funcs = []
        self.__state_funcs = []
        self.number = number
        self.out_of_amount = out_of_amount
        self.__downloaded = 0
        self.__paused = False
        self.__queued = True
        self.__progress = -1
        self.__state:Enum = self.__state.QUEUED
        
    def state(self):
        """
        Gets the download state.
        
        Return:
        -------
            state: Download state enumeration entry
        """
        return self.__state
        
    def register_finish_function(self, func = None, func_args = None):
        """
        Registers a new finish function with associated arguments.
        
        Parameters:
        -----------
            func: Function that is invoked when the download finishes
            func_args: Function arguments
        """
        if func is None:
            return
        self.__finish_funcs.append([func,func_args])
        
    def get_finish_functions(self):
        """
        Gets the list of registered finish functions.
        
        The first argument of each entry is the function and the second the arguments if existing.
        
        Return:
        -------
            list: Finish functions
        """
        return self.__finish_funcs
        
    def register_progress_function(self,func = None, func_args = None):
        """
        Registers a new progress function with associated arguments.
        
        Parameters:
        -----------
            func: Function that is invoked when the download progress is updated
            func_args: Function arguments
        """
        if func is None:
            return
        self.__progress_funcs.append([func,func_args])
        
    def get_progress_functions(self):
        """
        Gets the list of registered progress update functions.
        
        The first argument of each entry is the function and the second the arguments if existing.
        
        Return:
        -------
            list: Progress functions
        """
        return self.__progress_funcs
        
    def register_cancel_function(self,func = None, func_args = None):
        """
        Registers a new cancel function with associated arguments.
        
        Parameters:
        -----------
            func: Function that is invoked when the download is canceled
            func_args: Function arguments
        """
        if func is None:
            return
        self.__cancel_funcs.append([func,func_args])
        
    def get_cancel_functions(self):
        """
        Gets the list of registered cancel functions.
        
        The first argument of each entry is the function and the second the arguments if existing.
        
        Return:
        -------
            list: Cancel functions
        """
        return self.__cancel_funcs
        
    def register_error_function(self,func = None, func_args = None):
        """
        Registers a new error function with associated arguments.
        
        Parameters:
        -----------
            func: Function that is invoked when the download terminates with an error
            func_args: Function arguments
        """
        if func is None:
            return
        self.__error_funcs.append([func,func_args])
        
    def get_error_functions(self):
        """
        Gets the list of registered error functions.
        
        The first argument of each entry is the function and the second the arguments if existing.
        
        Return:
        -------
            list: Error functions
        """
        return self.__error_funcs
    
    def register_state_function(self,func = None, func_args = None):
        """
        Registers a new state update function with associated arguments.
        
        Parameters:
        -----------
            func: Function that is invoked when the download changes state
            func_args: Function arguments
        """
        if func is None:
            return
        self.__state_funcs.append([func,func_args])
        
    def get_state_functions(self):
        """
        Gets the list of registered state functions.
        
        The first argument of each entry is the function and the second the arguments if existing.
        
        Return:
        -------
            list: State update functions
        """
        return self.__state_funcs
        
    def priority(self) -> int:
        """
        Gets the download priority.
        
        Return:
        -------
            int : -1 for immediate downloads, greater than 0 for normal downloads, being 0 the highest priority
        """
        return self.__priority
    
    def set_priority(self, priority : int):
        """
        Sets the download priority.
        
        Parameters:
        -----------
            priority : int -> -1 for immediate downloads, greater than 0 for normal downloads, being 0 the highest priority
        """
        self.__priority = priority

    def pause(self):
        """Pauses the download"""
        self.__paused = True
        self.__set_state(self.__state.PAUSED)
        
    def resume(self):
        """Resumes the download"""
        self.__paused = False
        self.__set_state(self.__state.QUEUED)

    def is_paused(self) -> bool:
        """
        Checks if the Download is paused.
        
        Return:
        -------
            True if the download is paused, False otherwise
        """
        return self.__paused
    
    def set_queued(self, state: bool = True):
        """
        Sets whether or not the download is queued. Only the Download Manager should change this.
        
        Parameters:
        -----------
            state: bool -> True if the download is queued, False if the download is running
        """
        self.__queued = state
        self.__set_state(self.__state.DOWNLOADING if state == False else self.__state.QUEUED)
    
    def is_queued(self) -> bool:
        """
        Checks if the Download is queued.
        
        Return:
        -------
            True if the download is queued, False otherwise
        """
        return self.__queued
    
    def is_completed(self) -> bool:
        """
        Checks whether or not the download was completed.
        
        Return:
        -------
            bool: True if the download was completed (with or without success), False otherwise
        """
        return self.__completed is not None
    
    def set_completed(self,result: bool = True):
        """
        Sets the whether or not the download was successful.
        
        Parameters:
        -----------
            result: bool -> True if the download as successful, False otherwise
        """
        self.__completed = result
        self.__state = self.__state.FINISHED if result == True else self.__state.ERROR

    def get_progress(self) -> int:
        """
        Gets the current progress.
        
        Return:
        ------
            int : Progress percentage or -1 if indeterminate
        """
        return self.__progress

    def set_progress(self, percentage: int) -> None:
        """
        Updates the download percentage.
        
        Parameters:
        -----------
            percentage: int -> Download percentage, -1 for unknown
        """
        self.__progress = percentage
        for entry in self.__progress_funcs:
            progress_func = entry[0]
            progress_func_args = entry[1]
            if self.out_of_amount > 1:
                # Change the percentage based on which number we are
                progress_start = 100/self.out_of_amount*(self.number-1)
                percentage = progress_start + percentage/self.out_of_amount
                percentage = int(percentage)
            if progress_func_args is None:
                progress_func(percentage)
            else:
                progress_func(percentage, progress_func_args)

    def set_downloaded(self, downloaded : int) -> None:
        """
        Set downloaded value.
        
        Parameters:
        -----------
            downloaded : int -> Downloaded size in bytes
        """
        self.__downloaded = downloaded

    def get_downloaded(self):
        """
        Get downloaded value.
        
        Return:
        -------
            int : Downloaded size in bytes
        """
        return self.__downloaded

    def error(self, e:Exception = None):
        """
        Indicates that the download finished with an error.
        
        Parameters:
        -----------
            e: Exception -> Optional exception
        """
        self.__set_state(self.__state.ERROR)
        for entry in self.__error_funcs:
            error_func = entry[0]
            error_func_args = entry[1]
            if error_func_args is None:
                error_func(e)
            else:
                error_func(e,error_func_args)

    def finish(self):
        """
        Indicates that the download finished with success.
        """
        self.__set_state(self.__state.FINISHED)
        for entry in self.__finish_funcs:
            finish_func = entry[0]
            finish_func_args = entry[1]
            try:
                if finish_func_args:
                    finish_func(finish_func_args)
                else:
                    finish_func()
            except (FileNotFoundError, BadZipFile):
                self.cancel()
            except Exception as e:
                self.error(e)

    def cancel(self):
        """
        Indicates that the download was canceled.
        """
        self.__set_state(self.__state.CANCELED)
        for entry in self.__cancel_funcs:
            cancel_func = entry[0]
            cancel_func_args = entry[1]
            if cancel_func_args is None:
                cancel_func()
            else:
                cancel_func(cancel_func_args)

    def __set_state(self, state):
        """
        Sets the current download state.
        
        Parameters:
        -----------
            state: State enumeration entry
        """
        self.__state = state
        for entry in self.__state_funcs:
            state_func = entry[0]
            state_func_args = entry[1]
            if state_func_args is None:
                state_func(state)
            else:
                state_func(state,state_func_args)
