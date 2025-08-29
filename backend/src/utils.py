from models import TableColumn, Property, ResultItem
from typing import List, Dict, Tuple
from db_utils.crud import insert_or_update_film
from db_utils.executor import execute_query
from db_utils.schema_utils import schema_text_from_information_schema
from text_to_sql.text_to_sql import ask_ollama
from text_to_sql.text_to_sql import build_prompt



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


def add_row_to_db(data_line: str) -> tuple[bool, str | None]:
    """
    Aggiunge o aggiorna una riga nel DB, usando insert_or_update_film.
    Restituisce (True, None) se tutto ok, (False, messaggio_errore) se fallisce.
    """
    return insert_or_update_film(data_line)


def run_sql_query(sql_query: str) -> Tuple[str, List[Dict] | None, str | None]:
    """
    Esegue una query SQL in modalità sicura e converte i risultati in formato strutturato.

    Blocca query pericolose (DROP, DELETE, UPDATE, INSERT) e gestisce eventuali errori.

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
    if "INSERT" in sql_query.upper():
        return "unsafe", None, "Operazione INSERT non permessa"

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
    Converte la domanda in SQL chiamando Ollama.
    """
    # recupera schema
    schema_text = schema_text_from_information_schema()
    if not schema_text:
        error_msg = "[ERROR] Impossibile recuperare lo schema dal database."
        print(error_msg)
        return f"SELECT NULL AS warning -- {error_msg}"
    
    prompt = build_prompt(schema_text, question)

    # delega a funzione dedicata
    return ask_ollama(prompt, model)


def call_nlp_module_retry(original_question: str, previous_sql: str, db_error: str, model: str | None = None) -> str:
    """
    Genera un prompt di retry per correggere una query SQL fallita e chiama Ollama.
    """
    schema_text = schema_text_from_information_schema()
    if not schema_text:
        error_msg = "[ERROR] Impossibile recuperare lo schema dal database."
        print(error_msg)
        return f"SELECT NULL AS warning -- {error_msg}"

    # genera il prompt 
    prompt_retry = (
        f"Domanda originale:\n{original_question}\n\n"
        f"Query SQL precedente:\n{previous_sql}\n\n"
        f"Errore dal database:\n{db_error}\n\n"
        f"Schema del database:\n{schema_text}\n\n"
        "Correggi la query  o riprova a rigenerarla e restituisci solo una query SQL valida"
    )

    # chiama Ollama con il prompt di retry
    return ask_ollama(prompt_retry, model)




