#!/bin/sh

# Ensure GPU is available
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "Warning: NVIDIA GPU not detected"
fi

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready before pulling the model
while ! nc -z localhost 11434; do
  sleep 1
done

# Pull the correct model
ollama pull deepseek-r1:7b

# Keep the container running
wait
