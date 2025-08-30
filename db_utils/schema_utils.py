from collections import defaultdict
from .executor import execute_query


def schema_text_from_information_schema() -> str | None:
    """
    Costruisce una rappresentazione compatta dello schema leggendo da information_schema.
    Ritorna una stringa tipo:
        TABLE movies(id, titolo, anno, genere, piattaforma_1_id, piattaforma_2_id, regista_id);
        TABLE registi(id, nome, eta);
        TABLE piattaforme(id, nome);
    oppure None se qualcosa va storto.
    """
    cols_sql = """
        SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    ok, rows, err = execute_query(cols_sql)
    if not ok or not rows:
        return None

    by_table = defaultdict(list)
    for r in rows:
        by_table[r["table_name"]].append(r["column_name"])

    lines = []
    for tbl in sorted(by_table.keys()):
        cols_sorted = ", ".join(by_table[tbl])
        lines.append(f"TABLE {tbl}({cols_sorted});")
    return "\n".join(lines)