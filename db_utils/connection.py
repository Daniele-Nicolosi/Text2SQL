import mariadb
from typing import Tuple

def get_connection() -> Tuple[mariadb.Connection, mariadb.Cursor]:
    """
    Restituisce una connessione e un cursore a MariaDB.
    """
    conn = mariadb.connect(
        host="mariadb",
        port=3306,
        user="user",
        password="password",
        database="movies_db"
    )
    cur = conn.cursor(dictionary=True)
    return conn, cur
