from pydantic import BaseModel
from typing import Optional, List, Any, Literal

class TableColumn(BaseModel):
    table_name: str
    table_column: str

class AddInput(BaseModel):
    data_line: str

class AddOutput(BaseModel):
    status: str

class SQLSearchInput(BaseModel):
    sql_query: str



class SearchInput(BaseModel):
    question: str
    model: Optional[str] = None


class Property(BaseModel):
    property_name: str
    property_value: Any
    # devo considerare null ??? SI


class ResultItem(BaseModel):
    item_type: str
    properties: List[Property]


class SearchOutput(BaseModel):
    sql: str
    sql_validation: Literal["valid", "unsafe", "invalid"]
    results: Optional[List[ResultItem]] = None
    #modelli pydantic che vengono annidati



class SQLSearchOutput(BaseModel):
    sql_validation: Literal["valid", "unsafe", "invalid"]
    results: Optional[List[ResultItem]] = None
    #in realtà vedi se al posto di ResultItem ci devi mettere 
    #un altra classe per la validazione 
    #in quanto dice lo stesso formato dell esonero ma non so sicuro


class SearchWithRetryOutput(BaseModel):
    attempt_1: SearchOutput
    attempt_2: Optional[SearchOutput] = None