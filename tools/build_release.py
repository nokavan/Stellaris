#!/usr/bin/env python3
"""Собирает архив мода для установки: releases/partisan_syndicate.zip

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


if __name__ == "__main__":
    main()
