# iOSLENS.ai — Production Container
# Multi-stage: deps → build → api/mcp targets

# ─ Stage 1: Dependencies ─
FROM python:3.12-slim AS deps
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─ Stage 2: API Target ─
FROM deps AS api
COPY src/ ./src/
ENV PYTHONPATH=/app/src
ENV APP_MODULE=ioslens.main:app
EXPOSE 8000
CMD ["uvicorn", "ioslens.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

# ─ Stage 3: MCP Server Target ─
FROM deps AS mcp
COPY src/ ./src/
ENV PYTHONPATH=/app/src
EXPOSE 8001
CMD ["python", "-m", "ioslens.mcp.server"]
