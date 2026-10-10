/*
 * NovaOS — thème SDDM « novaos »
 * Écran de connexion futuriste, inspiré de l'esthétique Windows 11 :
 * fond sombre, panneau « verre dépoli », accent bleu électrique #0078D4.
 *
 * Chaînes en français (modifiez-les ici pour traduire le thème).
 *
 * Uniquement QtQuick.Controls (pas de SddmComponents : son import sans
 * alias cassait le thème sous Qt 6). Objets fournis par SDDM : sddm, userModel,
 * sessionModel.
 */
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Window 2.15

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
                timeLabel.text = new Date().toLocaleTimeString(locale, "HH:mm")
                dateLabel.text = new Date().toLocaleDateString(locale, "dddd d MMMM yyyy")
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
                // Taille imposée : dans un ColumnLayout, width/height sont
                // ignorés et l'image (1024 px) envahissait tout l'écran.
                Layout.preferredWidth: 72
                Layout.preferredHeight: 72
                sourceSize.width: 144
                sourceSize.height: 144
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
            QQC2.TextField {
                id: userName
                Layout.fillWidth: true
                text: userModel.lastUser
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
            QQC2.TextField {
                id: password
                echoMode: TextInput.Password
                passwordCharacter: "●"
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
            QQC2.Button {
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
            QQC2.ComboBox {
                id: sessionCombo
                Layout.fillWidth: true
                model: sessionModel
                textRole: "name"
                font.pixelSize: 13
                background: Rectangle {
                    radius: 10
                    color: root.novaField
                    border.color: sessionCombo.activeFocus ? root.novaAccent : "#26ffffff"
                    border.width: 1
                }
                contentItem: QQC2.Label {
                    leftPadding: 12
                    text: sessionCombo.displayText
                    font: sessionCombo.font
                    color: root.novaTextDim
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
                // Dernière session utilisée (Plasma Wayland par défaut)
                currentIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
            }
        }
    }

    // — Boutons d'alimentation (bas, à droite) —
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 12

        PowerButton {
            text: "Suspendre"
            visible: sddm.canSuspend
            onClicked: sddm.suspend()
        }
        PowerButton {
            text: "Redémarrer"
            visible: sddm.canReboot
            onClicked: sddm.reboot()
        }
        PowerButton {
            text: "Éteindre"
            visible: sddm.canPowerOff
            onClicked: sddm.powerOff()
        }
    }

    // Bouton d'alimentation « verre » (bas de l'écran)
    component PowerButton: QQC2.Button {
        id: pb
        font.pixelSize: 13
        padding: 10
        background: Rectangle {
            radius: 10
            color: pb.hovered ? "#400078d4" : "#26ffffff"
            border.color: "#33ffffff"
            border.width: 1
        }
        contentItem: QQC2.Label {
            text: pb.text
            font: pb.font
            color: root.novaText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
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
        timeLabel.text = new Date().toLocaleTimeString(locale, "HH:mm")
        dateLabel.text = new Date().toLocaleDateString(locale, "dddd d MMMM yyyy")
        if (userName.text.length > 0) {
            password.forceActiveFocus()
        } else {
            userName.forceActiveFocus()
        }
    }
}
