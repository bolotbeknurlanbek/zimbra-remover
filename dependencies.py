from typing import Optional
from fastapi import Header, HTTPException, status

from functions import process


async def authenticate(authorization: Optional[str] = Header(None)):
    """
    Проверка авторизационных данных
    """
    
    api_key: str = "a3c42c77439a5a618f6d6c50d37c71172bc129888944425f2c62aeb396960f4e"
    
    if not authorization or authorization != api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="API key неверный или отсутствует")


async def allow_one_process():
    """
    Разрешить только один экземпляр данного процесса
    """
    
    if process.is_blocked:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Сервер занят выполнением задачи")
