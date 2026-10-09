# Architecture Technique — NovaOS Hyperion 2026

Ce document détaille l'architecture interne du système d'exploitation NovaOS, de la séquence d'amorçage jusqu'au gestionnaire de fenêtres du bureau.

---

## 1. Séquence d'Amorçage (Boot Sequence)

NovaOS supporte deux chemins de démarrage :

```
                  +-----------------------------------+
                  |         Mise sous tension         |
                  +-----------------------------------+
                                    |
                    +---------------+---------------+
                    |                               |
           [Mode BIOS / MBR]                [Mode UEFI 64-bit]
                    |                               |
          +-------------------+           +-------------------+
          |  bootsector.s     |           |   BOOTX64.EFI     |
          |  (512 o, 0xAA55)  |           |   (PE32+ x86_64)  |
          +-------------------+           +-------------------+
                    |                               |
          +-------------------+           +-------------------+
          |    stage2.c       |           |   Vérif. PCR-7    |
          |  (Mode protégé)   |           |  (Secure Boot db) |
          +-------------------+           +-------------------+
                    \                               /
                     \                             /
                   +---------------------------------+
                   |       vmlinuz-novaos (Noyau)    |
                   |      KASLR / PTI / Hardening    |
                   +---------------------------------+
                                    |
                   +---------------------------------+
                   |     initrd-novaos.img (RAM)     |
                   |      Initramfs CPIO Compilé     |
                   +---------------------------------+
                                    |
                   +---------------------------------+
                   |      NovaShell Desktop Core     |
                   | (Bureau Win11 / Terminal / Wzd) |
                   +---------------------------------+
```

### Amorçage BIOS (Legacy El Torito)
1. Le BIOS charge les 512 premiers octets de l'image de boot (`boot/bootsector.bin`) à l'adresse mémoire `0x7C00`.
2. `bootsector.s` initialise les segments, active la ligne A20, valide la présence de CPUID et du support 64-bit Long Mode.
3. Le contrôle est transféré à `stage2.c` qui initialise la table des descripteurs globaux (GDT), active la pagination et saute dans le noyau durci.

### Amorçage UEFI (Modern Secure Boot)
1. Le firmware UEFI charge `EFI/BOOT/BOOTX64.EFI` (image PE32+ 64-bit conforme à la spécification UEFI 2.8+).
2. L'application EFI mesure son propre hash dans le registre PCR-4 du TPM 2.0 et vérifie la clé Secure Boot dans PCR-7.
3. Elle alloue la mémoire système et transfère l'exécution au noyau NovaOS.

---

## 2. Arguments de Durcissement du Noyau

Le chargeur de démarrage applique systématiquement ces paramètres de sécurité au démarrage :
- `pti=on` : Isolation stricte de la table des pages utilisateur/noyau (protection contre Meltdown).
- `slab_nomerge` : Interdiction de mutualiser les caches mémoire slab pour empêcher le détournement d'objets du noyau.
- `page_alloc.shuffle=1` : Randomisation de l'allocateur de pages physiques contre les attaques de prédictibilité de tas.
- `randomize_kstack_offset=on` : Décalage aléatoire de la pile d'exécution du noyau à chaque appel système.
- `init_on_alloc=1` et `init_on_free=1` : Mise à zéro automatique de la mémoire à l'allocation et à la libération contre les fuites de secrets.
- `security=apparmor` : Profilage strict des capacités système des processus.

---

## 3. Composants du Système d'Exploitation

### A. Couche d'Intégrité Matérielle (`kernel/`)
- `sysinfo.py` : Interroge `/proc`, `/sys` et les compteurs CPU/RAM pour offrir une télémétrie en temps réel au bureau.
- `integrity.py` : Simule et gère les registres PCR d'un co-processeur cryptographique TPM 2.0 avec hachage SHA-512 réentrant.

### B. Moteur de Défense et de Cryptographie (`security/`)
- `crypto_engine.py` : Abstraction cryptographique certifiée FIPS-ready (AES-256-GCM, Argon2id, PBKDF2-HMAC-SHA512, Ed25519).
- `vault.py` : Conteneur de fichiers chiffré transparent (disque virtuel V:).
- `defender.py` : Moteur antivirus heuristique temps réel détectant les signatures de shells distants et attaques DoS.
- `firewall.py` : Pare-feu à état dynamique bloquant les flux non sollicités et appliquant une politique Zero-Trust.
- `shredder.py` : Nettoyeur sécurisé DoD 5220.22-M écrasant 7 fois les données avant suppression des pointeurs inode.

### C. Environnement Graphique Windows 11 Neo (`shell/`)
- `desktop.py` : Moteur de rendu plein écran reproduisant l'interface de Windows 11 avec design néon/holographique.
- `terminal.py` : Console cybernétique inspirée de Windows Terminal / PowerShell avec commandes d'administration avancées.
- `taskbar.py` : Barre des tâches centrée avec horloge, indicateurs matériels et raccourcis.

### D. Installateur sur Disque (`installer/`)
- `disk.py` : Découverte des unités de stockage physiques et virtuelles, création des tables GPT et conteneurs LUKS2.
- `deploy.py` : Pipeline d'installation avec génération de la clé de secours BitLocker Neo à 48 chiffres.
- `wizard.py` : Interface d'installation assistée pas à pas.
