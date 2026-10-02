#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INFRA_DIR="${REPO_ROOT}/infra"
BACKEND_URL="azblob://pulumi-state?storage_account=rapstate18c845ca"
IMAGE_REPOSITORY="research-analysis"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

for command_name in az docker git pulumi; do
  require_command "${command_name}"
done

if [[ ! -x "${INFRA_DIR}/.venv/bin/python" ]]; then
  echo "Infrastructure virtual environment not found at infra/.venv." >&2
  echo "Create it and install infra/requirements.txt before deploying." >&2
  exit 1
fi

if [[ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]]; then
  echo "Refusing to publish an image from a dirty working tree." >&2
  exit 1
fi

IMAGE_TAG="$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"

echo "Verifying Azure authentication..."
az account show --output none

echo "Selecting the Azure Blob Pulumi backend and DEV stack..."
pulumi login "${BACKEND_URL}"
pulumi -C "${INFRA_DIR}" stack select dev

echo "Previewing DEV infrastructure..."
pulumi -C "${INFRA_DIR}" preview --stack dev --non-interactive --diff

echo "Applying DEV infrastructure..."
pulumi -C "${INFRA_DIR}" up --stack dev --yes --non-interactive --diff

REGISTRY_NAME="$(pulumi -C "${INFRA_DIR}" stack output registryName)"
REGISTRY_SERVER="$(pulumi -C "${INFRA_DIR}" stack output registryLoginServer)"
LOCAL_IMAGE="${IMAGE_REPOSITORY}:${IMAGE_TAG}"
REMOTE_IMAGE="${REGISTRY_SERVER}/${IMAGE_REPOSITORY}:${IMAGE_TAG}"

echo "Building ${LOCAL_IMAGE}..."
docker build \
  --platform linux/amd64 \
  --tag "${LOCAL_IMAGE}" \
  "${REPO_ROOT}/app"

echo "Authenticating to ${REGISTRY_NAME} with the current Azure identity..."
az acr login --name "${REGISTRY_NAME}"

echo "Publishing ${REMOTE_IMAGE}..."
docker tag "${LOCAL_IMAGE}" "${REMOTE_IMAGE}"
docker push "${REMOTE_IMAGE}"

echo "Verifying the published tag..."
az acr repository show-tags \
  --name "${REGISTRY_NAME}" \
  --repository "${IMAGE_REPOSITORY}" \
  --query "[?name=='${IMAGE_TAG}'].{tag:name,digest:digest}" \
  --output table

echo "Deployment complete."
echo "Registry: ${REGISTRY_SERVER}"
echo "Image: ${REMOTE_IMAGE}"
