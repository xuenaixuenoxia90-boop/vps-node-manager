#!/usr/bin/env bash
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "请使用 sudo bash install.sh" >&2
  exit 1
fi

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST=/opt/vps-node-manager

install -d -m 700 "$DST" "$DST/adapters" "$DST/config" "$DST/backups" "$DST/output" "$DST/logs"

# The repository may already have been cloned into the installation directory.
# Never copy a file or directory onto itself.
if [[ "$SRC" != "$DST" ]]; then
  install -m 755 "$SRC/node_manager.py" "$DST/node_manager.py"
  cp -a "$SRC/adapters/." "$DST/adapters/"
  install -m 600 "$SRC/config/settings.example.json" "$DST/config/settings.example.json"
else
  chmod 755 "$DST/node_manager.py"
  find "$DST/adapters" -type f -name '*.py' -exec chmod 644 {} \;
  chmod 600 "$DST/config/settings.example.json"
fi

if [[ ! -f "$DST/config/settings.json" ]]; then
  install -m 600 "$DST/config/settings.example.json" "$DST/config/settings.json"
fi

chmod 700 "$DST" "$DST/adapters" "$DST/config" "$DST/backups" "$DST/output" "$DST/logs"
chmod 600 "$DST/config/settings.json"

cat >/usr/local/bin/vps-node-manager <<'EOF'
#!/usr/bin/env bash
exec python3 /opt/vps-node-manager/node_manager.py "$@"
EOF
chmod 755 /usr/local/bin/vps-node-manager

if command -v apt-get >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y python3-yaml python3-cryptography
fi

echo "安装完成。先检查 $DST/config/settings.json，再运行 vps-node-manager audit"
