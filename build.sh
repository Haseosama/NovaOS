#!/usr/bin/env bash
#
# NovaOS — script de construction de l'ISO
#
# Construit une ISO NovaOS (Debian 13 « trixie » + KDE Plasma 6, look
# futuriste inspiré de Windows 11, durcie, démarrage automatique sur le bureau)
# au moyen de Debian live-build.
#
# Usage : sudo ./build.sh
#
# Variables d'environnement :
#   NOVAOS_DISTRO          version de Debian   (défaut : trixie)
#   NOVAOS_ARCH            architecture        (défaut : amd64)
#   NOVAOS_MIRROR          miroir principal    (défaut : http://deb.debian.org/debian)
#   NOVAOS_MIRROR_SECURITY miroir de sécurité  (défaut : http://security.debian.org/debian-security)
#   NOVAOS_IMAGE_NAME      nom de l'ISO        (défaut : novaos-2026.10-amd64)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DISTRO="${NOVAOS_DISTRO:-trixie}"
ARCH="${NOVAOS_ARCH:-amd64}"
MIRROR="${NOVAOS_MIRROR:-http://deb.debian.org/debian}"
MIRROR_SECURITY="${NOVAOS_MIRROR_SECURITY:-http://security.debian.org/debian-security}"
IMAGE_NAME="${NOVAOS_IMAGE_NAME:-novaos-2026.10-amd64}"

log()  { printf '\033[1;34m[novaos]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[novaos]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[novaos] ERREUR :\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- bannière --
cat <<'BANNER'

   ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ███████╗ ██████╗ ███████╗
   ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝██╔════╝ ██╔════╝
   ██╔██╗ ██║██║   ██║██║   ██║███████║██║   ██║███████╗██║  ███╗█████╗
   ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║   ██║╚════██║██║   ██║██╔══╝
   ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╔╝███████║╚██████╔╝███████╗
   ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝

   Debian 13 « trixie » · KDE Plasma 6 · look futuriste inspiré de Windows 11
   Sécurisée · démarre automatiquement sur le bureau

BANNER

# ------------------------------------------------------------- vérifications --
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        log "Reconnexion en root via sudo (live-build construit un chroot)…"
        exec sudo -E "$0" "$@"
    fi
    die "Ce script doit être exécuté en root : sudo ./build.sh"
fi

# Outils nécessaires sur l'hôte (l'ISO est hybride BIOS+UEFI : syslinux + grub-efi)
for dep in lb xorriso mksquashfs rsync wget debootstrap isohybrid grub-mkimage; do
    command -v "$dep" >/dev/null 2>&1 \
        || die "Dépendance manquante : '$dep'. Installez : sudo apt install live-build debootstrap xorriso squashfs-tools rsync wget isolinux syslinux-common syslinux-utils grub-pc-bin grub-efi-amd64-bin mtools"
done

log "Distribution : Debian $DISTRO ($ARCH)"
log "Miroir        : $MIRROR"
log "Image         : $IMAGE_NAME.iso"

# ----------------------------------------------------------------- nettoyage --
log "Nettoyage de l'état de build précédent…"
lb clean >/dev/null 2>&1 || true

# ------------------------------------------------------- configuration lb -----
log "Configuration de live-build…"
lb config \
    --distribution "$DISTRO" \
    --architectures "$ARCH" \
    --archive-areas "main contrib non-free non-free-firmware" \
    --mirror-bootstrap "$MIRROR" \
    --mirror-chroot "$MIRROR" \
    --mirror-binary "$MIRROR" \
    --mirror-binary-security "$MIRROR_SECURITY" \
    --apt-recommends true \
    --bootloaders "syslinux,grub-efi" \
    --binary-images iso-hybrid \
    --debian-installer none \
    --image-name "$IMAGE_NAME" \
    --iso-application "NovaOS" \
    --iso-publisher "NovaOS Project" \
    --iso-preparer "NovaOS build.sh (Debian live-build)" \
    --iso-volume "NovaOS" \
    --bootappend-live "boot=live components quiet splash locales=fr_FR.UTF-8 keyboard-layouts=fr preempt=full"

# ------------------------------------------------------------------ build -----
log "Construction de l'ISO (30 à 90 minutes selon la machine)…"
lb build

# ------------------------------------------------------------------ résultat --
ISO="$(ls -1 "${IMAGE_NAME}"*.iso 2>/dev/null | head -n1 || true)"
[ -n "$ISO" ] || die "L'ISO n'a pas été trouvée après la construction."

sha256sum "$ISO" > "${ISO}.sha256sums"

log "✔ ISO générée      : $SCRIPT_DIR/$ISO"
log "✔ Somme SHA256     : $SCRIPT_DIR/${ISO}.sha256sums"
log "✔ Vérification     : sha256sum -c ${ISO}.sha256sums"
log "✔ Test sans install: ./vm-test.sh"
log "✔ Installation     : gravez l'ISO sur une clé USB, démarrez dessus,"
log "                     puis cliquez sur l'icône « Installer NovaOS » du bureau"
