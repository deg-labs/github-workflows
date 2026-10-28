#!/usr/bin/env bash
set -euo pipefail
mode=$1
app=$2
runtime_file=$3
prefix=$4
[[ "$prefix" =~ ^gce-[0-9]+-[0-9]+$ ]] || exit 1
if [[ "$mode" == package-update ]]; then
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get -o APT::Update::Error-Mode=any update
  sudo apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold upgrade
  sudo systemd-run --unit=gce-package-maintenance-reboot --on-active=60s /usr/bin/systemctl reboot
  exit 0
fi
[[ "$mode" == compose && "$app" =~ ^[a-z0-9][a-z0-9._-]*$ ]] || exit 1
target="/opt/apps/$app"
sudo mkdir -p "$target"
sudo chown -R "$(id -u):$(id -g)" "$target"
tar --no-same-owner --no-same-permissions -xzf "$HOME/$prefix-archive.tgz" -C "$target"
mv -f "$HOME/$prefix-env" "$target/.env"
chmod 600 "$target/.env"
if [[ -n "$runtime_file" ]]; then
  [[ "$runtime_file" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]] || exit 1
  mv -f "$HOME/$prefix-file" "$target/$runtime_file"
  chmod 600 "$target/$runtime_file"
fi
cd "$target"
sudo docker compose up -d --build --remove-orphans
