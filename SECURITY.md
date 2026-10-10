# 🔒 Politique de sécurité de NovaOS

NovaOS est construite sur **Debian 13 « trixie »** et durcie par défaut. Ce document détaille les mesures en place, les choix de conception, leurs limites et les recommandations.

---

## 1. Modèle de menaces

NovaOS cible un **poste de travail personnel** (machine physique ou VM), potentiellement exposé à :

- un **réseau non fiable** (Wi-Fi public, LAN hostile) ;
- un **accès physique** à la machine (vol, emprunt, « evil maid ») ;
- des **comptes non privilégiés compromis** (navigation, logiciels tiers) ;
- une **divulgation de données au repos** (disque volé / non chiffré).

Ce document ne couvre pas : la sécurité du matériel (firmware, Secure Boot non signé), la sécurité en entreprise (MDM, 802.1X, annuaire), ni la sécurité des applications tierces.

## 2. Mesures en place par défaut

### 2.1 Pare-feu

- **UFW** est installé et **activé** (`ENABLED=yes` dans `/etc/ufw/ufw.conf`).
- Politique par défaut : **tout entrant refusé**, sortant autorisé.
- Aucun port n'est ouvert (aucun serveur SSH, aucun service d'accès à distance).
- Interface graphique de gestion : **Gufw** (menu « Pare-feu »).

### 2.2 Mises à jour automatiques

- **unattended-upgrades** : les mises à jour de **sécurité** et les **correctifs** du dépôt `trixie-updates` s'installent automatiquement (`/etc/apt/apt.conf.d/52unattended-upgrades-novaos`).
- `APT::Periodic::Update-Package-Lists "1"` : les listes de paquets sont rafraîchies chaque jour.
- Pas de redémarrage automatique (`Automatic-Reboot "false"`) — l'utilisateur est averti.
- APT est durci : `AllowInsecureRepositories=false`, `AllowUnauthenticated=false` (`/etc/apt/apt.conf.d/99novaos-hardening`).

### 2.3 Politique de mots de passe

- **libpam-pwquality** : minimum **12 caractères**, au moins 1 chiffre, 1 majuscule, 1 minuscule, 1 caractère spécial, pas de répétition (3 max), pas de séquence, pas de sous-chaînes du login (3+), vérification GECOS, `retry=3`, appliqué aussi à root.
- **login.defs** : `PASS_MAX_DAYS=90`, `PASS_MIN_DAYS=1`, `PASS_WARN_AGE=14`, `LOGIN_RETRIES=5`, `LOGIN_TIMEOUT=60`, `FAIL_DELAY=4`, `UMASK=027`.
- Le mot de passe root est défini à l'installation (Calamares `setRootPassword: true`) — pas de compte root sans mot de passe.

### 2.4 Durcissement du noyau (sysctl)

`/etc/sysctl.d/99-novaos-hardening.conf` :

- `kernel.kptr_restrict=2`, `kernel.dmesg_restrict=1` — pas de fuites d'adresses noyau
- `kernel.unprivileged_bpf_disabled=1` — BPF non privilégié désactivé
- `kernel.yama.ptrace_scope=2` — `ptrace` réservé à l'administrateur
- `kernel.kexec_load_disabled=1` — pas de remplacement de noyau à chaud
- `kernel.unprivileged_userns_clone=0` + `kernel.apparmor_restrict_unprivileged_userns=1` — user namespaces non privilégiés restreints (si supporté par le noyau)
- `vm.mmap_min_addr=65536`, `kernel.randomize_va_space=2`
- `fs.protected_hardlinks/symlinks/fifos/regular` — protections symlink/hardlink
- Réseau : `rp_filter=1`, redirections ICMP refusées, `log_martians`, `tcp_syncookies=1`, `tcp_rfc1337=1`

### 2.5 AppArmor

- `apparmor`, `apparmor-profiles` et `apparmor-utils` sont installés ; le service AppArmor est activé.
- Les profils fournis par Debian s'appliquent automatiquement. Pour enforcer un profil en mode *enforce* : `sudo aa-enforce /etc/apparmor.d/<profil>`.

### 2.6 Journaux et coredumps

- **Coredumps désactivés** : `/etc/systemd/coredump.conf.d/novaos.conf` (`Storage=none`) — pas de fuite de mémoire (mots de passe, clés) dans des fichiers core.
- **Journaux bornés** : `SystemMaxUse=500M`, `RuntimeMaxUse=100M`, rétention 1 mois.

### 2.7 Verrouillage de l'écran

