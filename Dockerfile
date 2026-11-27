# Arivo — the reproducible runtime image (Workstream 10; runtime-neutral: any host
# that runs Linux containers — the Cloudflare Tunnel front, a VPS, or a local daemon).
# Two start commands (the directive's letter): `api` (uvicorn, :8080) and `worker`
# (the durable worker loop); plus `migrate` (the release command — the same oracle
# the CI uses).
FROM python:3.12-slim AS base
# the pg client binaries (the worker's adapter shells out to psql; the migrate
# oracle and the kernel's read arms use it too)
RUN apt-get update && apt-get install -y --no-install-recommends \
        postgresql-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY harness/api/requirements.lock /app/harness/api/requirements.lock
RUN pip install --no-cache-dir -r harness/api/requirements.lock
COPY . /app
# the non-root user (the container's own boundary; never root in the runtime)
RUN useradd -m -u 10001 arivo && chown -R arivo /app
USER arivo
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
# the health endpoints: /health/live (the liveness) + /health/ready (the readiness:
# the DB reachable + the auth state declared)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/health/live', timeout=4)" || exit 1
CMD ["python3", "-m", "harness.api"]
