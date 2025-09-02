FROM ollama/ollama
WORKDIR /root

RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Disable ollama’s default entrypoint and use our script
ENTRYPOINT ["/bin/sh", "-c", "\
  if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi; else echo 'Warning: NVIDIA GPU not detected'; fi && \
  ollama serve & \
  while ! nc -z localhost 11434; do sleep 1; done && \
  ollama pull deepseek-r1:7b && \
  wait \
"]
