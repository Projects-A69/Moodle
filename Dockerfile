FROM python:3.12-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
 && pip install uv

WORKDIR /app

COPY pyproject.toml pyproject.lock* ./

ENV UV_USE_VENV=0
RUN uv sync

COPY . .

FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

WORKDIR /app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]