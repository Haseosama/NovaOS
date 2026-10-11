/*
 * NovaOS — écran de chargement de la session (remplace le splash KDE).
 * Fond sombre, logo NovaOS qui pulse, barre de progression bleue.
 * « stage » est fourni par ksplashqml (1 à 6).
 */
import QtQuick 2.15

Rectangle {
    id: root
    color: "#0b0e1a"

    property int stage

    Image {
        anchors.fill: parent
        source: "file:///usr/share/wallpapers/NovaOS-Bloom/contents/images/1920x1080.jpg"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.35
        asynchronous: true
    }

    Column {
        anchors.centerIn: parent
        spacing: 22

        Image {
            id: logo
            anchors.horizontalCenter: parent.horizontalCenter
            source: "file:///usr/share/novaos/novaos-logo.png"
            width: 112
            height: 112
            sourceSize.width: 224
            sourceSize.height: 224
            fillMode: Image.PreserveAspectFit
            smooth: true

            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 0.55; duration: 900; easing.type: Easing.InOutQuad }
                NumberAnimation { from: 0.55; to: 1.0; duration: 900; easing.type: Easing.InOutQuad }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "NovaOS"
            color: "#eff0f1"
            font.pixelSize: 30
            font.weight: Font.Light
            font.letterSpacing: 4
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 220
            height: 4
            radius: 2
            color: "#26ffffff"

            Rectangle {
                width: parent.width * Math.min(1, Math.max(0.08, root.stage / 6))
                height: parent.height
                radius: 2
                color: "#0078d4"
                Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
            }
        }
    }
}
