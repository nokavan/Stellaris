#!/usr/bin/env python3
"""Готовый патч «кочевники строят мегаструктуры модов» без PowerShell.

Порт логики NomadPatch.ps1 из «Nomad Can Build Megastructures — Mod Compatible Edition».
В блоках possible мегаструктур:
  is_inside_border/is_within_borders_of = from|root -> always = yes (внутри NOR/NAND/NOT -> always = no)
  exists = starbase                                  -> то же
и в начало possible добавляется ванильная проверка
  inline_script = megastructures/system_ownership_or_waystation_check
(владение системой ИЛИ стоянка кочевника). Затем is_nomadic = no -> always = yes.
В технологиях: is_nomadic = no -> always = yes.

Файлы пишутся с теми же именами, что в исходном моде, поэтому патч ставится ПОСЛЕ этих модов.

Запуск:  python3 tools/gen_nomad_mega_patch.py <папка_мода> [<папка_мода> ...]
Результат: compat/nomad_mega_patch/common/{megastructures,technology}/
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "compat" / "nomad_mega_patch" / "common"
BORDER = re.compile(r"(is_inside_border|is_within_borders_of)\s*=\s*(from|root)")
STARBASE = re.compile(r"exists\s*=\s*starbase")
NEG = re.compile(r"\b(NOR|NAND|NOT)\s*=\s*\{")
CHECK = "system_ownership_or_waystation_check"


def process(text):
    if CHECK in text:
        return None
    lines = text.split("\n")
    out, neg = [], []
    depth = 0
    in_poss, poss_start, poss_depth, inject = False, -1, 0, False
    changed = False
    for i, line in enumerate(lines):
        clean = line.split("#", 1)[0]
        opens, closes = clean.count("{"), clean.count("}")
        if NEG.search(clean):
            neg.append(depth + opens)
        depth += opens
        if re.search(r"\bpossible\s*=\s*\{", clean):
            in_poss, poss_start, poss_depth, inject = True, i, depth, False
        if in_poss:
            in_neg = bool(neg) and depth >= neg[-1]
            rep = "always = no" if in_neg else "always = yes"
            if BORDER.search(clean):
                line = BORDER.sub(rep, line); inject = True
            if STARBASE.search(clean):
                line = STARBASE.sub(rep, line); inject = True
        out.append(line)
        depth -= closes
        while neg and depth < neg[-1]:
            neg.pop()
        if in_poss and depth < poss_depth:
            in_poss = False
            if inject:
                block = "\n".join(lines[poss_start:i + 1])
                if CHECK not in block:
                    out[poss_start] += f"\n\t\tinline_script = megastructures/{CHECK}"
                changed = True
    if not changed:
        return None
    res = "\n".join(out)
    return re.sub(r"is_nomadic\s*=\s*no", "always = yes", res)


def read(p):
    return p.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")


def main(mods):
    (OUT / "megastructures").mkdir(parents=True, exist_ok=True)
    (OUT / "technology").mkdir(parents=True, exist_ok=True)
    for d in ("megastructures", "technology"):
        for f in (OUT / d).glob("*.txt"):
            f.unlink()
    nm = nt = 0
    for mod in map(pathlib.Path, mods):
        for f in sorted((mod / "common" / "megastructures").glob("*.txt")):
            if f.name in ("00_ring_world.txt", "habitats.txt"):
                continue
            new = process(read(f))
            if new is not None:
                (OUT / "megastructures" / f.name).write_text(new, encoding="utf-8")
                nm += 1
        for f in sorted((mod / "common" / "technology").glob("*.txt")):
            t = read(f)
            if re.search(r"is_nomadic\s*=\s*no", t):
                (OUT / "technology" / f.name).write_text(re.sub(r"is_nomadic\s*=\s*no", "always = yes", t), encoding="utf-8")
                nt += 1
    print(f"ok: {nm} файлов мегаструктур, {nt} файлов технологий")


if __name__ == "__main__":
    main(sys.argv[1:])
