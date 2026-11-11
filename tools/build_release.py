#!/usr/bin/env python3
"""Собирает архив мода для установки: releases/partisan_syndicate.zip

Также собирает необязательные патчи из compat/<имя>/:
  releases/partisan_syndicate_vanilla_ui_patch.zip   — окно стоянки для игры БЕЗ UIOD
  releases/partisan_syndicate_xhk_worldark_patch.zip — интеграция с XHK World Ark

Структура архива (распаковать в Документы/Paradox Interactive/Stellaris/mod/):
  partisan_syndicate.mod        <- файл для лаунчера (с path="mod/partisan_syndicate")
  partisan_syndicate/...        <- сам мод (без vanilla_ref, tools и служебных файлов)

Запуск из корня репозитория:  python3 tools/build_release.py
"""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
INCLUDE = ["common", "events", "gfx", "interface", "localisation", "descriptor.mod", "thumbnail.png", "README.md"]
OUT = ROOT / "releases" / "partisan_syndicate.zip"


def main():
    OUT.parent.mkdir(exist_ok=True)
    descriptor = (ROOT / "descriptor.mod").read_text(encoding="utf-8").rstrip("\n")
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("partisan_syndicate.mod", descriptor + '\npath="mod/partisan_syndicate"\n')
        for item in INCLUDE:
            p = ROOT / item
            files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
            for f in files:
                z.write(f, "partisan_syndicate/" + f.relative_to(ROOT).as_posix())
                n += 1
    version = next(l.split('"')[1] for l in descriptor.splitlines() if l.startswith("version"))
    print(f"ok: {OUT.relative_to(ROOT)} — версия {version}, {n + 1} файлов, {OUT.stat().st_size // 1024} КБ")

    # Необязательные патчи совместимости: каждая папка compat/<имя>/ с descriptor.mod
    for patch in sorted(d for d in (ROOT / "compat").iterdir() if (d / "descriptor.mod").exists()):
        name = "partisan_syndicate_" + patch.name.replace("_waystation_patch", "_patch").replace("_patch", "") + "_patch"
        out = ROOT / "releases" / f"{name}.zip"
        pdesc = (patch / "descriptor.mod").read_text(encoding="utf-8").rstrip("\n")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{name}.mod", pdesc + f'\npath="mod/{name}"\n')
            for f in sorted(x for x in patch.rglob("*") if x.is_file()):
                z.write(f, f"{name}/" + f.relative_to(patch).as_posix())
        print(f"ok: {out.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
