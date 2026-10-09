# NovaOS — infos système « futuristes » à l'ouverture d'un terminal (shell de login)
# Désactiver : export NOVAOS_NO_FETCH=1 dans ~/.bashrc
#              ou créer le fichier ~/.config/novaos/no-fetch
if [ -n "${PS1:-}" ] && [ -z "${NOVAOS_NO_FETCH:-}" ] && [ ! -f "${HOME:-/root}/.config/novaos/no-fetch" ]; then
    if command -v fastfetch >/dev/null 2>&1; then
        fastfetch
    elif command -v neofetch >/dev/null 2>&1; then
        neofetch
    fi
fi
