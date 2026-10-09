#!/usr/bin/env bash
#
# NovaOS — démarre l'ISO dans QEMU pour la tester sans l'installer.
#
# Usage : ./vm-test.sh
#   NOVAOS_UEFI=1 ./vm-test.sh   # test en mode UEFI (nécessite OVMF)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ISO="$(ls -1 "$SCRIPT_DIR"/novaos-*.iso 2>/dev/null | head -n1 || true)"
if [ -z "$ISO" ]; then
    echo "[novaos] Aucune ISO trouvée. Construisez-la d'abord : sudo ./build.sh" >&2
    exit 1
fi

command -v qemu-system-x86_64 >/dev/null 2>&1 \
    || { echo "[novaos] qemu-system-x86_64 non trouvé : sudo apt install qemu-system-x86" >&2; exit 1; }

KVM_ARGS=()
if [ -e /dev/kvm ] && [ -w /dev/kvm ]; then
    KVM_ARGS=(-enable-kvm -cpu host)
    echo "[novaos] KVM détecté — accélération matérielle activée."
else
    echo "[novaos] KVM indisponible — démarrage en émulation (plus lent)."
fi

UEFI_ARGS=()
if [ "${NOVAOS_UEFI:-0}" = "1" ]; then
    for ovmf in /usr/share/OVMF/OVMF_CODE.fd /usr/share/ovmf/OVMF.fd /usr/share/qemu/OVMF.fd; do
        if [ -f "$ovmf" ]; then
            UEFI_ARGS=(-bios "$ovmf")
            echo "[novaos] Test en mode UEFI ($ovmf)."
            break
        fi
    done
    [ ${#UEFI_ARGS[@]} -gt 0 ] || echo "[novaos] OVMF introuvable — test BIOS classique."
fi

echo "[novaos] Démarrage de : $ISO"
exec qemu-system-x86_64 \
    "${KVM_ARGS[@]}" \
    "${UEFI_ARGS[@]}" \
    -m 4096 \
    -smp 4 \
    -cdrom "$ISO" \
    -boot d \
    -vga virtio \
    -netdev user,id=n0 \
    -device virtio-net-pci,netdev=n0 \
    -usb \
    -device usb-tablet
