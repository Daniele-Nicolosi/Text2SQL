from models import TableColumn
from typing import List, Dict, Tuple

def get_schema() -> list[TableColumn]:
    """funzione di supporto solo per vedere il
    funzionamento(dati alla cazzo di cane)"""
    return [
        TableColumn(table_name="movies", table_column="id"),
        TableColumn(table_name="movies", table_column="nome")
    ]


def add_row_to_db(data_line: str) -> bool:
    """
    Stub: aggiunge o aggiorna una riga nel DB.
    In futuro chiamerà il modulo DB dello studente C.
    """
    print(f"[DEBUG] Riga ricevuta: {data_line}")
    # Simuliamo che l'operazione sia sempre ok
    return True


def run_sql_query(sql_query: str) -> Tuple[str, List[Dict] | None, str | None]:
    """"
    Stub: esegue la query SQL e restituisce una lista di dizionari.
    In futuro invocherà il modulo DB dello studente C
    """
    if "DROP" in sql_query.upper():
        return "unsafe", None, "Operazione pericolosa: DROP trovato"
    if "colonna_sbagliata" in sql_query.lower():
        return "invalid", None, "Colonna 'colonna_sbagliata' non trovata"
    
    #esempio di risultato valido
    return "valid",  [
        {
            "item_type": "Penne",
            "properties": [
                {"property_name":"nome", "property_value":"Penna"},
                {"property_name":"prezzo", "property_value": 1.5}
            ]
        }
    ],None


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

