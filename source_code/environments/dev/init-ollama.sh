#!/bin/sh

# Start Ollama server in the background
ollama serve &

# Wait for the server to start
sleep 10

ollama pull qwen3:0.6b

# Keep the container running
wait
