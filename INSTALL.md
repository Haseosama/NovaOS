# Guide d'Installation et de Démarrage — NovaOS Hyperion 2026

Ce guide explique pas à pas comment :
1. Démarrer NovaOS en mode **Live CD** (session temporaire en RAM).
2. Installer NovaOS de manière permanente sur un disque NVMe, SSD ou machine virtuelle avec **chiffrement total LUKS2 / AES-256**.
3. Récupérer et sauvegarder la **clé d'urgence BitLocker Neo** à 48 chiffres.

---

## 💿 Option 1 : Démarrer en Mode Live CD (Sans Installation)

Le mode **Live CD** charge l'intégralité du système en mémoire vive (RAM). Aucune modification n'est apportée à vos disques physiques tant que vous ne lancez pas l'installateur.

### Démarrage sur Machine Virtuelle (VirtualBox / VMware / QEMU)
1. Téléchargez ou compilez l'image ISO : `dist/NovaOS-v1.0-x86_64-LiveCD.iso`.
2. Créez une nouvelle machine virtuelle :
   - Type : Linux / Windows 11 (64-bit)
   - Mémoire vive : 2048 Mo minimum (4096 Mo recommandés)
   - Disque dur : 32 Go ou plus (si vous souhaitez tester l'installation)
   - Activez l'option **EFI (Special OSes only)** dans les paramètres de la carte mère.
3. Attachez le fichier ISO au lecteur virtuel.
4. Lancez la machine : le menu de démarrage NovaOS s'affiche avec le logo néon.
5. Sélectionnez `NovaOS 1.0 (Live CD - Futuristic Secure Desktop)`.
6. Le bureau NovaShell s'affiche avec la barre des tâches centrée.

### Démarrage sur PC Réel (Clé USB Bootable)
1. Insérez une clé USB de 4 Go ou plus.
2. Flashez l'ISO à l'aide d'un outil tel que **Rufus** (sélectionner partitionnement GPT et cible UEFI) ou **BalenaEtcher** :
   ```bash
   # Ou en ligne de commande Linux :
   sudo dd if=dist/NovaOS-v1.0-x86_64-LiveCD.iso of=/dev/sdX bs=4M status=progress conv=fdatasync
   ```
3. Redémarrez votre ordinateur et appuyez sur la touche de sélection de boot (F12, F11, F8 ou Échap selon la marque).
4. Choisissez la clé USB en mode UEFI.
5. NovaOS démarre directement dans le bureau sécurisé.

---

## 💾 Option 2 : Installer NovaOS sur Disque (Setup Wizard)

L'installation déploie NovaOS sur votre disque avec chiffrement matériel de niveau militaire.

### Étapes de l'Installation :
1. **Depuis le bureau Live CD** :
   - Cliquez sur l'icône **[5] Installer** ou tapez `5` dans la console.
   - Ou depuis le terminal : tapez `install-os` ou exécutez `./bin/novaos-installer`.
2. **Étape 1 : Sélection du disque cible** :
   - L'assistant liste tous les disques détectés (ex. `/dev/nvme0n1`, `/dev/sda`, `/dev/vda`).
   - Sélectionnez le numéro correspondant au disque à utiliser.
3. **Étape 2 : Partitionnement GPT & Chiffrement** :
   - NovaOS prépare automatiquement 3 partitions :
     - `ESP` (512 Mo, FAT32) pour le boot UEFI Secure Boot.
     - `NovaRecovery` (1024 Mo, ext4) pour la restauration d'urgence.
     - `Nova Encrypted Root` (Reste du disque) configuré en **LUKS2 AES-256-XTS** avec dérivation de clé **Argon2id**.
4. **Étape 3 : Compte Administrateur & PIN** :
   - Définissez le nom d'utilisateur et le mot de passe maître / PIN de déverrouillage.
5. **Étape 4 : Déploiement** :
   - La barre de progression affiche le formatage, l'extraction de l'image système, la configuration du TPM 2.0 et l'enregistrement de l'entrée NVRAM UEFI.
6. **Étape 5 : Clé d'Urgence BitLocker Neo** :
   - Un identifiant à 48 chiffres est généré (ex: `482910-384920-194820-948201-482910-394821-482910-849201`).
   - **Notez cette clé en lieu sûr.** Elle est requise si votre carte mère change ou si le module TPM est réinitialisé.
7. **Étape 6 : Redémarrage** :
   - Retirez le support Live CD et redémarrez sur votre disque chiffré.

---

## ⌨️ Commandes Rapides dans Nova Terminal

Une fois dans NovaOS, ouvrez le terminal (`[1] Terminal`) :

| Commande | Action |
|---|---|
| `novafetch` | Affiche les spécifications techniques et le logo Win11 néon |
| `sysinfo` | Détails sur le CPU, la mémoire, le disque et l'état du TPM |
| `defender` | État des boucliers temps réel et des signatures antivirus |
| `scan <dossier>` | Analyse heuristique antimalware |
| `firewall` | Affiche les statistiques du pare-feu Zero-Trust |
| `vault init <motdepasse>` | Initialise le coffre-fort BitLocker Neo (Lecteur V:) |
| `vault status` | Vérifie si le coffre est monté ou verrouillé |
| `shred <fichier>` | Détruit définitivement un fichier selon le standard militaire DoD 5220.22-M |
| `integrity` | Affiche l'état des registres PCR TPM 2.0 (Measured Boot) |
| `install-os` | Déclenche l'assistant d'installation sur disque |
| `matrix` | Effet visuel cybernétique néon |
