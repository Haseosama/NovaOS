// NovaOS — disposition par défaut du bureau (exécutée par Plasma à la
// première ouverture de session d'un compte, quand aucune configuration
// n'existe encore).
//
// La partie « barre des tâches » est une copie de /usr/share/novaos/novaos-panel.js
// (gardez les deux identiques).

// --- Bureau : fond d'écran NovaOS « Bloom » ---
try {
    var allDesktops = desktops();
    for (var i = 0; i < allDesktops.length; i++) {
        var d = allDesktops[i];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        d.writeConfig("Image", "file:///usr/share/wallpapers/NovaOS-Bloom/contents/images/1920x1080.jpg");
    }
} catch (e) {
    print("NovaOS: fond d'écran : " + e);
}

// --- Barre des tâches ---
function novaTry(label, fn) {
    try { fn(); } catch (e) { print("NovaOS: " + label + " : " + e); }
}

function novaCreatePanel() {
    var panel = new Panel;
    novaTry("emplacement", function () { panel.location = "bottom"; });
    novaTry("hauteur", function () {
        var gu = (typeof gridUnit === "number" && gridUnit > 0) ? gridUnit : 18;
        panel.height = 2 * Math.ceil(gu * 2.6 / 2);
    });
    novaTry("masquage", function () { panel.hiding = "none"; });
    novaTry("flottante", function () { panel.floating = true; });
    // Verre liquide : barre toujours translucide (floutée par KWin)
    novaTry("opacité", function () { panel.opacity = "translucent"; });

    novaTry("espace gauche", function () { panel.addWidget("org.kde.plasma.panelspacer"); });

    // Menu Démarrer (s'ouvre aussi avec la touche Windows/Meta)
    novaTry("menu Démarrer", function () {
        var kickoff = panel.addWidget("org.kde.plasma.kickoff");
        kickoff.currentConfigGroup = ["Shortcuts"];
        kickoff.writeConfig("global", "Alt+F1");
        kickoff.currentConfigGroup = ["General"];
        kickoff.writeConfig("icon", "/usr/share/novaos/novaos-logo.svg");
    });

    // Applications épinglées (icônes seules, comme Windows 11)
    novaTry("applications épinglées", function () {
        var tasks = panel.addWidget("org.kde.plasma.icontasks");
        tasks.currentConfigGroup = ["General"];
        tasks.writeConfig("launchers", [
            "applications:firefox-esr.desktop",
            "applications:novaos-explorer.desktop",
            "applications:org.kde.discover.desktop",
            "applications:org.kde.konsole.desktop",
            "applications:systemsettings.desktop"
        ].join(","));
    });

    novaTry("espace droit", function () { panel.addWidget("org.kde.plasma.panelspacer"); });
    novaTry("zone de notification", function () { panel.addWidget("org.kde.plasma.systemtray"); });

    novaTry("horloge", function () {
        var clock = panel.addWidget("org.kde.plasma.digitalclock");
        clock.currentConfigGroup = ["Appearance"];
        clock.writeConfig("showDate", true);
        clock.writeConfig("dateDisplayFormat", "BelowTime");
    });

    novaTry("afficher le bureau", function () { panel.addWidget("org.kde.plasma.showdesktop"); });
    print("NovaOS: barre des tâches créée");
}

// Widgets du bureau (en haut à droite, style verre du thème NovaGlass) :
// grande horloge, processeur, mémoire. Ajoutés seulement avec une barre neuve.
function novaDesktopWidgets() {
    var ds = [];
    novaTry("bureaux", function () { ds = desktops(); });
    if (ds.length === 0) { return; }
    var d = ds[0];
    var sw = 1920;
    novaTry("taille d'écran", function () {
        var g = screenGeometry(d.screen);
        if (g && g.width > 0) { sw = g.width; }
    });
    var w = 300, x = sw - w - 32;
    novaTry("horloge du bureau", function () {
        var c = d.addWidget("org.kde.plasma.digitalclock", x, 40, w, 150);
        c.currentConfigGroup = ["Appearance"];
        c.writeConfig("showDate", true);
        c.writeConfig("dateDisplayFormat", "BelowTime");
    });
    novaTry("processeur", function () { d.addWidget("org.kde.plasma.systemmonitor.cpu", x, 210, w, 190); });
    novaTry("mémoire", function () { d.addWidget("org.kde.plasma.systemmonitor.memory", x, 420, w, 190); });
}

// Une barre existe déjà ? On n'y touche pas (l'utilisateur l'a peut-être
// personnalisée). Sinon on la crée.
var novaPanels = [];
novaTry("liste des barres", function () { novaPanels = panels(); });
if (novaPanels.length === 0) {
    novaCreatePanel();
    novaDesktopWidgets();
} else {
    print("NovaOS: " + novaPanels.length + " barre(s) déjà présente(s)");
}
