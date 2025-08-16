# Base image Python 3.11 slim
FROM python:3.11-slim

# Cartella di lavoro
WORKDIR /app

# Librerie di sistema per MariaDB e compilazione
RUN apt-get update && apt-get install -y libmariadb-dev build-essential

# Copia requirements e installa librerie Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . /app

# Comando di default
CMD ["python", "load_data.py"]

