# ==========================================
# BramTech VTU - Django Application
# ==========================================
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    DJANGO_SETTINGS_MODULE=config.settings.dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 django && useradd -u 1000 -g django -m django

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ /app/
COPY start.sh /start.sh
RUN chmod +x /start.sh && chown -R django:django /app /start.sh

USER django

EXPOSE 8000

CMD ["/start.sh"]
