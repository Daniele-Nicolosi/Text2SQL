from models import TableColumn, Property, ResultItem
from typing import List, Dict, Tuple
from db_utils.crud import insert_or_update_film
from db_utils.executor import execute_query


def get_schema() -> list[TableColumn]:
    """
    Restituisce la struttura delle tabelle del database come lista di TableColumn.
    """
    columns = [
        # Colonne della tabella movies
        TableColumn(table_name="movies", table_column="id"),
        TableColumn(table_name="movies", table_column="titolo"),
        TableColumn(table_name="movies", table_column="anno"),
        TableColumn(table_name="movies", table_column="genere"),
        TableColumn(table_name="movies", table_column="piattaforma_1"),
        TableColumn(table_name="movies", table_column="piattaforma_2"),
        TableColumn(table_name="movies", table_column="regista_id"),

        # Colonne della tabella registi
        TableColumn(table_name="registi", table_column="id"),
        TableColumn(table_name="registi", table_column="nome"),
        TableColumn(table_name="registi", table_column="eta"),

        # Colonne della tabella piattaforme
        TableColumn(table_name="piattaforme", table_column="id"),
        TableColumn(table_name="piattaforme", table_column="nome"),
    ]
    return columns


def add_row_to_db(data_line: str) -> bool:
    """
    Aggiunge o aggiorna una riga nel DB, usando insert_or_update_film.
    """
    
    result = insert_or_update_film(data_line)

    return result


def run_sql_query(sql_query: str) -> Tuple[str, List[Dict] | None, str | None]:
    """
    Esegue una query SQL in modalità sicura e converte i risultati in formato strutturato.

    Blocca query pericolose (DROP, DELETE, UPDATE) e gestisce eventuali errori.

    Args:
        sql_query (str): la query SQL da eseguire.

    Returns:
        Tuple[str, List[Dict] | None, str | None]:
            - stato: "valid", "invalid" o "unsafe"
            - results: lista di risultati strutturati (ResultItem) oppure None
            - error: messaggio di errore se presente, altrimenti None
    """
    # Sicurezza: blocco di query pericolose
    if "DROP" in sql_query.upper():
        return "unsafe", None, "Operazione DROP non permessa"
    if "DELETE" in sql_query.upper():
        return "unsafe", None, "Operazione DELETE non permessa"
    if "UPDATE" in sql_query.upper():
        return "unsafe", None, "Operazione UPDATE non permessa"

    # Esecuzione query tramite modulo executor
    success, rows, error = execute_query(sql_query)
    if not success:
        return "invalid", None, error

    table_name = "film"
    results: List[Dict] = []

    # Conversione dei risultati in ResultItem con Property
    for row in rows:
        props = []
        for k, v in row.items():
            # Mappatura specifica: 'titolo' -> 'name'
            if k == "titolo":
                props.append(Property(property_name="name", property_value=v))
            else:
                props.append(Property(property_name=k, property_value=v))
        results.append(ResultItem(item_type=table_name, properties=props).dict())

    return "valid", results, None


def call_nlp_module(question: str, model: str | None = None) -> str:
    """
    Stub: convertela domanda in SQL.
    In futuro invocherà il modulo NLP dello studente A
    """
    if "prezzo" in question.lower():
        return "SELECT * FROM prodotti WHERE prezzo > 50"
    if "drop" in question.lower():
        return "DROP ALL"
    return "SELECT * FROM prodotti"

