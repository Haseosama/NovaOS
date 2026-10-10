// NovaOS — disposition par défaut du bureau (exécutée par Plasma à la
// première ouverture de session d'un compte, quand aucune configuration
// n'existe encore).
//
// Barre des tâches façon Windows 11 : flottante, en bas, contenu centré
//   [espace] [Démarrer] [applications épinglées / ouvertes] [espace]
//   [zone de notification] [horloge] [afficher le bureau]

// --- Bureau : fond d'écran NovaOS « Bloom » ---
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {
    var d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/NovaOS-Bloom/contents/images/1920x1080.jpg");
}

// --- Barre des tâches ---
var panel = new Panel;
panel.location = "bottom";
panel.height = 2 * Math.ceil(gridUnit * 2.6 / 2);
panel.hiding = "none";
try { panel.floating = true; } catch (e) { /* Plasma < 6 */ }
// Verre liquide : barre toujours translucide (floutée par KWin)
try { panel.opacity = "translucent"; } catch (e) { }

panel.addWidget("org.kde.plasma.panelspacer");

// Menu Démarrer (s'ouvre aussi avec la touche Windows/Meta)
var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["Shortcuts"];
kickoff.writeConfig("global", "Alt+F1");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "/usr/share/novaos/novaos-logo.svg");

// Applications épinglées (icônes seules, comme Windows 11)
var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:firefox-esr.desktop",
    "applications:novaos-explorer.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
].join(","));

panel.addWidget("org.kde.plasma.panelspacer");

panel.addWidget("org.kde.plasma.systemtray");

var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateDisplayFormat", "BelowTime");

panel.addWidget("org.kde.plasma.showdesktop");
