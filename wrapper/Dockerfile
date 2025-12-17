FROM node:20-bullseye-slim

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    git \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Bring in the rest of the source
COPY . .

ENV PYTHONUNBUFFERED=1 \
    NODE_ENV=development \
    HOST=0.0.0.0 \
    PORT=5000 \
    CHOKIDAR_USEPOLLING=true \
    WATCHPACK_POLLING=true \
    BROWSER=none

EXPOSE 5000

CMD ["python3", "/app/wrapper/run_dev.py"]
