import os

from aiomysql import create_pool
from aiomysql.utils import _PoolContextManager as PoolContextManager


def get_pool(autocommit: bool = True) -> PoolContextManager:
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    host, port = db_host.split(":") if ":" in db_host else (db_host, 3306)
    return create_pool(
        host=host,
        port=int(port),
        user=db_user,
        password=db_pass,
        db=db_name,
        autocommit=autocommit
    )
