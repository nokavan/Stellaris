#!/usr/bin/env python3
"""Генерирует плейсхолдер-графику мода и добавляет BOM в файлы локализации.

Запуск из корня репозитория:  python3 tools/build_assets.py
Требуется Pillow (pip install pillow). Замените DDS своими артами, когда будут готовы.
"""
import math
import pathlib

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent

RED = (178, 34, 34, 255)
GOLD = (214, 175, 82, 255)
DARK = (18, 22, 20, 255)
GREEN = (34, 60, 40, 255)


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def forest(draw, w, h, base, color, count, seed=1):
    step = w / count
    for i in range(count):
        x = i * step + (seed * 7 + i * 13) % int(step / 2 + 1)
        th = h * (0.25 + ((i * 37 + seed * 11) % 40) / 100)
        draw.polygon([(x, base), (x + step * 0.6, base - th), (x + step * 1.2, base)], fill=color)


def icon(kind, size=128):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.ellipse([2, 2, s - 3, s - 3], fill=DARK, outline=GOLD, width=max(2, s // 32))
    c = s / 2
    if kind == "star":
        d.polygon(star_points(c, c, s * 0.36, s * 0.15), fill=RED)
    elif kind == "eye":
        d.ellipse([s * 0.18, s * 0.32, s * 0.82, s * 0.68], fill=GOLD)
        d.ellipse([s * 0.38, s * 0.38, s * 0.62, s * 0.62], fill=RED)
        d.ellipse([s * 0.46, s * 0.46, s * 0.54, s * 0.54], fill=DARK)
    elif kind == "crown":
        d.polygon([(s * .22, s * .66), (s * .22, s * .36), (s * .36, s * .5), (s * .5, s * .3),
                   (s * .64, s * .5), (s * .78, s * .36), (s * .78, s * .66)], fill=GOLD)
        d.polygon(star_points(c, s * 0.56, s * 0.08, s * 0.035), fill=RED)
    elif kind == "tree":
        forest(d, s * 0.6, s * 0.5, s * 0.72, GREEN, 3)
        d.polygon(star_points(c, s * 0.3, s * 0.12, s * 0.05), fill=RED)
        img = img  # keep
    elif kind == "press":
        d.rectangle([s * .25, s * .3, s * .75, s * .72], fill=GOLD)
        for i in range(4):
            y = s * (.38 + i * .08)
            d.line([s * .3, y, s * .7, y], fill=DARK, width=max(1, s // 40))
        d.polygon(star_points(s * .7, s * .3, s * .1, s * .04), fill=RED)
    elif kind == "net":
        pts = [(c + s * .3 * math.cos(math.radians(a)), c + s * .3 * math.sin(math.radians(a)))
               for a in range(0, 360, 60)]
        for p in pts:
            d.line([c, c, p[0], p[1]], fill=GOLD, width=max(1, s // 32))
            r = s * .06
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=RED)
        r = s * .09
        d.ellipse([c - r, c - r, c + r, c + r], fill=GOLD)
    return img


def scene(w, h, accent, seed):
    img = Image.new("RGBA", (w, h), DARK)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([0, y, w, y], fill=(int(20 + 40 * t), int(18 + 10 * t), int(30 + 10 * t), 255))
    # звёзды
    for i in range(120):
        x = (i * 97 + seed * 31) % w
        y = (i * 53 + seed * 17) % int(h * 0.6)
        d.point((x, y), fill=(220, 220, 255, 255))
    d.ellipse([w * .7, h * .08, w * .7 + h * .3, h * .38], fill=accent)
    forest(d, w, h * .8, h, (10, 30, 18, 255), 24, seed)
    forest(d, w, h * .6, h, (5, 15, 10, 255), 30, seed + 3)
    d.polygon(star_points(w * .15, h * .3, h * .12, h * .05), fill=RED)
    return img.filter(ImageFilter.SMOOTH)


def save_dds(img, rel):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGBA").save(p, format="DDS")


def main():
    save_dds(icon("star", 64), "gfx/interface/icons/origins/origin_ps_partisan_legacy.dds")
    save_dds(scene(450, 150, (150, 60, 40, 255), 1), "gfx/interface/icons/origins/ps_origin_picture.dds")
    save_dds(icon("net", 64), "gfx/interface/icons/governments/civics/civic_ps_partisan_network.dds")
    save_dds(icon("crown", 64), "gfx/interface/icons/governments/civics/civic_ps_shadow_overlord.dds")
    save_dds(icon("tree", 52), "gfx/interface/icons/technologies/tech_ps_guerrilla_doctrine.dds")
    save_dds(icon("eye", 52), "gfx/interface/icons/technologies/tech_ps_ghost_networks.dds")
    save_dds(icon("star", 128), "gfx/interface/icons/buildings/building_ps_partisan_cell.dds")
    save_dds(icon("press", 128), "gfx/interface/icons/buildings/building_ps_underground_press.dds")
    save_dds(icon("star", 32), "gfx/interface/icons/modifiers/mod_ps_partisan.dds")
    save_dds(scene(450, 150, (170, 40, 30, 255), 2), "gfx/event_pictures/ps_evt_partisans.dds")
    save_dds(scene(450, 150, (60, 80, 140, 255), 3), "gfx/event_pictures/ps_evt_spy.dds")
    save_dds(scene(450, 150, (200, 160, 70, 255), 4), "gfx/event_pictures/ps_evt_syndicate.dds")

    thumb = scene(512, 512, (170, 40, 30, 255), 5).convert("RGB")
    ImageDraw.Draw(thumb).polygon(star_points(256, 200, 120, 48), fill=RED[:3])
    thumb.save(ROOT / "thumbnail.png")

    # Stellaris требует UTF-8 с BOM для .yml
    for yml in (ROOT / "localisation").rglob("*.yml"):
        raw = yml.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            yml.write_bytes(b"\xef\xbb\xbf" + raw)
    print("ok")


if __name__ == "__main__":
    main()
