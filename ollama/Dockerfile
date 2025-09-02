# Use the official Ollama image as the base
FROM ollama/ollama

# Set the working directory
WORKDIR /root

# Install curl and netcat (nc) for readiness check
RUN apt-get update && apt-get install -y curl netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy the entrypoint script
COPY entrypoint.sh /root/entrypoint.sh

# Give execute permissions to the script
RUN chmod +x /root/entrypoint.sh

# Ensure the script is executed properly
ENTRYPOINT ["/bin/sh", "/root/entrypoint.sh"]
