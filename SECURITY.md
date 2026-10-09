# Spécifications de Sécurité — NovaOS Hyperion 2026

NovaOS applique les principes du **Zero-Trust Architecture (ZTA)** dès la première instruction exécutée par le processeur jusqu'à l'environnement utilisateur.

---

## 1. Modèle de Menace (Threat Model)

NovaOS est conçu pour résister aux attaques suivantes :
1. **Vol physique d'ordinateur ou de disque dur** :
   - *Mitigation* : Chiffrement intégral LUKS2 AES-256-XTS lié au PCR-7 du TPM 2.0. Les données sont illisibles sans le PIN ou la clé de secours BitLocker à 48 chiffres.
2. **Attaques par Evil Maid (altération du chargeur de démarrage)** :
   - *Mitigation* : Measured Boot vérifiant les condensats SHA-512 du firmware, du bootloader et du noyau. Tout binaire modifié empêche le TPM de libérer la clé de déchiffrement.
3. **Exploitation de vulnérabilités en mémoire (Buffer Overflow, ROP)** :
   - *Mitigation* : KASLR (Kernel Address Space Layout Randomization), PTI (Page Table Isolation), initialisation obligatoire de la mémoire à l'allocation (`init_on_alloc=1`) et à la libération (`init_on_free=1`), mélange des pages physiques (`page_alloc.shuffle=1`).
4. **Malwares, Rançongiciels (Ransomware) et Reverse Shells** :
   - *Mitigation* : Moteur heuristique Nova Defender surveillant en continu les processus et les motifs d'attaque connus (sockets réseau non autorisées, tentatives d'effacement récursif de disques, fork bombs).
5. **Scans de ports et intrusions réseau** :
   - *Mitigation* : Pare-feu Zero-Trust NovaWall avec mode furtif (Stealth Mode) qui abandonne silencieusement les requêtes ICMP ping et bloque tous les ports entrants non explicitement autorisés.
6. **Récupération médico-légale de données effacées** :
   - *Mitigation* : Broyeur DoD 5220.22-M appliquant 7 passes d'écrasement destructif avant suppression du descripteur de fichier.

---

## 2. Cryptographie & Gestion des Clés

| Rôle | Algorithme | Paramètres |
|---|---|---|
| **Chiffrement des Données** | AES (Advanced Encryption Standard) | 256 bits, modes GCM (authentifié) et XTS (disque) |
| **Authentification des Blocs** | GMAC | Tag d'authentification 128 bits |
| **Dérivation de Clé (KDF)** | PBKDF2-HMAC-SHA512 / Argon2id | 600 000 itérations, sel cryptographique de 256 bits |
| **Signatures Numériques** | Ed25519 (Courbe Edwards-25519) | Clés publiques 256 bits, vérification ultra-rapide |
| **Empreintes & Hachage** | SHA-256 & SHA-512 | Résistant aux collisions |
| **Clé de Récupération BitLocker** | Générateur pseudo-aléatoire cryptographique | 48 chiffres décimaux regroupés en 8 blocs |

---

## 3. Registres PCR TPM 2.0 (Measured Boot)

NovaOS enregistre chaque étape dans les registres PCR :
- **PCR[0]** : Firmware de la carte mère (UEFI)
- **PCR[1]** : Configuration de la plateforme matérielle
- **PCR[2]** : ROMs d'extension (Cartes graphiques, contrôleurs NVMe)
- **PCR[4]** : Chargeur de démarrage Stage 1 & Stage 2
- **PCR[7]** : Politique Secure Boot et clés PK, KEK, db
- **PCR[8]** : Ligne de commande et arguments de durcissement du noyau
- **PCR[9]** : Initramfs et modules de sécurité Nova Defender

---

## 4. Signalement de Vulnérabilités
Pour signaler une vulnérabilité dans le code de NovaOS, veuillez ouvrir une issue de sécurité privée sur le dépôt GitHub officiel.
