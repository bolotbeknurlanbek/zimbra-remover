from datetime import datetime


class Manager:
    """
    Класс для управления данным экземпляром программы
    """
    
    def __init__(self):
        
        self.workers:                   int         = 0

        self.last_filter:               str         = ''
        self.last_action:               str         = ''
        self.last_request_date:         datetime    = None
        self.last_processed_mails:      list[str]   = []
        self.last_deleted_messages:     list[str]   = []
        
        self.current_filter:            str         = ''
        self.current_action:            str         = ''
        self.current_request_date:      datetime    = None
        self.current_processed_mails:   list[str]   = []
        self.current_deleted_messages:  list[str]   = []


    def add_worker(self, n: int = 1) -> None:
        self.workers += n
        
        
    def remove_worker_and_swap(self) -> None:
        self.workers -= 1
        if not self.is_blocked:
            self.swap_states()
        
        
    def add_deleted_message(self, message: str) -> None:
        self.current_deleted_messages.append(message)
    
    
    def add_processed_mail(self, mail: str) -> None:
        self.current_processed_mails.append(mail)
    
    
    def extend_deleted_messages(self, messages: list[str]) -> None:
        self.current_deleted_messages.extend(messages)
        
        
    def extend_processed_mails(self, mails: list[str]) -> None:
        self.current_processed_mails.extend(mails)
        
        
    def set_current_state(self, filter: str, action: str):
        self.current_filter             = filter
        self.current_action             = action
        self.current_request_date       = datetime.now()
        self.current_processed_mails    = []
        self.current_deleted_messages   = []
    
    
    def swap_states(self) -> None:
        self.last_request_date          = self.current_request_date
        self.last_processed_mails       = self.current_processed_mails.copy()
        self.last_deleted_messages      = self.current_deleted_messages.copy()
        self.last_filter                = self.current_filter
        self.last_action                = self.current_action
        
        self.current_filter             = ''
        self.current_action             = ''
        self.current_request_date       = None
        self.current_processed_mails    = []
        self.current_deleted_messages   = []


    @property
    def is_blocked(self):
        return self.workers != 0


    @property
    def last_state(self) -> dict:
        return {
            'last_filter':              self.last_filter,
            'last_action':              self.last_action,
            'last_request_date':        self.last_request_date,
            'last_processed_mails':     self.last_processed_mails,
            'last_deleted_messages':    self.last_deleted_messages
        }
    
    
    @property
    def current_state(self) -> dict:
        return {
            'current_filter':              self.current_filter,
            'current_action':              self.current_action,
            'current_request_date':        self.current_request_date,
            'current_processed_mails':     self.current_processed_mails,
            'current_deleted_messages':    self.current_deleted_messages
        }
