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
    

class ResultItem(BaseModel):
    item_type: str
    properties: List[Property]


class SearchOutput(BaseModel):
    sql: str
    sql_validation: Literal["valid", "unsafe", "invalid"]
    results: Optional[List[ResultItem]] = None


class SQLSearchOutput(BaseModel):
    sql_validation: Literal["valid", "unsafe", "invalid"]
    results: Optional[List[ResultItem]] = None
    

class SearchWithRetryOutput(BaseModel):
    attempt_1: SearchOutput
    attempt_2: Optional[SearchOutput] = None