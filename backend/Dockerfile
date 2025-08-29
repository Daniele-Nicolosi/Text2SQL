FROM python:3.11-slim

# Evita la creazione di file .pyc e disabilita buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la cartella di lavoro
WORKDIR /app
ENV PYTHONPATH="${PYTHONPATH}:/app/db_utils:/app/text_to_sql"


# Installa dipendenze di sistema necessarie per mariadb
RUN apt-get update && apt-get install -y libmariadb-dev build-essential curl && rm -rf /var/lib/apt/lists/*

# Copia e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente
COPY src/ ./src/

# Espone la porta dell'applicazione
EXPOSE 8003  

# Avvia l'app FastAPI tramite uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--app-dir", "src"]





