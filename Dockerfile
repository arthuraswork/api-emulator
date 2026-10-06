FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PORT=9312
ENV HOST='0.0.0.0'

COPY pyproject.toml uv.lock ./

RUN uv sync --no-install-project --no-dev --frozen

COPY . .

EXPOSE 9312
CMD ["uv", "run", "python", "main.py"]