`/etc/xdg/kscreenlockrc` (applicable à tous les utilisateurs) :

- verrouillage automatique après **5 minutes** d'inactivité ;
- verrouillage **au réveil** de la mise en veille (`LockOnResume=true`) ;
- pas de « grâce » sans mot de passe (`LockGrace=0`).

Raccourci : `Ctrl+Alt+L`.

### 2.8 Connexion automatique (choix de l'utilisateur)

L'utilisateur a explicitement demandé un démarrage automatique sur le bureau : SDDM ouvre la session de l'utilisateur principal **sans mot de passe au démarrage**.

Compensations mises en place :

- `Relogin=false` : après une **déconnexion**, l'écran de connexion (mot de passe) réapparaît ;
- verrouillage écran 5 min + au réveil (2.7) ;
- **désactivation en une ligne** : `NOVAOS_AUTOLOGIN=false` dans `/etc/novaos/autologin.conf` puis redémarrage ;
- le service `novaos-autologin-setup.service` ne s'applique qu'au **premier** compte humain (uid ≥ 1000) — jamais à un compte système.

> ⚠️ Sur un ordinateur portable nomade, pensez à désactiver l'autologin et à activer le chiffrement LUKS.

### 2.9 Compte « live » de l'ISO

- L'ISO live démarre avec l'utilisateur `user` (mot de passe `live`, standard des ISO live Debian) — **ne boottez pas de clé USB inconnue sur une machine contenant des données sensibles sans chiffrement**.
- Sur le **système installé**, le service `novaos-firstboot.service` **verrouille** le compte `user` (mot de passe verrouillé + shell `nologin`) dès qu'un autre compte principal existe.

### 2.10 Chiffrement

- L'installateur Calamares propose le **chiffrement LUKS complet du disque** à l'installation (étape partitionnement → « Effacer le disque » → cocher « Chiffrer »).
- Les microcodes CPU sont à jour (`intel-microcode`, `amd64-microcode`).
- Le dépôt `non-free-firmware` est activé (pilotes Wi-Fi/SSD récents, nécessaires aussi pour la sécurité matérielle).

### 2.11 Surface réseau minimale

- **openssh-server n'est pas installé** : aucun accès à distance par défaut.
- Seul `openssh-client` est présent.
- Bluetooth et Wi-Fi sont gérés par l'utilisateur ; le Wi-Fi utilise NetworkManager (MAC aléatoire par défaut).

## 3. Limites connues

- **Secure Boot** : l'ISO n'est pas signée. Sur une machine avec Secure Boot actif, désactivez-le temporairement dans l'UEFI (ou enregistrez les clés — non automatisé ici).
- **L'autologin** est une porte ouverte physique si la machine n'est pas chiffrée — c'est un choix explicite de l'utilisateur, documenté ci-dessus.
- **Le noyau Debian** reçoit les correctifs de sécurité via les mises à jour automatiques ; un redémarrage est nécessaire pour appliquer un nouveau noyau.
- **AppArmor** : les profils Debian sont en mode *complain* par défaut pour certains ; l'enforcement se fait au cas par cas (`aa-enforce`).
- **Pare-feu** : UFW filtre IPv4 et IPv6, mais ne remplace pas le chiffrement des communications (TLS/HTTPS, VPN).

## 4. Recommandations

1. **Chiffrez le disque (LUKS)** à l'installation — c'est la mesure la plus efficace contre le vol.
2. **Verrouillez la session** (`Ctrl+Alt+L`) quand vous vous éloignez.
3. **Désactivez l'autologin** sur un portable : `sudo sed -i 's/NOVAOS_AUTOLOGIN=true/NOVAOS_AUTOLOGIN=false/' /etc/novaos/autologin.conf && sudo reboot`.
4. Gardez les mises à jour automatiques actives ; redémarrez régulièrement.
5. Activez **chiffrement du navigateur** (Firefox Lockwise) et un gestionnaire de mots de passe.
6. Surveillez le pare-feu : `sudo ufw status verbose`.
7. Optionnel : installez `clamav`, `rkhunter` et `lynis` pour des audits ponctuels :
   `sudo apt install clamav rkhunter lynis`

## 5. Signaler une vulnérabilité

Ouvrez un ticket privé via [GitHub Security Advisories](https://github.com/Haseosama/NovaOS/security/advisories/new) ou un ticket public : https://github.com/Haseosama/NovaOS/issues

---

*Document maintenu avec le projet — dernière mise à jour : 2026-10.*
