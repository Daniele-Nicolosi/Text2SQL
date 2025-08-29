FROM ollama/ollama:latest

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copia lo script di start
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Usa lo script come entrypoint
ENTRYPOINT ["/start.sh"]