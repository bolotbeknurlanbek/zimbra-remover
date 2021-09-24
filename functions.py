import re
from manager import Manager
from functools import partial
from multiprocessing import Pool
from subprocess import PIPE, CompletedProcess, run


process: Manager = Manager()


def run_command(command: str) -> CompletedProcess:
    """Запустить команду в консоли"""

    return run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)


def get_all_users() -> list[str]:
    """Получить список всех пользователей"""

    result = run_command('zmprov --ldap getAllAccounts')
    return result.stdout.splitlines()


def filter_and_delete_messages(maillist: list[str], filter: str, count_only: bool = False) -> None:
    """Удалить письма в почте пользователя найденные по указанному фильтру"""

    try:

        for mail in maillist:

            searchresult = run_command(f'zmmailbox --zadmin --mailbox {mail} search --limit 999 --types message {filter}')

            for line in searchresult.stdout.splitlines():
                match = re.search(r'(?!^\d\W\W)\d+(?=\W+mess)', line)
                if match:
                    
                    message = match.group()
                    
                    if not count_only:
                        run_command(f'zmmailbox --zadmin --mailbox {mail} deleteMessage {message}')
                    
                    process.add_deleted_message(message)

            process.add_processed_mail(mail)
    except:
        raise

    finally:
        process.remove_worker_and_swap()


def run_background(fn, chunked, filter, count_only) -> None:
    """Запустить процесс в бэкграунде"""
    
    try:
        
        # Pool без аргументов использует все процессоры машины
        with Pool() as pool:
            
            f = partial(fn, filter=filter, count_only=count_only)
            
            for mails, messages in pool.map(f, chunked):
                process.extend_processed_mails(mails)
                process.extend_deleted_messages(messages)

    finally:
        process.remove_worker_and_swap()
