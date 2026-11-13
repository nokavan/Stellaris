#!/usr/bin/env python3
"""Перенос скриптов модов 3.x на Stellaris 4.x (механические замены).

  planet_event -> carrier_event
  create_pop = { species = X }  -> create_pop_group = { species = X }
  kill_pop = yes               -> kill_single_pop = yes
  every/random/any/count_owned_pop -> ..._owned_pop_group
  kill_leader = { fire = yes } -> kill_leader = { show_notification = yes }
  create_leader: убрать sub_type (в 4.x нет)
  num_pops > N -> any_owned_pop_group = { always = yes }
  resettle_pop = { pop planet } -> resettle_pop_group = { POP_GROUP PLANET PERCENTAGE = 25 }
  блоки if/while, «докручивающие» число попов одного вида (count_owned_pop < N) — удаляются
  (в 4.x население — группы, такая проверка теряет смысл)

Запуск: python3 tools/port_3x.py <файл> [<файл> ...]   (правит файлы на месте)
"""
import re, sys


def block_end(s, i):
    d = 0
    j = s.index("{", i)
    while True:
        if s[j] == "{":
            d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0:
                return j
        j += 1


def drop_pop_balancing(s):
    out, i = [], 0
    pat = re.compile(r"\n(\t*)(if|while) = \{")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        end = block_end(s, m.end() - 1)
        body = s[m.end():end]
        head = body.split("{", 2)
        if "count_owned_pop" in body[:400] and re.search(r"count_owned_pop\s*=\s*\{\s*count\s*<", body):
            out.append(s[i:m.start()])
            out.append(f"\n{m.group(1)}# (port 4.x) убрано выравнивание числа попов одного вида")
            i = end + 1
        else:
            out.append(s[i:m.end()])
            i = m.end()
    return "".join(out)


def port(s):
    s = drop_pop_balancing(s)
    s = re.sub(r"\bplanet_event\b", "carrier_event", s)
    s = re.sub(r"\bcreate_pop = \{", "create_pop_group = {", s)
    s = re.sub(r"\bkill_pop = yes", "kill_single_pop = yes", s)
    s = re.sub(r"\b(every|random|any|count)_owned_pop\b(?!_group)", r"\1_owned_pop_group", s)
    s = re.sub(r"kill_leader = \{\s*fire = yes\s*\}", "kill_leader = { show_notification = yes }", s)
    s = re.sub(r"\n\t*sub_type = [a-z_]+", "", s)
    # num_pops > N (N небольшое) -> есть хотя бы одна группа населения
    s = re.sub(r"\bnum_pops > [0-9]\b", "any_owned_pop_group = { always = yes }", s)
    # resettle_pop = { pop = THIS planet = X } -> resettle_pop_group (4.x), четверть группы за раз
    s = re.sub(r"resettle_pop = \{\s*pop = (\w+)\s*planet = ([^\s}]+)\s*\}",
               r"resettle_pop_group = {\n\t\t\t\t\t\t\t\tPOP_GROUP = this\n\t\t\t\t\t\t\t\tPLANET = \2\n\t\t\t\t\t\t\t\tPERCENTAGE = 25\n\t\t\t\t\t\t\t}", s)
    return s


if __name__ == "__main__":
    for p in sys.argv[1:]:
        raw = open(p, "rb").read()
        bom = raw.startswith(b"\xef\xbb\xbf")
        s = raw.decode("utf-8-sig").replace("\r\n", "\n")
        t = port(s)
        open(p, "w", encoding="utf-8-sig" if bom else "utf-8").write(t)
        print(p, "changed" if t != s else "same")
