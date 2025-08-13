FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libmariadb-dev build-essential

COPY . /app

RUN pip install mariadb

CMD ["python", "load_data.py"]