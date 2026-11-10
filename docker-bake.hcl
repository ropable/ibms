# docker-bake.hcl — reproducible, multi-arch build config.
# Build (local, native platform, loaded into Docker): docker buildx bake local
# Build + push (multi-arch):                          docker buildx bake --push app
# Override at runtime:   TAG=v2 IMAGE=ghcr.io/me/ibms docker buildx bake local
# Override the base tag: PYTHON_VERSION=3.14 docker buildx bake local
# CI builds the "ci" target (see .github/workflows/multi-build.yml).

variable "IMAGE" {
  description = "Fully-qualified image name, without the tag."
  default     = "ghcr.io/dbca-wa/ibms"
}

variable "TAG" {
  description = "Tag applied to the built image."
  default     = "latest"
}

variable "PYTHON_VERSION" {
  description = "dhi.io/python image tag used by the Dockerfile."
  default     = "3.13-debian13-dev"
}

variable "PLATFORMS" {
  description = "Platforms used by the multi-arch targets."
  type        = list(string)
  default     = ["linux/amd64", "linux/arm64"]
}

group "default" {
  targets = ["app"]
}

# What to build. Exporter, cache and attestation policy belong to the targets
# that consume this, so local builds don't inherit CI-only behaviour.
target "_base" {
  context    = "."
  dockerfile = "Dockerfile"
  args       = { PYTHON_VERSION = PYTHON_VERSION }
}

# Multi-arch image for the registry (manual release push or CI).
target "app" {
  inherits  = ["_base"]
  tags      = ["${IMAGE}:${TAG}"]
  platforms = PLATFORMS
  # Only attached on push; the docker exporter ignores these.
  attest    = ["type=provenance,mode=max", "type=sbom"]
}

# CI-only: GitHub Actions cache, and always refresh base images so the
# scheduled rebuild actually picks up upstream security fixes.
target "ci" {
  inherits   = ["app"]
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
  pull       = true
}

# Local development: native platform, loaded straight into Docker.
target "local" {
  inherits = ["_base"]
  tags     = ["${IMAGE}:local"]
  output   = ["type=docker"]
}
