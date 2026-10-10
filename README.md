# 🌌 NovaOS

**NovaOS** est une distribution GNU/Linux construite sur **Debian 13 « trixie »**, dotée d'un bureau **KDE Plasma 6** au design **futuriste inspiré de Windows 11** : barre des tâches centrée, thème sombre « verre dépoli », coins arrondis, écran de connexion et splash de démarrage originaux.

Elle est **sécurisée par défaut** et **démarre automatiquement sur le bureau** (connexion automatique à l'ouverture de session).

> 🎨 Le look est une création originale de NovaOS — aucun asset Microsoft n'est utilisé. Les fonds d'écran, le logo et le thème de connexion sont générés pour ce projet.

---

## ✨ Fonctionnalités

| Domaine | Ce que fait NovaOS |
|---|---|
| **Base** | Debian 13 « trixie » (paquets officiels, noyaux Debian, dépôts `main contrib non-free non-free-firmware`) |
| **Bureau** | KDE Plasma 6 (Wayland par défaut, X11 disponible), Plasma 6 + Breeze Dark |
| **Look Windows 11** | Barre des tâches centrée façon Win11, lanceur + applications épinglées (Firefox, Dolphin, Konsole, Réglages, VLC), horloge avec date, thème sombre accent `#0078D4`, curseur blanc, icônes Papirus-Dark, simple clic |
| **Futuriste** | Écran de connexion SDDM maison (`novaos`), splash Plymouth, fonds d'écran « Bloom » et « Neon » générés pour NovaOS, `fastfetch` à l'ouverture des terminaux, logo hexagonal NovaOS |
| **Démarrage auto** | Connexion automatique SDDM → le bureau s'ouvre directement, sans mot de passe (désactivable en une ligne) |
| **Sécurité** | Pare-feu UFW actif, mises à jour automatiques, AppArmor, politique de mots de passe (12 caractères + complexité), sysctl noyau durcis, aucun serveur SSH, verrouillage écran après 5 min d'inactivité, coredumps désactivés, chiffrement LUKS proposé à l'installation |
| **Langue** | Français par défaut (interface, AZERTY, fuseau Europe/Paris) |

## 🛠️ Prérequis (pour construire l'ISO)

- Un hôte **Debian 12/13** ou **Ubuntu 22.04+** (la construction se fait dans un chroot : **root requis**)
- ~20 Go d'espace disque libres, 4 Go de RAM
- Les outils : `live-build`, `debootstrap`, `xorriso`, `squashfs-tools`, `rsync`, `wget` + les outils de l'ISO hybride BIOS+UEFI : `isolinux`, `syslinux-common`, `syslinux-utils` (fournit `isohybrid`), `grub-pc-bin`, `grub-efi-amd64-bin`, `mtools`

```bash
sudo apt install live-build debootstrap xorriso squashfs-tools rsync wget \
  isolinux syslinux-common syslinux-utils grub-pc-bin grub-efi-amd64-bin mtools
```

## 🏗️ Construire l'ISO

```bash
sudo ./build.sh
```

Le script :

1. nettoie l'état de build précédent,
2. configure **live-build** (Debian `trixie`, `amd64`, dépôts officiels + sécurité, **pas** d'installeur Debian — l'installateur est **Calamares**, installé par paquets et lancé depuis le bureau),
3. construit le chroot en appliquant les hooks NovaOS (branding, thème, sécurité, autologin, installateur, finalisation),
4. produit **`novaos-2026.10-amd64.hybrid.iso`** (ISO **hybride BIOS+UEFI**, inscriptible directement sur clé USB avec `dd`) + sa somme de contrôle SHA256.

⏱️ Comptez **30 à 90 minutes** selon la machine et la connexion.

### Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `NOVAOS_DISTRO` | `trixie` | Version de Debian à embarquer |
| `NOVAOS_ARCH` | `amd64` | Architecture |
| `NOVAOS_MIRROR` | `http://deb.debian.org/debian` | Miroir principal |
| `NOVAOS_MIRROR_SECURITY` | `http://security.debian.org/debian-security` | Miroir de sécurité |
| `NOVAOS_IMAGE_NAME` | `novaos-2026.10-amd64` | Nom de l'ISO produite |

Exemple : `sudo NOVAOS_DISTRO=trixie NOVAOS_IMAGE_NAME=novaos-test-amd64 ./build.sh`

## ▶️ Tester sans installer

```bash
./vm-test.sh
```

Démarre l'ISO dans **QEMU** (KVM automatiquement si disponible, 4 Go de RAM, réseauNAT). Vous arrivez directement sur le bureau — comme sur la machine réelle.

## 💿 Installer sur une machine

1. Gravez l'ISO sur une clé USB (`sudo dd if=novaos-*.iso of=/dev/sdX bs=4M status=progress` — ou Ventoy).
2. Démarrez dessus : la session **live** s'ouvre automatiquement sur le bureau. Utilisateur live : **« user »**, mot de passe : **« live »** (`sudo` fonctionne sans mot de passe dans la session live).
3. Double-cliquez sur l'icône **« Installer NovaOS »** du bureau (installateur graphique **Calamares**, lancé en root sans mot de passe).
4. À l'étape de partitionnement : choisissez **« Effacer le disque »** et cochez **« Chiffrer »** (LUKS) — **fortement recommandé** pour la sécurité.
5. Créez votre compte (12 caractères minimum, complexité requise).
6. Redémarrez : **le bureau s'ouvre automatiquement**, sans saisie de mot de passe.

> 💡 Le compte « live » de la clé USB est automatiquement verrouillé sur le système installé, et l'icône « Installer NovaOS » est retirée du bureau.

## 🔓 Démarrage automatique (autologin)

NovaOS démarre directement sur le bureau KDE (session Plasma Wayland).

- **Désactiver la connexion automatique** (mot de passe demandé à chaque démarrage) :

  ```bash
  sudo sed -i 's/NOVAOS_AUTOLOGIN=true/NOVAOS_AUTOLOGIN=false/' /etc/novaos/autologin.conf
  sudo reboot
  ```

- Le service `novaos-autologin-setup.service` écrit la configuration SDDM (`/etc/sddm.conf.d/99-novaos-autologin.conf`) **au démarrage**, pour l'utilisateur principal — que ce soit l'utilisateur live de l'ISO ou le compte créé à l'installation.
- En cas de **désactivation**, le service neutralise aussi l'autologin écrit dans `/etc/sddm.conf` par live-config (session live) ou Calamares (système installé) : chez SDDM, ce fichier a la **priorité** sur `/etc/sddm.conf.d/`.
- Après une **déconnexion**, l'écran de connexion réapparaît (politique sécurisée : `Relogin=false`).

## 🔒 Sécurité

Le détail complet des mesures, du modèle de menaces et des limites est dans **[SECURITY.md](SECURITY.md)**.

En résumé : pare-feu UFW (entrant refusé), mises à jour automatiques (sécurité + correctifs), AppArmor, mots de passe 12+ caractères, sysctl noyau durcis (`ptrace_scope=2`, BPF non privilégié désactivé, user namespaces restreints…), aucun serveur SSH, verrouillage écran 5 min + au réveil, coredumps désactivés, journaux bornés, compte live verrouillé après installation, chiffrement LUKS proposé.

## 🎨 Personnaliser NovaOS

Tout se passe dans le dépôt, avant de reconstruire l'ISO :

| Élément | Fichier |
|---|---|
| Palette / thème sombre | `config/includes.chroot/usr/share/color-schemes/NovaOS-Dark.colors` |
| Barre des tâches (look Win11) | `config/includes.chroot/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc` |
| Fonds d'écran | `config/includes.chroot/usr/share/wallpapers/` |
| Écran de connexion (SDDM) | `config/includes.chroot/usr/share/sddm/themes/novaos/` |
| Logo NovaOS | `assets/branding/novaos-logo.svg` (copie dans `usr/share/novaos/`) |
| Paquets installés | `config/package-lists/*.list.chroot` |
| Durcissement | `config/hooks/live/0130-security.hook.chroot` |
| Connexion automatique | `config/hooks/live/0140-autologin.hook.chroot` + `config/includes.chroot/etc/novaos/autologin.conf` |
| Installateur (Calamares) | `config/includes.chroot/usr/share/novaos/calamares-staging/` |
| Icône « Installer NovaOS » | `config/includes.chroot/usr/local/bin/novaos-install` + `config/includes.chroot/etc/skel/Desktop/` |
| Localisation (FR) | `config/hooks/live/0160-finalize.hook.chroot` |

## 📁 Structure du projet

```
NovaOS/
├── build.sh                          # construction de l'ISO (live-build)
├── vm-test.sh                        # test de l'ISO dans QEMU
├── Makefile                          # make build / test / check / clean
├── SECURITY.md                       # politique de sécurité détaillée
├── LICENSE                           # MIT
├── .github/workflows/build-iso.yml    # CI : construit l'ISO à chaque push
├── assets/
│   ├── branding/novaos-logo.svg      # logo (source)
│   └── installer/preseed-novaos.cfg  # preseed d-i (référence — non utilisé)
└── config/                           # configuration live-build
    ├── package-lists/                # paquets par thème (bureau, applis, sécurité…)
    ├── hooks/                        # scripts exécutés dans le chroot
    │   ├── normal/                   # (live-build n'exécute les hooks locaux
    │   │   └── 0110-branding.hook.chroot   # que si normal/ ET live/ sont non vides)
    │   └── live/
    │       ├── 0120-theme-win11.hook.chroot
    │       ├── 0130-security.hook.chroot
    │       ├── 0140-autologin.hook.chroot
    │       ├── 0150-installer.hook.chroot
    │       └── 0160-finalize.hook.chroot
    └── includes.chroot/              # fichiers copiés tels quels dans le système
        ├── etc/                      # sysctl, APT, SDDM, systemd, skel, autostart, polkit, live-config…
        └── usr/                      # thèmes, fonds d'écran, scripts, Calamares…
```

## 🤖 Intégration continue

La [GitHub Action](.github/workflows/build-iso.yml) construit l'ISO automatiquement à chaque push sur `main` (ou `arena/**`) et la publie en **artefact téléchargeable** (`novaos-iso`).

## 🙏 Crédits

- **Debian** — base de la distribution
- **KDE Community** — bureau Plasma 6, Breeze, SDDM
- **Calamares** — installateur graphique
- Les fonds d'écran, le logo et le thème de connexion NovaOS sont des créations originales générées pour ce projet

## 📜 Licence

[MIT](LICENSE) — © 2026 NovaOS Project
