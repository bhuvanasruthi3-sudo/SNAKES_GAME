# Browser Snake game — deploy to Render, Railway, Fly.io, or any Docker host
FROM python:3.12-slim-bookworm

WORKDIR /app

# App files only (see .dockerignore)
COPY server.py .
COPY web/ ./web/

# Render sets PORT at runtime (default 10000 for local runs)
ENV PORT=10000
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"10000\")}/')" || exit 1

CMD ["python", "server.py"]
