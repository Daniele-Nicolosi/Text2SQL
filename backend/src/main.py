from fastapi import FastAPI, HTTPException
from models import TableColumn, AddInput, AddOutput, SQLSearchInput, SQLSearchOutput, SearchInput, SearchOutput, SearchWithRetryOutput
from typing import List
from utils import get_schema, add_row_to_db, run_sql_query, call_nlp_module, call_nlp_module_retry

app = FastAPI()


# endpoint -- root
@app.get("/", response_model=AddOutput)
def root() -> AddOutput:
    """
    Endpoint di test/base: restituisce status ok.
    """
    return AddOutput(status="ok")


# endpoint -- schema_summary
@app.get("/schema_summary", response_model=List[TableColumn])
def schema_summary() -> List[TableColumn]:
    """
    Restituisce lo schema del database.
    """
    return get_schema()


# endpoint -- add
@app.post("/add", response_model=AddOutput)
def add(data: AddInput) -> AddOutput:
    """
    Aggiunge o aggiorna una riga nel database.
    """
    success, error_msg = add_row_to_db(data.data_line)
    if success:
        return AddOutput(status="ok")
    raise HTTPException(status_code=422, detail=error_msg)


# endpoint -- search
@app.post("/search", response_model=SearchOutput)
def search(body: SearchInput) -> SearchOutput:
    """
    Converte una domanda in SQL e restituisce i risultati.
    """
    sql_traduction = call_nlp_module(body.question, body.model)
    valid, result, _ = run_sql_query(sql_traduction)

    if valid != "valid":
        return SearchOutput(sql=sql_traduction, sql_validation=valid, results=None)
    return SearchOutput(sql=sql_traduction, sql_validation=valid, results=result)


# endpoint -- sql_search
@app.post("/sql_search", response_model=SQLSearchOutput)
def sql_search(req: SQLSearchInput) -> SQLSearchOutput:
    """
    Esegue una query SQL diretta e restituisce i risultati.
    """
    validation, results, _ = run_sql_query(req.sql_query)
    if validation != "valid":
        return SQLSearchOutput(sql_validation=validation, results=None)
    return SQLSearchOutput(sql_validation=validation, results=results)


# endpoint -- search_with_retry
@app.post("/search_with_retry", response_model=SearchWithRetryOutput)
def search_with_retry(body: SearchInput) -> SearchWithRetryOutput:
    """
    Esegue una query NLP con retry automatico in caso di errore.
    """
    sql_query = call_nlp_module(body.question, body.model)
    valid, result, error = run_sql_query(sql_query)
    if valid != "valid":
        attempt_1 = SearchOutput(sql=sql_query, sql_validation=valid, results=None)
        sql_retry = call_nlp_module_retry(body.question, sql_query, error, body.model)
        valid, result, error = run_sql_query(sql_retry)
        if valid != "valid":
            return SearchWithRetryOutput(
                attempt_1=attempt_1, 
                attempt_2=SearchOutput(sql=sql_retry, sql_validation=valid, results=None)
            )
        return SearchWithRetryOutput(
            attempt_1=attempt_1, 
            attempt_2=SearchOutput(sql=sql_retry, sql_validation=valid, results=result)
        )
    return SearchWithRetryOutput(
        attempt_1=SearchOutput(sql=sql_query, sql_validation=valid, results=result), 
        attempt_2=None
    )







