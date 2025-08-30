FROM ollama/ollama:latest

USER root

# Aggiorna pacchetti e installa curl + certificati
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copia script di start e rendilo eseguibile
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Imposta lo script come entrypoint
ENTRYPOINT ["/start.sh"]
