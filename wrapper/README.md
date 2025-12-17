# Docker dev wrapper

This directory keeps the Docker + Python wrapper isolated from the main app code. The container runs the Node development server through `wrapper/run_dev.py`, which installs dependencies if needed and forwards signals cleanly.

## Build the image

```bash
docker build -f wrapper/Dockerfile -t fhir-query-dev .
```

## Run the dev server

```bash
# start using the source baked into the image
docker run --rm -it -p 5000:5000 fhir-query-dev

# optional: live-reload against your working tree
docker run --rm -it -p 5000:5000 \
  -v "$(pwd)":/app \
  -v fhir-query-node-modules:/app/node_modules \
  fhir-query-dev
```

The server listens on `PORT` (default `5000`) and binds to `0.0.0.0` so it is reachable from the host at `http://localhost:5000`.

## Useful environment variables

- `PORT` (default `5000`)
- `HOST` (default `0.0.0.0`)
- `NODE_ENV` (default `development`)
- `CHOKIDAR_USEPOLLING` (default `true` to make file watching work with bind mounts)
- `SKIP_INSTALL` (set to `1` to skip `npm install` on start)
- `FORCE_INSTALL` (set to `1` to force a clean reinstall on start)
