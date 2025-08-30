FROM python:3.11-slim

WORKDIR /app

# Installa le dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'app
COPY . .

# Espone la porta del frontend
EXPOSE 8004

# Avvia l'app con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004", "--app-dir", "src"]

