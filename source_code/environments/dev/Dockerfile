# Dockerfile
FROM python:3.13-slim as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Git configuration
RUN git config --global url."https://".insteadOf git:// && \
    git config --global url."https://".insteadOf ssh://git@

FROM base as builder

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

RUN mkdir -p /app/webapp

WORKDIR /app/webapp

# Poetry 파일 복사 및 의존성 설치
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

# 애플리케이션 코드 복사
COPY ./webapp /app/webapp

# shell script 복사
COPY ./environments/dev/start-webapp.sh /start-webapp.sh
RUN chmod +x /start-webapp.sh

EXPOSE ${PORT}
