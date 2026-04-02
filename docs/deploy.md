# Deploy

## Что добавлено в репозиторий

- GitHub Actions workflow: `.github/workflows/ci-cd.yml`
- Kubernetes-манифесты: `k8s/todoro/`
- Bootstrap-скрипт: `scripts/deploy/todoro-bootstrap-k8s.sh`

## GHCR-образы

- `ghcr.io/mattoyuzuru/todoro/backend`
- `ghcr.io/mattoyuzuru/todoro/frontend`

Workflow публикует теги:
- `sha-<short-sha>` для каждого push
- `branch-<branch-name>` для push в ветки
- `edge` для default branch
- `main` для default branch

Для production frontend workflow по умолчанию запекает:

- `VITE_API_BASE_URL=https://api.todo.keykomi.com`

Если нужен другой URL API, можно задать GitHub variable `PROD_API_BASE_URL`.

## Что важно для VPS

- Деплой идет только в namespace `todoro`.
- Чужие namespace-ы, pod'ы и ingress'ы не трогаются.
- Скрипт не перезапускает `traefik`, `cert-manager` и любые чужие deployment'ы.

## Доменная схема

- `https://todo.keykomi.com` — frontend
- `https://api.todo.keykomi.com` — backend API

Для этого на DNS должны смотреть оба host на тот же VPS / ingress-controller.

## Первый deploy на сервер

```bash
ssh -i ~/sshKeysDir/id_ed25519_hse matto@158.160.66.87
cd /opt
sudo mkdir -p /opt/todoro
sudo chown matto:matto /opt/todoro
git clone git@github.com:MattoYuzuru/Todoro.git /opt/todoro || true
cd /opt/todoro
git fetch --all --prune
git checkout main
git pull --ff-only
sudo TODORO_IMAGE_TAG=edge ./scripts/deploy/todoro-bootstrap-k8s.sh
```

## Обычный rollout после merge в `main`

```bash
ssh -tt -i ~/sshKeysDir/id_ed25519_hse matto@158.160.66.87 '
set -euo pipefail
cd /opt/todoro
sudo -v
sudo git fetch --all --prune
sudo git checkout main
sudo git pull --ff-only
sudo TODORO_IMAGE_TAG=edge ./scripts/deploy/todoro-bootstrap-k8s.sh
sudo k3s kubectl -n todoro rollout restart deployment/backend deployment/frontend
sudo k3s kubectl -n todoro rollout status deployment/backend --timeout=180s
sudo k3s kubectl -n todoro rollout status deployment/frontend --timeout=180s
sudo k3s kubectl -n todoro get ingress,svc,pods
'
```

Если нужно развернуть конкретный сборочный тег:

```bash
sudo TODORO_IMAGE_TAG=sha-<short-sha> ./scripts/deploy/todoro-bootstrap-k8s.sh
```

## Что делает bootstrap-скрипт

- создает namespace `todoro`, если его нет;
- создает secret `todoro-secrets`, если его нет;
- применяет манифесты из `k8s/todoro`;
- обновляет образы backend/frontend на нужный GHCR-tag;
- ждет rollout `postgres`, `redis`, `backend`, `frontend`;
- показывает итоговое состояние ingress/service/pods.

Если `todoro-secrets` уже существует, скрипт его переиспользует и не перетирает случайно пароли и `SECRET_KEY`.

## Проверка после rollout

```bash
sudo k3s kubectl get ingress,svc,pods -n todoro
sudo k3s kubectl get certificate -n todoro
curl -I https://todo.keykomi.com
curl -I https://api.todo.keykomi.com/healthz
```

## Важное замечание про GHCR

Если пакеты GHCR оставлены приватными, `k3s` не сможет их скачать без `imagePullSecret`.
Самый простой вариант для этого проекта — сделать пакеты `ghcr.io/mattoyuzuru/todoro/*` публичными.
