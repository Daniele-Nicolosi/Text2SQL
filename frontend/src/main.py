import os
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---- Config ----
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8003").rstrip("/")

app = FastAPI()

# Static (opzionale, se vuoi mettere CSS in /frontend/static)
static_dir = Path(__file__).resolve().parents[1] / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates_dir = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# ---------------- UI ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
def ui_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/schema_summary", response_class=HTMLResponse)
def ui_schema_summary(request: Request):
    try:
        r = requests.get(f"{BACKEND_URL}/schema_summary", timeout=30)
        r.raise_for_status()
        schema = r.json()
    except Exception as e:
        schema = None
        error = f"Errore nel recupero dello schema: {e}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error})

    return templates.TemplateResponse("index.html", {"request": request, "schema": schema})


@app.post("/search", response_class=HTMLResponse)
def ui_search(request: Request,
              question: str = Form(...),
              model: Optional[str] = Form(None)):
    payload = {"question": question, "model": model or None}
    try:
        r = requests.post(f"{BACKEND_URL}/search", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        search = {
            "sql": data.get("sql"),
            "sql_validation": data.get("sql_validation"),
            "results": data.get("results")
        }
    except Exception as e:
        search = None
        error = f"Errore nella richiesta /search: {e}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error, "question": question, "model": model})

    ctx = {"request": request, "search": search, "question": question, "model": model}
    return templates.TemplateResponse("index.html", ctx)


@app.post("/search_with_retry", response_class=HTMLResponse)
def ui_search_with_retry(request: Request,
                         question: str = Form(...),
                         model: Optional[str] = Form(None)):
    payload = {"question": question, "model": model or None}
    try:
        r = requests.post(f"{BACKEND_URL}/search_with_retry", json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
        s1 = data.get("attempt_1")
        s2 = data.get("attempt_2")
        search_with_retry = {
            "attempt_1": s1,
            "attempt_2": s2
        }
    except Exception as e:
        search_with_retry = None
        error = f"Errore nella richiesta /search_with_retry: {e}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error, "question_retry": question, "model_retry": model})

    ctx = {"request": request, "search_with_retry": search_with_retry, "question_retry": question, "model_retry": model}
    return templates.TemplateResponse("index.html", ctx)


@app.post("/sql_search", response_class=HTMLResponse)
def ui_sql_search(request: Request, sql_query: str = Form(...)):
    payload = {"sql_query": sql_query}
    try:
        r = requests.post(f"{BACKEND_URL}/sql_search", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        sql_search = {
            "sql_validation": data.get("sql_validation"),
            "results": data.get("results")
        }
    except Exception as e:
        sql_search = None
        error = f"Errore nella richiesta /sql_search: {e}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error, "sql_query": sql_query})

    ctx = {"request": request, "sql_search": sql_search, "sql_query": sql_query}
    return templates.TemplateResponse("index.html", ctx)


@app.post("/add", response_class=HTMLResponse)
def ui_add(request: Request, data_line: str = Form(...)):
    payload = {"data_line": data_line}
    try:
        r = requests.post(f"{BACKEND_URL}/add", json=payload, timeout=60)
        r.raise_for_status()
        status = (r.json() or {}).get("status", "error")
    except Exception as e:
        status = "error"
        return templates.TemplateResponse("index.html", {"request": request, "add_status": status, "add_input": data_line, "error": f"Errore /add: {e}"})

    return templates.TemplateResponse("index.html", {"request": request, "add_status": status, "add_input": data_line})
