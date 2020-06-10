from zipfile import BadZipFile


class Download:
    def __init__(self, 
                 url, 
                 save_location, 
                 finish_func=None, 
                 finish_func_args=None, 
                 error_func=None, 
                 error_func_args=None,
                 progress_func=None, 
                 progress_func_args=None,
                 cancel_func=None, 
                 cancel_func_args=None,
                 number=1, 
                 out_of_amount=1
            ):
        self.url = url
        self.save_location = save_location
        self.__finish_func = finish_func
        self.__progress_func = progress_func
        self.__progress_func_args = progress_func_args
        self.__finish_func_args = finish_func_args
        self.__cancel_func = cancel_func
        self.__cancel_func_args = cancel_func_args
        self.__error_func = error_func
        self.__error_func_args = error_func_args
        self.number = number
        self.out_of_amount = out_of_amount

    def set_progress(self, percentage: int) -> None:
        if self.__progress_func:
            if self.out_of_amount > 1:
                # Change the percentage based on which number we are
                progress_start = 100/self.out_of_amount*(self.number-1)
                percentage = progress_start + percentage/self.out_of_amount
            if self.__progress_func_args is None:
                self.__progress_func(percentage)
            else:
                self.__progress_func(percentage,self.__progress_func_args)

    def finish(self):
        if self.__finish_func:
            try:
                if self.__finish_func_args:
                    self.__finish_func(self.__finish_func_args)
                else:
                    self.__finish_func()
            except (FileNotFoundError, BadZipFile):
                self.cancel()
            except Exception as e:
                if self.__error_func:
                    if self.__error_func_args is None:
                        self.__error_func(e)
                    else:
                        self.__error_func(self.__error_func_args)
                else:
                    self.cancel()

    def cancel(self):
        if self.__cancel_func:
            if self.__cancel_func_args is None:
                self.__cancel_func()
            else:
                self.__cancel_func(self.__cancel_func_args)
