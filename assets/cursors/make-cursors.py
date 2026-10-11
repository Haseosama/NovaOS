#!/usr/bin/env python3
"""NovaOS — génère les images du curseur « NovaOS » (PNG + fichiers xcursorgen).

Exécuté une fois par les développeurs (PySide6) ; les PNG produits sont
versionnés dans config/includes.chroot/usr/share/novaos/cursors-src/ et
assemblés en Xcursor par le hook 0120 (xcursorgen) pendant la construction.
Usage : python3 make-cursors.py <dossier de sortie>
"""
import math, os, sys
from PySide6.QtGui import (QGuiApplication, QImage, QPainter, QColor, QPen, QPainterPath,
                           QLinearGradient, QBrush)
from PySide6.QtCore import Qt, QPointF, QRectF

SIZES = [24, 32, 48, 64]
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
app = QGuiApplication([])

def grad(s):
    g = QLinearGradient(0, 0, s, s)
    g.setColorAt(0, QColor("#00e5ff")); g.setColorAt(1, QColor("#8b5cf6"))
    return g

def canvas(s):
    img = QImage(s, s, QImage.Format_ARGB32); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.scale(s / 64.0, s / 64.0)
    return img, p

def stroke_glow(p, path, width=3.0):
    for w, a in ((width + 5, 40), (width + 2.5, 70)):
        p.setPen(QPen(QColor(0, 229, 255, a), w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.drawPath(path)
    p.setPen(QPen(QBrush(grad(64)), width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.drawPath(path)

FILL = QColor(10, 16, 32, 235)

def arrow(p):
    path = QPainterPath(QPointF(6, 4))
    for x, y in ((6, 46), (17, 36), (25, 54), (33, 50), (25, 33), (40, 33)):
        path.lineTo(x, y)
    path.closeSubpath()
    p.fillPath(path, FILL); stroke_glow(p, path, 2.6)

def hand(p):
    path = QPainterPath()
    path.addRoundedRect(QRectF(20, 4, 9, 30), 4.5, 4.5)
    body = QPainterPath(); body.addRoundedRect(QRectF(14, 26, 34, 30), 10, 10)
    path = path.united(body)
    for x in (29, 36, 43):
        f = QPainterPath(); f.addRoundedRect(QRectF(x - 0.5, 20, 7, 18), 3.5, 3.5); path = path.united(f)
    p.fillPath(path, FILL); stroke_glow(p, path, 2.4)

def ibeam(p):
    path = QPainterPath(QPointF(22, 8)); path.lineTo(30, 8); path.moveTo(34, 8); path.lineTo(42, 8)
    path.moveTo(32, 10); path.lineTo(32, 54)
    path.moveTo(22, 56); path.lineTo(30, 56); path.moveTo(34, 56); path.lineTo(42, 56)
    stroke_glow(p, path, 3.0)

def cross(p):
    path = QPainterPath(QPointF(32, 6)); path.lineTo(32, 24); path.moveTo(32, 40); path.lineTo(32, 58)
    path.moveTo(6, 32); path.lineTo(24, 32); path.moveTo(40, 32); path.lineTo(58, 32)
    stroke_glow(p, path, 2.6)
    c = QPainterPath(); c.addEllipse(QPointF(32, 32), 3, 3); p.fillPath(c, QColor("#00e5ff"))

def forbidden(p):
    c = QPainterPath(); c.addEllipse(QPointF(32, 32), 20, 20)
    p.fillPath(c, FILL); stroke_glow(p, c, 3)
    l = QPainterPath(QPointF(18, 46)); l.lineTo(46, 18); stroke_glow(p, l, 3)

def ring(p, phase, with_arrow=False):
    cx, cy, r = (44, 44, 13) if with_arrow else (32, 32, 20)
    if with_arrow:
        p.save(); p.scale(0.8, 0.8); arrow(p); p.restore()
    p.setPen(QPen(QColor(255, 255, 255, 40), 5)); p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(cx, cy), r, r)
    pen = QPen(QBrush(grad(64)), 5, Qt.SolidLine, Qt.RoundCap); p.setPen(pen)
    p.drawArc(QRectF(cx - r, cy - r, 2 * r, 2 * r), int(-phase * 16), int(-110 * 16))

# nom -> (fonction, hotspot sur 64, alias Xcursor)
STATIC = {
    "left_ptr": (arrow, (6, 4), ["default", "arrow", "top_left_arrow", "left_arrow"]),
    "pointer": (hand, (24, 4), ["hand1", "hand2", "pointing_hand", "openhand", "e29285e634086352946a0e7090d73106", "9d800788f1b08800ae810202380a0822"]),
    "xterm": (ibeam, (32, 32), ["text", "ibeam"]),
    "crosshair": (cross, (32, 32), ["cross", "tcross", "cell"]),
    "not-allowed": (forbidden, (32, 32), ["forbidden", "crossed_circle", "no-drop", "circle", "03b6e0fcb3499374a867c041f52298f0"]),
}
FRAMES = 12

def render(name, fn, hot, frames=None):
    lines = []
    for s in SIZES:
        if frames is None:
            img, p = canvas(s); fn(p); p.end()
            f = f"{name}-{s}.png"; img.save(os.path.join(OUT, f))
            lines.append(f"{s} {round(hot[0]*s/64)} {round(hot[1]*s/64)} {f}")
        else:
            for i in range(frames):
                img, p = canvas(s); fn(p, i * 360 / frames); p.end()
                f = f"{name}-{s}-{i:02d}.png"; img.save(os.path.join(OUT, f))
                lines.append(f"{s} {round(hot[0]*s/64)} {round(hot[1]*s/64)} {f} 60")
    open(os.path.join(OUT, f"{name}.cfg"), "w").write("\n".join(lines) + "\n")

aliases = {}
for name, (fn, hot, al) in STATIC.items():
    render(name, fn, hot); aliases[name] = al
render("watch", lambda p, ph: ring(p, ph), (32, 32), FRAMES); aliases["watch"] = ["wait"]
render("left_ptr_watch", lambda p, ph: ring(p, ph, True), (5, 3), FRAMES)
aliases["left_ptr_watch"] = ["progress", "half-busy", "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"]
with open(os.path.join(OUT, "aliases"), "w") as fh:
    for k, v in aliases.items():
        fh.write(k + " " + " ".join(v) + "\n")
print("ok", len(os.listdir(OUT)))
