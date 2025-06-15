FROM python:3.12.11-slim-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Dependências de sistema
RUN apt-get update && apt-get install -y curl libpq-dev && rm -rf /var/lib/apt/lists/*

# Instalação do uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Instala dependências só quando o lock muda
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project

COPY . /app/

# Faz o sync final já com o projeto copiado
RUN --mount=type=cache,target=/root/.cache/uv uv sync

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]