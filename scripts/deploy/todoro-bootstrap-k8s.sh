#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KUBECTL_BIN="${KUBECTL_BIN:-sudo k3s kubectl}"
NAMESPACE="todoro"
IMAGE_OWNER="${TODORO_IMAGE_OWNER:-mattoyuzuru}"
IMAGE_TAG="${TODORO_IMAGE_TAG:-edge}"
FRONTEND_IMAGE="ghcr.io/${IMAGE_OWNER}/todoro/frontend:${IMAGE_TAG}"
BACKEND_IMAGE="ghcr.io/${IMAGE_OWNER}/todoro/backend:${IMAGE_TAG}"

POSTGRES_USER="${TODORO_POSTGRES_USER:-todoro}"
POSTGRES_DB="${TODORO_POSTGRES_DB:-todoro}"
POSTGRES_PASSWORD="${TODORO_POSTGRES_PASSWORD:-}"
SECRET_KEY="${TODORO_SECRET_KEY:-}"
ACCESS_TOKEN_EXPIRE_MINUTES="${TODORO_ACCESS_TOKEN_EXPIRE_MINUTES:-4320}"
TIME_ZONE="${TODORO_TIME_ZONE:-Europe/Moscow}"
APP_HOST="${TODORO_APP_HOST:-https://todo.keykomi.com}"
API_HOST="${TODORO_API_HOST:-https://api.todo.keykomi.com}"

if ! ${KUBECTL_BIN} get namespace "${NAMESPACE}" >/dev/null 2>&1; then
  ${KUBECTL_BIN} apply -f "${ROOT_DIR}/k8s/todoro/namespace.yaml"
fi

if ${KUBECTL_BIN} -n "${NAMESPACE}" get secret todoro-secrets >/dev/null 2>&1; then
  echo "Secret todoro-secrets already exists in namespace ${NAMESPACE}, reusing it."
else
  if [[ -z "${POSTGRES_PASSWORD}" ]]; then
    POSTGRES_PASSWORD="$(openssl rand -hex 24)"
  fi

  if [[ -z "${SECRET_KEY}" ]]; then
    SECRET_KEY="$(openssl rand -hex 32)"
  fi

  DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"
  CORS_ORIGINS="${TODORO_CORS_ORIGINS:-${APP_HOST},${API_HOST}}"

  ${KUBECTL_BIN} -n "${NAMESPACE}" create secret generic todoro-secrets \
    --from-literal=postgres-user="${POSTGRES_USER}" \
    --from-literal=postgres-password="${POSTGRES_PASSWORD}" \
    --from-literal=postgres-db="${POSTGRES_DB}" \
    --from-literal=database-url="${DATABASE_URL}" \
    --from-literal=secret-key="${SECRET_KEY}" \
    --from-literal=access-token-expire-minutes="${ACCESS_TOKEN_EXPIRE_MINUTES}" \
    --from-literal=time-zone="${TIME_ZONE}" \
    --from-literal=cors-origins="${CORS_ORIGINS}" \
    --dry-run=client \
    -o yaml | ${KUBECTL_BIN} apply -f -
fi

${KUBECTL_BIN} apply -k "${ROOT_DIR}/k8s/todoro"
${KUBECTL_BIN} -n "${NAMESPACE}" set image deployment/backend backend="${BACKEND_IMAGE}"
${KUBECTL_BIN} -n "${NAMESPACE}" set image deployment/frontend frontend="${FRONTEND_IMAGE}"

${KUBECTL_BIN} -n "${NAMESPACE}" rollout status statefulset/postgres --timeout=180s
${KUBECTL_BIN} -n "${NAMESPACE}" rollout status statefulset/redis --timeout=180s
${KUBECTL_BIN} -n "${NAMESPACE}" rollout status deployment/backend --timeout=180s
${KUBECTL_BIN} -n "${NAMESPACE}" rollout status deployment/frontend --timeout=180s
${KUBECTL_BIN} -n "${NAMESPACE}" get ingress,svc,pods
