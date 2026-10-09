# NovaOS — Hyperion 2026 Edition
### OS Futuriste Inspiré de Windows 11 avec Cœur Ultra-Sécurisé (Live CD & Installation sur Disque)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Security Profile](https://img.shields.io/badge/security-Zero--Trust%20Military%20Grade-cyan.svg)]()
[![Encryption](https://img.shields.io/badge/crypto-AES--256--GCM%20%7C%20LUKS2-blue.svg)]()
[![Format](https://img.shields.io/badge/delivery-Live%20CD%20ISO%20%7C%20Bare--Metal%20Installer-purple.svg)]()

```
 ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗      ██████╗ ███████╗
 ████╗  ██║██╔═══██╗██║   ██║██╔══██╗    ██╔═══██╗██╔════╝
 ██╔██╗ ██║██║   ██║██║   ██║███████║    ██║   ██║███████╗
 ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║    ██║   ██║╚════██║
 ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║    ╚██████╔╝███████║
 ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝     ╚═════╝ ╚══════╝
   HYPERION 2026 — SECURE WINDOWS 11 NEO ARCHITECTURE
```

**NovaOS** est un système d'exploitation moderne, inspiré de l'ergonomie et de l'esthétique futuriste de **Windows 11** (barre des tâches centrée, menu Démarrer dynamique, effet verre acrylique/néon cyan, widgets de télémétrie), doté d'une **architecture de sécurité militaire Zero-Trust**.

NovaOS est conçu pour être exécuté en **Live CD (démarrage direct en RAM sans modifier votre matériel)** ou pour être **installé sur disque (NVMe, SSD, disque virtuel)** avec un chiffrement intégral des partitions (**LUKS2 AES-256-XTS** + clé de récupération d'urgence **BitLocker Neo** à 48 chiffres).

---

## 🌟 Points Forts & Fonctionnalités

### 1. 💽 Format Live CD & Installateur Natif (Pas de Navigateur Web)
- **Image ISO Bootable El Torito** : Conforme aux standards BIOS et UEFI 64-bit (`dist/NovaOS-v1.0-x86_64-LiveCD.iso`).
- **Prêt pour Bare-Metal ou VM** : Peut être gravé sur clé USB avec Rufus, Ventoy ou BalenaEtcher, ou démarré directement dans VirtualBox, VMware ou QEMU.
- **Mode Live CD en RAM** : Démarre instantanément en mémoire vive pour des sessions anonymes et ultra-sécurisées, sans laisser de traces sur les disques physiques.
- **NovaOS Setup Wizard** : Installateur guidé pas à pas pour partitionner votre disque en GPT, initialiser le chiffrement matériel, configurer l'administrateur et installer le système.

### 2. 🪟 Interface Graphique Futuriste Style Windows 11 (NovaShell)
- **Barre des Tâches Centrée** :
  - Bouton Démarrer Nova avec logo néon cyan
  - Raccourcis directs : Terminal, Defender, Coffre-fort, Explorateur, Paramètres, Installateur
  - Zone de notification (System Tray) : Horloge temps réel, Statut Wi-Fi 6E, Bouclier TPM 2.0, Batterie
- **Menu Démarrer Holographique** :
  - Applications épinglées
  - Recommandations et derniers événements de sécurité
  - Gestion de session : Verrouillage, Déconnexion, Arrêt sécurisé
- **Nova Terminal (PowerShell Neo)** :
  - Console cybernétique avec télémétrie CPU/RAM en temps réel
  - Commandes intégrées : `novafetch`, `sysinfo`, `defender`, `firewall`, `vault`, `shred`, `integrity`, `matrix`
- **Nova Files (Explorateur de Fichiers)** :
  - Visualisation des lecteurs (Lecteur C: Chiffré, Lecteur V: Coffre-fort, Lecteur D: Live CD)
  - Broyeur de fichiers militaire intégré

### 3. 🛡️ Cœur de Sécurité Militaire (Zero-Trust)
- **Chaîne de Démarrage Mesurée (Measured Boot & TPM 2.0)** :
  - Registres PCR (PCR-0 UEFI, PCR-4 Bootloader, PCR-7 Secure Boot, PCR-8 Kernel)
  - Vérification cryptographique SHA-512 de chaque binaire avant exécution
- **Chiffrement Intégral BitLocker Neo / LUKS2** :
  - Algorithmes : **AES-256-GCM** et **AES-256-XTS**
  - Dérivation de clé par **Argon2id** et **PBKDF2-HMAC-SHA512** (600 000 itérations)
  - Clé de secours d'urgence Windows 11 à 48 chiffres (`XXXXXX-XXXXXX-...`)
- **Nova Defender (Centre de Sécurité en Temps Réel)** :
  - Moteur heuristique détectant les reverse shells, fork bombs, wipers et injections
  - Zone de quarantaine cryptographique isolée
- **NovaWall (Pare-feu Zero-Trust)** :
  - Filtrage dynamique des paquets
  - Mode Furtif (Stealth Mode) : rejet silencieux des scans de ports et requêtes ICMP ping
- **Broyeur de Fichiers DoD 5220.22-M** :
  - Destruction sécurisée en 7 passes successives (zéros, uns, aléatoire cryptographique)

---

## 🚀 Démarrage Rapide

### 1. Cloner le Dépôt
```bash
git clone https://github.com/Haseosama/NovaOS.git
cd NovaOS
```

### 2. Construire l'Image ISO Bootable (Live CD)
```bash
make iso
```
L'image est générée dans `dist/NovaOS-v1.0-x86_64-LiveCD.iso` avec son empreinte SHA-256 dans `dist/SHA256SUMS`.

### 3. Vérifier la Conformité de l'ISO
```bash
make verify
```

### 4. Lancer les Tests Unitaires & Sécurité
```bash
make test
```

### 5. Démarrer NovaOS Directement en Console / Terminal
```bash
# Démarrer le Bureau Futuriste Windows 11 en mode Live CD :
make run-live
# ou directement :
./bin/novaos

# Lancer l'assistant d'installation sur disque :
make install-os

# Lancer la console cybernétique PowerShell Neo :
make terminal

# Lancer le Centre de Sécurité Nova Defender :
make defender
```

---

## 📦 Structure du Projet

```
NovaOS/
├── Makefile                      # Commandes de build, test, et lancement
├── README.md                     # Documentation complète
├── INSTALL.md                    # Guide d'installation et démarrage Live CD
├── SECURITY.md                   # Modèle de menaces et spécifications cryptographiques
├── ARCHITECTURE.md               # Architecture du noyau et des sous-systèmes
├── boot/                         # Chargeurs de démarrage et noyaux
│   ├── bootsector.s              # Boot sector MBR 16/32-bit El Torito (512 octets, 0xAA55)
│   ├── stage2.c                  # Chargeur 2e étape mode protégé / 64-bit
│   ├── efi_boot.c                # Application UEFI PE32+ (BOOTX64.EFI)
│   ├── kernel_stub.c             # Noyau durci NovaOS (KASLR, Zero-Alloc)
│   ├── grub.cfg                  # Menu GRUB Live CD avec options néon
│   └── isolinux.cfg              # Menu Syslinux
├── kernel/                       # Couche d'abstraction noyau & matériel
│   ├── sysinfo.py                # Télémétrie CPU, RAM, disques et TPM
│   └── integrity.py              # Chaîne de mesure TPM 2.0 (PCR 0-9)
├── security/                     # Sous-système de sécurité
│   ├── crypto_engine.py          # AES-256-GCM, PBKDF2-SHA512, Ed25519
│   ├── vault.py                  # Coffre chiffré BitLocker Neo (Lecteur V:)
│   ├── defender.py               # Antivirus heuristique et détection d'intrusions
│   ├── firewall.py               # Pare-feu Zero-Trust NovaWall
│   └── shredder.py               # Broyeur DoD 5220.22-M 7 passes
├── shell/                        # Environnement de bureau Windows 11 Neo
│   ├── desktop.py                # Bureau interactif, barre des tâches, menu Démarrer
│   └── terminal.py               # Terminal cybernétique PowerShell Neo
├── installer/                    # Moteur d'installation
│   ├── disk.py                   # Détection disques et partitionnement GPT
│   ├── deploy.py                 # Déploiement système & clé de récupération
│   └── wizard.py                 # Assistant interactif Windows 11 Setup
├── bin/                          # Exécutables natifs autonomes
│   ├── novaos                    # Lanceur du bureau NovaOS
│   ├── novaos-installer          # Lanceur de l'installateur sur disque
│   ├── novaos-terminal           # Lanceur du terminal
│   └── novaos-defender           # Lanceur de Nova Defender
├── tools/                        # Outils de compilation
│   ├── build_iso.py              # Générateur de l'ISO bootable
│   ├── make_initramfs.py         # Générateur de la ramdisk cpio.gz
│   ├── make_efiboot.py           # Générateur de l'image FAT12 UEFI
│   └── verify_iso.py             # Validateur de conformité ISO El Torito
├── tests/                        # Suite de tests automatisés
│   └── test_novaos.py            # 11 tests unitaires validant l'ensemble
└── dist/                         # Fichiers livrables
    ├── NovaOS-v1.0-x86_64-LiveCD.iso
    ├── NovaOS-v1.0-x86_64-LiveCD.iso.sha256
    └── SHA256SUMS
```

---

## 💻 Démarrage sur Machine Virtuelle & Matériel Réel

### Dans VirtualBox
1. Créez une nouvelle machine virtuelle (Type: **Linux**, Version: **Other Linux 64-bit** ou **Windows 11 64-bit**).
2. Attribuez au minimum 2 Go de RAM et 2 CPU.
3. Dans **Système** > **Carte mère**, cochez **Activer EFI**.
4. Dans **Stockage**, insérez `NovaOS-v1.0-x86_64-LiveCD.iso` dans le lecteur optique virtuel.
5. Démarrez : NovaOS se lance en mode Live CD !

### Dans QEMU
```bash
qemu-system-x86_64 -cdrom dist/NovaOS-v1.0-x86_64-LiveCD.iso -m 2048 -enable-kvm -smp 2
```

### Gravure sur Clé USB pour PC Réel
```bash
# Avec dd sous Linux (remplacer /dev/sdX par votre clé USB) :
sudo dd if=dist/NovaOS-v1.0-x86_64-LiveCD.iso of=/dev/sdX bs=4M status=progress conv=fdatasync
```

---

## 🔒 Spécifications de Sécurité

| Fonctionnalité | Implémentation dans NovaOS |
|---|---|
| **Chiffrement du Disque** | LUKS2 avec AES-256-XTS et dérivation Argon2id |
| **Coffre-fort Virtuel** | AES-256-GCM avec tag d'authentification 128 bits |
| **Clé de Récupération** | Format BitLocker Windows 11 (8 groupes de 6 chiffres = 48 chiffres) |
| **Démarrage Mesuré** | TPM 2.0 PCR-0 (Firmware), PCR-4 (Boot), PCR-7 (Secure Boot Policy) |
| **Protection Processus** | KASLR, PTI, Allocations mémoires mises à zéro (Init-on-Alloc) |
| **Destruction de Données** | DoD 5220.22-M (7 passes avec motif destructif et aléatoire cryptographique) |
| **Filtrage Réseau** | Zero-Trust NovaWall avec rejet furtif (Stealth Drop) |

---

## 📜 Licence
NovaOS est distribué sous licence MIT. Conçu en 2026 pour allier l'élégance de Windows 11 et la rigueur de la cybersécurité moderne.
