# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.5 AS uv

FROM python:3.13-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev
COPY . .
RUN DEBUG=1 .venv/bin/python manage.py collectstatic --noinput

FROM python:3.13-slim
LABEL org.opencontainers.image.source="https://github.com/101t/django-lms" \
      org.opencontainers.image.description="Django LMS — a lightweight, self-hosted learning management system"
RUN useradd --create-home --uid 1000 lms
WORKDIR /app
COPY --from=build --chown=lms:lms /app /app
RUN mkdir -p /app/media && chown lms:lms /app/media
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 MEDIA_ROOT=/app/media
USER lms
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/')" || exit 1
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]
