import re
import os
import json
import requests

def build_prompt(schema_text: str, question: str) -> str:
    """
    Costruisce un prompt per il modello Ollama in italiano.
    Regole:
    - Solo SELECT o CTE WITH + SELECT.
    - Usa esclusivamente tabelle/colonne presenti nello schema.
    - Nessuna spiegazione, solo SQL.
    """

    return (
        "Sei un assistente Text-to-SQL per MariaDB.\n"
        "Regole IMPORTANTI:\n"
        "- Genera SOLO UNA query SQL, SOLO SELECT (o CTE WITH + SELECT) e nulla più.\n"
        "- NON usare INSERT/UPDATE/DELETE/CREATE/ALTER/DROP/TRUNCATE/REPLACE/GRANT.\n"
        "- Usa solo tabelle e colonne presenti nello schema.\n"
        "- Niente spiegazioni o commenti: restituisci solo SQL.\n"
        "SCHEMA DEL DATABASE:\n"
        f"{schema_text}\n\n"
        "DOMANDA UTENTE:\n"
        f"{question}\n\n"
        "Rispondi con SOLO il codice SQL (senza backtick)."
    )

def _sanitize_sql(sql: str) -> str:
    """
    Sanifica l'output LLM per garantire sicurezza:
    - Rimuove backtick/fence Markdown.
    - Isola da WITH/SELECT in avanti.
    - Limita a una sola istruzione.
    - Blocca keyword pericolose (INSERT/UPDATE/...).
    - Se non inizia con SELECT/WITH, ritorna fallback sicuro.
    Restituisce sempre una query SELECT valida (o un fallback).
    """

    s = sql.strip()

    # rimuovi fence tipo ```sql ... ``` o ```
    s = re.sub(r"^```(?:sql)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)

    # conserva da WITH/SELECT in poi
    m = re.search(r"(?is)\b(with|select)\b.*", s)
    if m:
        s = m.group(0).strip()

    # una sola istruzione
    if ";" in s:
        s = s.split(";", 1)[0].strip()

    # blocco keyword pericolose
    forbidden = ("insert", "update", "delete", "drop", "alter", "create", "truncate", "replace", "grant")
    if any(kw in s.lower() for kw in forbidden):
        return "SELECT NULL AS warning -- [ERROR] Query contiene keyword pericolose"

    # SELECT-only enforcement
    if not (s.lower().startswith("select") or s.lower().startswith("with")):
        s = "SELECT NULL AS warning -- [ERROR] Query non valida, fallback sicuro"

    return s

def ask_ollama(prompt : str, model: str | None = None) -> str:
    """
    Interroga Ollama via API REST (/api/chat).
    - Usa modello indicato o default 'gemma3:1b-it-qat'.
    - Host configurabile via env OLLAMA_HOST (default: http://ollama:11434).
    - Restituisce una query SQL SELECT (sanificata con _sanitize_sql).
    """
    
    # setup modello
    default_model = "gemma3:1b-it-qat"
    use_model = (model or "").strip() or default_model

    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
    url = f"{ollama_host}/api/chat"

    payload = {
        "model": use_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        resp = requests.post(
            url,
            data=json.dumps(payload),
            timeout=120,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()

        # estrazione SQL
        raw = data.get("message", {}).get("content", "") or ""
        sql = _sanitize_sql(raw)
        return sql if sql else "SELECT NULL AS warning -- [ERROR] Output vuoto"
    except Exception as e:
        print(f"[DEBUG] Errore in ask_ollama: {e}")
        return f"SELECT NULL AS warning -- [ERROR] {e}"
