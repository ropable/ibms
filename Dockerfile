# syntax=docker/dockerfile:1
FROM dhi.io/python:3.13-debian13-dev AS build-stage

# Install system packages required to install the project
RUN apt-get update -y \
  # Python package dependencies: gunicorn_h1c requires gcc
  && apt-get install -y --no-install-recommends gcc g++ \
  # Run shared library linker after installing packages
  && ldconfig \
  && rm -rf /var/lib/apt/lists/*

# Copy and configure uv, to install dependencies
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/
WORKDIR /app
# Install project dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group dev --link-mode=copy --compile-bytecode --no-python-downloads --frozen \
  # Remove uv and lockfile after use
  && rm -rf /bin/uv \
  && rm uv.lock

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Copy the remaining project files to finish building the project
COPY gunicorn.py manage.py ./
COPY ibms_project ./ibms_project
COPY ibms ./ibms
COPY sfm ./sfm
# Compile scripts and collect static files
RUN python -m compileall ibms_project \
  && python manage.py collectstatic --noinput

##################################################################################

FROM dhi.io/python:3.13-debian13 AS runtime-stage
LABEL org.opencontainers.image.authors=asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source=https://github.com/dbca-wa/ibms

# Copy over the built project and virtualenv
WORKDIR /app
COPY --from=build-stage /app /app

# Image runs as the nonroot user
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.py"]
