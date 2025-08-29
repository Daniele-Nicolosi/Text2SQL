#!/bin/bash
set -e

# Avvia Ollama in background
ollama serve &
OLLAMA_PID=$!

# Attendi che Ollama risponda
until curl -fsS http://localhost:11434/v1/models -o /dev/null; do
    echo "Attendo Ollama..."
    sleep 2
done

# Lista modelli da scaricare (usando l’API HTTP)
MODELS=("gemma3:1b-it-qat" "gemma3:1b-it-q4_K_M")

for model in "${MODELS[@]}"; do
    if curl -fsS http://localhost:11434/api/tags | grep -q "$model"; then
        echo "Modello $model già presente, salto download"
    else
        echo "Scarico modello $model..."
        curl -fsS -X POST http://localhost:11434/api/pull \
            -d "{\"model\": \"$model\"}"
    fi
done


# Tieni Ollama in foreground
wait $OLLAMA_PID



