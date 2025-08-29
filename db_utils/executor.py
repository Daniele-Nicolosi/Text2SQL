from typing import List, Dict, Tuple, Optional
from .connection import get_connection

def execute_query(sql_query: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
    """
    Esegue una query SQL su MariaDB e restituisce una lista di dict.
    """
    try:
        conn, cur = get_connection()
        cur.execute(sql_query)
        rows = cur.fetchall()
        return True, rows, None

    except Exception as e:
        return False, None, str(e)

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
