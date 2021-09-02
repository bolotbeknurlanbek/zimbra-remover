import re
from subprocess import PIPE, CompletedProcess, run
from time import sleep, time
import random
from datetime import datetime
from manager import Manager


process: Manager = Manager()


def run_command(command: str) -> CompletedProcess:
    """Запустить команду в консоли"""

    return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)


def get_all_users() -> list[str]:
    """Получить список всех пользователей"""

    result = run_command('zmprov --ldap getAllAccounts')
    return result.stdout.splitlines()


def filter_and_delete_messages(maillist: list[str], filter: str, count_only: bool = False) -> tuple[list[str], list[str]]:
    """Удалить письма в почте пользователя найденные по указанному фильтру"""

    messages:   list[str] = []
    mails:      list[str] = []
    
    for mail in maillist:

        searchresult = run_command(f'zmmailbox --zadmin --mailbox {mail} search --limit 999 --types message {filter}')

        for line in searchresult.stdout.splitlines():
            match = re.search(r'(?!^\d\W\W)\d+(?=\W+mess)', line)
            if match:
                
                message = match.group()
                
                if not count_only:
                    run_command(f'zmmailbox --zadmin --mailbox {mail} deleteMessage {message}')
                
                messages.append(message)

        mails.append(mail)

    return mails, messages
