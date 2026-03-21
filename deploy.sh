#!/bin/bash
# Deploy script para VPS - Top Agenda Instagram Bot (Docker Swarm + Traefik)
# Executar na VPS como root:  bash deploy.sh
#
# Primeira vez: crie o .env na VPS antes de rodar:
#   cp .env.example .env && nano .env

set -e

REPO="https://github.com/decopt/themis-office.git"
DIR="/opt/topagenda"
STACK="topagenda"

echo "=========================================="
echo "  Top Agenda - Deploy (Swarm + Traefik)"
echo "=========================================="

# ── Garante que o diretorio existe e esta atualizado ───────────
if [ -d "$DIR/.git" ]; then
    echo "[1/4] Atualizando repositorio..."
    cd "$DIR"
    git pull origin main
else
    echo "[1/4] Clonando repositorio..."
    git clone "$REPO" "$DIR"
    cd "$DIR"
fi

# ── Cria .env se nao existir ───────────────────────────────────
if [ ! -f "$DIR/.env" ]; then
    cp "$DIR/.env.example" "$DIR/.env"
    echo ""
    echo "  ATENCAO: Configure o .env antes de continuar!"
    echo "  nano $DIR/.env"
    echo ""
    exit 1
fi

# ── Garante que a rede traefik-public existe ───────────────────
docker network ls | grep -q "traefik-public" || \
    docker network create --driver overlay --attachable traefik-public

# ── Build das imagens na VPS ───────────────────────────────────
echo "[2/4] Buildando imagens Docker..."
docker-compose build --no-cache

# ── Deploy no Swarm ────────────────────────────────────────────
echo "[3/4] Fazendo deploy no Swarm..."
docker stack deploy -c docker-stack.yml "$STACK" --with-registry-auth

# ── Aguarda servicos subirem ───────────────────────────────────
echo "[4/4] Aguardando servicos..."
sleep 10
docker service ls | grep "$STACK"

echo ""
echo "=========================================="
echo "  Deploy concluido!"
echo "=========================================="
echo ""
echo "  Dashboard:       https://insta.conectplay.top"
echo "  Imagens (bot):   http://$(curl -s ifconfig.me):8080"
echo ""
echo "  Logs bot:        docker service logs -f ${STACK}_instagram-bot"
echo "  Logs dashboard:  docker service logs -f ${STACK}_dashboard"
echo "  Status:          docker service ls | grep ${STACK}"
echo "  Remover stack:   docker stack rm ${STACK}"
echo ""
