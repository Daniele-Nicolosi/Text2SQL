from models import TableColumn, Property, ResultItem
from typing import List, Dict, Tuple
from db_utils.crud import insert_or_update_film
from db_utils.executor import execute_query
from db_utils.schema_utils import schema_text_from_information_schema
from text_to_sql.text_to_sql import build_prompt, ask_ollama


def get_schema() -> list[TableColumn]:
    """
    Recupera lo schema del database come lista di TableColumn.
    """
    sql = """
        SELECT TABLE_NAME AS table_name, COLUMN_NAME AS table_column
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    ok, rows, err = execute_query(sql)
    if not ok:
        print(f"[ERRORE] Query fallita su information_schema: {err}")
        return []

    # Converte le righe in oggetti TableColumn
    return [TableColumn(table_name=r["table_name"], table_column=r["table_column"]) for r in rows]


def add_row_to_db(data_line: str) -> tuple[bool, str | None]:
    """
    Aggiunge o aggiorna una riga nel DB.
    Restituisce (True, None) se ok, (False, messaggio_errore) se fallisce.
    """
    return insert_or_update_film(data_line)


def run_sql_query(sql_query: str) -> Tuple[str, List[Dict] | None, str | None]:
    """
    Esegue una query SQL sicura e converte i risultati in formato strutturato.

    Blocca query pericolose (DROP, DELETE, UPDATE, INSERT).

    Returns:
        Tuple[str, List[Dict] | None, str | None]:
            - stato: "valid", "invalid" o "unsafe"
            - results: lista di ResultItem oppure None
            - error: messaggio di errore se presente
    """
    # Sicurezza: blocco query pericolose
    for keyword in ("DROP", "DELETE", "UPDATE", "INSERT"):
        if keyword in sql_query.upper():
            return "unsafe", None, f"Operazione {keyword} non permessa"

    # Esecuzione query
    success, rows, error = execute_query(sql_query)
    if not success:
        return "invalid", None, error

    results: List[Dict] = []
    table_name = "film"

    # Conversione risultati in ResultItem
    for row in rows:
        props = []
        for k, v in row.items():
            props.append(Property(property_name="name" if k == "titolo" else k, property_value=v))
        results.append(ResultItem(item_type=table_name, properties=props).dict())

    return "valid", results, None


def call_nlp_module(question: str, model: str | None = None) -> str:
    """
    Converte una domanda in query SQL usando Ollama.
    """
    schema_text = schema_text_from_information_schema()
    if not schema_text:
        error_msg = "[ERROR] Impossibile recuperare lo schema dal database."
        print(error_msg)
        return f"SELECT NULL AS warning -- {error_msg}"
    
    prompt = build_prompt(schema_text, question)
    return ask_ollama(prompt, model)


def call_nlp_module_retry(original_question: str, previous_sql: str, db_error: str, model: str | None = None) -> str:
    """
    Corregge una query SQL fallita generando un prompt di retry per Ollama.
    """
    schema_text = schema_text_from_information_schema()
    if not schema_text:
        error_msg = "[ERROR] Impossibile recuperare lo schema dal database."
        print(error_msg)
        return f"SELECT NULL AS warning -- {error_msg}"

    prompt_retry = (
        f"Domanda originale:\n{original_question}\n\n"
        f"Query SQL precedente:\n{previous_sql}\n\n"
        f"Errore dal database:\n{db_error}\n\n"
        f"Schema del database:\n{schema_text}\n\n"
        "Correggi la query o riprova a rigenerarla e restituisci solo una query SQL valida"
    )

    return ask_ollama(prompt_retry, model)





