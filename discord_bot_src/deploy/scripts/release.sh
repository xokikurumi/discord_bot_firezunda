#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat <<USAGE
Usage:
  sudo ./deploy/scripts/release.sh <tag> [service_name] [app_user]

Examples:
  sudo ./deploy/scripts/release.sh v1.0.1 discord-bot discord-bot
  sudo ./deploy/scripts/release.sh v1.0.1 D_discord_dev discord

Environment variables:
  APP_ROOT     Default: /opt/discord
  PYTHON_BIN   Default: python3
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	usage
	exit 0
fi

TAG="${1:-}"
SERVICE_NAME="${2:-discord-bot}"
APP_USER="${3:-discord-bot}"
APP_ROOT="${APP_ROOT:-/opt/discord}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -z "$TAG" ]; then
	usage
	exit 1
fi

RELEASE_DIR="${APP_ROOT}/releases/${TAG}"
CURRENT_LINK="${APP_ROOT}/current"
CONFIG_DIR="${APP_ROOT}/config"

if [ "$(id -u)" -ne 0 ]; then
	echo "This script must be run as root. Use sudo." >&2
	exit 1
fi

if ! id "$APP_USER" >/dev/null 2>&1; then
	echo "Application user does not exist: ${APP_USER}" >&2
	exit 1
fi

if [ ! -d "$RELEASE_DIR" ]; then
	echo "Release directory does not exist: ${RELEASE_DIR}" >&2
	exit 1
fi

if [ ! -f "${RELEASE_DIR}/requirements.txt" ]; then
	echo "requirements.txt does not exist in: ${RELEASE_DIR}" >&2
	exit 1
fi

if [ ! -f "${RELEASE_DIR}/main.py" ]; then
	echo "main.py does not exist in: ${RELEASE_DIR}" >&2
	exit 1
fi

if [ -e "$CURRENT_LINK" ] && [ ! -L "$CURRENT_LINK" ]; then
	BACKUP_PATH="${APP_ROOT}/current.bak.$(date +%Y%m%d%H%M%S)"
	echo "${CURRENT_LINK} is a directory or file. Moving it to ${BACKUP_PATH}."
	mv "$CURRENT_LINK" "$BACKUP_PATH"
fi

echo "Switching current release to ${RELEASE_DIR}."
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"
ls -ld "$CURRENT_LINK"

echo "Updating owner for ${RELEASE_DIR}."
chown -R "${APP_USER}:${APP_USER}" "$RELEASE_DIR"

if [ -d "${RELEASE_DIR}/config" ]; then
	echo "Copying config files to ${CONFIG_DIR}."
	install -d -o "$APP_USER" -g "$APP_USER" "$CONFIG_DIR"
	cp -a "${RELEASE_DIR}/config/." "$CONFIG_DIR/"
	chown -R "${APP_USER}:${APP_USER}" "$CONFIG_DIR"
else
	echo "Config directory does not exist in release. Skipping config copy: ${RELEASE_DIR}/config"
fi

cd "$CURRENT_LINK"

echo "Preparing Python virtual environment."
if [ ! -x ".venv/bin/python" ]; then
	sudo -u "$APP_USER" "$PYTHON_BIN" -m venv .venv
fi

sudo -u "$APP_USER" .venv/bin/python -m pip install --upgrade pip
sudo -u "$APP_USER" .venv/bin/python -m pip install -r requirements.txt
sudo -u "$APP_USER" .venv/bin/python -m pip check

echo "Restarting ${SERVICE_NAME}.service."
systemctl restart "${SERVICE_NAME}.service"
systemctl --no-pager status "${SERVICE_NAME}.service"

echo "Release completed: ${TAG}"
