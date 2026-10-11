/*
 * NovaOS — widget « Système » : processeur et mémoire en anneaux néon.
 * Les mesures viennent de /usr/local/bin/novaos-sysinfo (lancé toutes les
 * 2 s par le moteur « executable » de Plasma) : aucune dépendance à
 * ksystemstats.
 */
import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root

    property int cpu: 0
    property int mem: 0
    property string memText: ""

    preferredRepresentation: fullRepresentation
    switchWidth: 1
    switchHeight: 1

    readonly property string command: "/usr/local/bin/novaos-sysinfo"

    P5Support.DataSource {
        id: sysinfo
        engine: "executable"
        connectedSources: [root.command]
        interval: 2000
        onNewData: function (source, data) {
            var parts = String(data["stdout"] || "").trim().split(/\s+/)
            if (parts.length >= 4) {
                root.cpu = parseInt(parts[0]) || 0
                root.mem = parseInt(parts[1]) || 0
                root.memText = parts[2] + " / " + parts[3] + " Go"
            }
        }
    }

    component Ring: Item {
        id: ring
        property real value: 0
        property string label: ""
        property string detail: ""
        property color tint: "#00d4ff"
        width: 120
        height: 150

        Canvas {
            id: canvas
            width: 110
            height: 110
            anchors.horizontalCenter: parent.horizontalCenter
            property real shown: ring.value
            Behavior on shown { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
            onShownChanged: requestPaint()
            onPaint: {
                var ctx = getContext("2d")
                ctx.reset()
                var c = width / 2, r = width / 2 - 8
                ctx.lineWidth = 9
                ctx.lineCap = "round"
                ctx.strokeStyle = "rgba(255,255,255,0.12)"
                ctx.beginPath(); ctx.arc(c, c, r, 0, 2 * Math.PI); ctx.stroke()
                ctx.strokeStyle = ring.tint
                ctx.beginPath()
                ctx.arc(c, c, r, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * Math.max(0.01, shown / 100))
                ctx.stroke()
            }
            Text {
                anchors.centerIn: parent
                text: Math.round(ring.value) + " %"
                color: "#eff0f1"
                font.pixelSize: 22
                font.weight: Font.Light
            }
        }
        Text {
            anchors.top: canvas.bottom
            anchors.topMargin: 6
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
            text: ring.label + (ring.detail ? "\n" + ring.detail : "")
            color: "#9fb3c8"
            font.pixelSize: 12
        }
    }

    fullRepresentation: Item {
        implicitWidth: 280
        implicitHeight: 180
        Row {
            anchors.centerIn: parent
            spacing: 18
            Ring { value: root.cpu; label: "Processeur"; tint: "#00d4ff" }
            Ring { value: root.mem; label: "Mémoire"; detail: root.memText; tint: "#8b5cf6" }
        }
    }
}
