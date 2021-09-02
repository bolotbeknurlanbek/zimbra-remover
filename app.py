import asyncio
import uvicorn
from multiprocessing import Pool, cpu_count
from typing import Optional
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI, Body, Depends, BackgroundTasks
from concurrent.futures.process import ProcessPoolExecutor
from functools import partial

from functions import process, get_all_users, filter_and_delete_messages
from dependencies import authenticate, allow_one_process


app = FastAPI(default_response_class=ORJSONResponse)


@app.on_event('startup')
async def on_startup():
    asyncio.create_task(process.run_main())


def run_background(fn, chunked, filter, count_only) -> None:
    
    try:
        
        # Pool без аргументов использует максимальное кол-во процессоров
        with Pool() as pool:
            
            f = partial(fn, filter=filter, count_only=count_only)
            
            for mails, messages in pool.map(f, chunked):
                process.extend_processed_mails(mails)
                process.extend_deleted_messages(messages)

    finally:
        process.remove_worker_and_swap()


@app.get('/status', dependencies=[Depends(authenticate)])
def status():
    """
    Статус API
    """
    
    return {
        'status': 'Blocked' if process.is_blocked else 'Available',
        **process.last_state,
        **process.current_state
        }


@app.get('/delete_messages', dependencies=[Depends(authenticate), Depends(allow_one_process)])
async def delete_messages(background: BackgroundTasks,
                          filter: str = Body(..., embed=True),
                          count_only: Optional[bool] = Body(False, embed=True)):
    """
    Удалить письмо из почты всех пользователей
    """
    
    # Обозначить данное действие
    process.set_current_state(filter, action='DELETE' if not count_only else 'COUNT')
    
    try:

        # Использовать все ядра машины
        cpu: int = cpu_count()
        
        # Заблокировать процесс
        process.add_workers(2)
        
        # Получить список всех пользователей
        mails: list[str] = get_all_users()
        
        # Распределить список пользователей на все ядра машины
        chunked = [
            mails[(i * len(mails)) // cpu : ((i + 1) * len(mails)) // cpu] 
            for i in range(cpu)
        ]

        background.add_task(run_background, filter_and_delete_messages, chunked, filter, count_only)

    except:
        raise
    
    finally:
        
        # Разблокировать процесс
        process.remove_worker_and_swap()

    return {'result': 'Accepted'}

if __name__ == "__main__":
    uvicorn.run("mail-remover:app", host="0.0.0.0", port=8754, reload=True)