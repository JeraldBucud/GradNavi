# Build context: repository root. Railway staging Root Directory must be "/".
# Keep Django at /app so the existing /app/media Railway volume still works.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/

# These are the approved, version-controlled reference files only.
# Both existing importers derive repository root as / from /app/careers/...
COPY data/reference/curated/ /data/reference/curated/
COPY data/reference/mappings/ /data/reference/mappings/
COPY data/reference/gradnavi_interests/v1/ /data/reference/gradnavi_interests/v1/
COPY data/reference/snapshots/onet_api_v2_in_demand/2026-09-16/ /data/reference/snapshots/onet_api_v2_in_demand/2026-09-16/

# Fail the build when required import input is missing.
RUN test -f /data/reference/curated/source_manifest.csv \
 && test -f /data/reference/curated/careers.csv \
 && test -f /data/reference/mappings/onet_mappings.csv \
 && test -f /data/reference/gradnavi_interests/v1/interest_catalogue.csv \
 && test -f /data/reference/gradnavi_interests/v1/career_interest_mappings.csv \
 && test -f /data/reference/snapshots/onet_api_v2_in_demand/2026-09-16/snapshot_manifest.json

CMD ["sh", "-c", "exec gunicorn gradnavi.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
