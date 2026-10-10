/*
 * NovaOS — thème SDDM « novaos »
 * Écran de connexion futuriste, inspiré de l'esthétique Windows 11 :
 * fond sombre, panneau « verre dépoli », accent bleu électrique #0078D4.
 *
 * Chaînes en français (modifiez-les ici pour traduire le thème).
 */
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Window 2.15
import SddmComponents 2.0

Rectangle {
    id: root

    // — Palette NovaOS —
    readonly property color novaAccent:      "#0078d4"
    readonly property color novaAccentLight: "#3daee9"
    readonly property color novaText:        "#eff0f1"
    readonly property color novaTextDim:     "#9ca3af"
    readonly property color novaPanel:       "#2b1b2440" // verre sombre (AARRGGBB)
    readonly property color novaField:       "#cc0f1420" // champ de saisie (AARRGGBB)

    width: Screen.width
    height: Screen.height
    color: "#0b0e1a"

    // — Fond d'écran —
    Image {
        id: background
        anchors.fill: parent
        source: "background.jpg"
        fillMode: Image.PreserveAspectCrop
        smooth: true
        mipmap: true
    }

    // Voile sombre pour la lisibilité
    Rectangle {
        anchors.fill: parent
        color: "#8c0b0e1a"
    }

    // — Horloge (haut, centrée) —
    ColumnLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: root.height * 0.10
        spacing: 6

        QQC2.Label {
            id: timeLabel
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: Math.round(root.height * 0.11)
            font.weight: Font.Light
            color: root.novaText
        }

        QQC2.Label {
            id: dateLabel
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: Math.round(root.height * 0.022)
            color: root.novaTextDim
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: {
                var locale = Qt.locale("fr_FR")
                timeLabel.text = Qt.formatDateTime(new Date(), "HH:mm", locale)
                dateLabel.text = Qt.formatDateTime(new Date(), "dddd d MMMM yyyy", locale)
            }
        }
    }

    // — Carte de connexion « verre dépoli » —
    Rectangle {
        id: loginCard
        width: Math.min(400, root.width * 0.86)
        height: cardContent.implicitHeight + 56
        anchors.centerIn: parent
        anchors.verticalCenterOffset: root.height * 0.05
        radius: 18
        color: root.novaPanel
        border.color: "#330078d4"
        border.width: 1

        ColumnLayout {
            id: cardContent
            anchors.fill: parent
            anchors.margins: 28
            spacing: 14

            // Logo NovaOS
            Image {
                Layout.alignment: Qt.AlignHCenter
                source: "/usr/share/novaos/novaos-logo.png"
                width: 72
                height: 72
                fillMode: Image.PreserveAspectFit
                smooth: true
            }

            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: "NovaOS"
                font.pixelSize: 22
                font.bold: true
                color: root.novaText
            }

            // Nom d'utilisateur
            SddmComponents.TextBox {
                id: userName
                Layout.fillWidth: true
                text: sddm.lastUser
                placeholderText: "Nom d'utilisateur"
                placeholderTextColor: root.novaTextDim
                color: root.novaText
                font.pixelSize: 15
                selectByMouse: true
                background: Rectangle {
                    radius: 10
                    color: root.novaField
                    border.color: userName.activeFocus ? root.novaAccent : "#26ffffff"
                    border.width: 1
                }
                onAccepted: password.forceActiveFocus()
            }

            // Mot de passe
            SddmComponents.PasswordBox {
                id: password
                Layout.fillWidth: true
                placeholderText: "Mot de passe"
                placeholderTextColor: root.novaTextDim
                color: root.novaText
                font.pixelSize: 15
                selectByMouse: true
                background: Rectangle {
                    radius: 10
                    color: root.novaField
                    border.color: password.activeFocus ? root.novaAccent : "#26ffffff"
                    border.width: 1
                }
                onAccepted: tryLogin()
            }

            // Message d'erreur
            QQC2.Label {
                id: errorLabel
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: ""
                color: "#f48771"
                font.pixelSize: 13
            }

            // Bouton de connexion
            SddmComponents.Button {
                id: loginButton
                Layout.fillWidth: true
                text: "Se connecter"
                font.bold: true
                onClicked: tryLogin()
                background: Rectangle {
                    radius: 10
                    color: loginButton.hovered ? root.novaAccentLight : root.novaAccent
                }
                contentItem: QQC2.Label {
                    text: loginButton.text
                    font: loginButton.font
                    color: "#ffffff"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Sélecteur de session (Plasma Wayland par défaut)
            SddmComponents.ComboBox {
                id: sessionCombo
                Layout.fillWidth: true
                model: sddm.sessions
                textRole: "name"
                font.pixelSize: 13
                currentIndex: 0
                Component.onCompleted: {
                    for (var i = 0; i < model.length; ++i) {
                        var s = model[i]
                        var f = ""
                        if (s.desktopFile !== undefined) { f = s.desktopFile }
                        else if (s.desktopSession !== undefined) { f = s.desktopSession }
                        else if (s.name !== undefined) { f = s.name }
                        if (String(f).indexOf("plasma") !== -1) {
                            currentIndex = i
                            break
                        }
                    }
                }
            }
        }
    }

    // — Boutons d'alimentation (bas, à droite) —
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 12

        QQC2.Button {
            text: "Suspendre"
            visible: sddm.canSuspend
            onClicked: sddm.suspend()
        }
        QQC2.Button {
            text: "Redémarrer"
            visible: sddm.canReboot
            onClicked: sddm.reboot()
        }
        QQC2.Button {
            text: "Éteindre"
            visible: sddm.canPowerOff
            onClicked: sddm.powerOff()
        }
    }

    // — Connexion —
    function tryLogin() {
        errorLabel.text = ""
        var idx = sessionCombo.currentIndex >= 0 ? sessionCombo.currentIndex : 0
        sddm.login(userName.text, password.text, idx)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            errorLabel.text = "Échec de la connexion : vérifiez votre nom d'utilisateur et votre mot de passe."
            password.text = ""
            password.forceActiveFocus()
        }
        function onLoginSucceeded() {
            errorLabel.text = ""
        }
    }

    Component.onCompleted: {
        var locale = Qt.locale("fr_FR")
        timeLabel.text = Qt.formatDateTime(new Date(), "HH:mm", locale)
        dateLabel.text = Qt.formatDateTime(new Date(), "dddd d MMMM yyyy", locale)
        if (userName.text.length > 0) {
            password.forceActiveFocus()
        } else {
            userName.forceActiveFocus()
        }
    }
}
