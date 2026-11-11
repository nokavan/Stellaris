# Генератор зданий «Наследие Предтеч».
# Цифры, работы и иконки — из оригинальных зданий мода «Halo: Forerunner Ships & Portraits»
# (Workshop 2268843111, common/buildings/00_forerunner_buildings.txt; авторы разрешили использование).
# Тир 2 = значения оригинала, тир 1 = половина. Тир 1 улучшается до тира 2.
# Империи с цивиками «Партизанская сеть» или «Теневой сюзерен» строят тир 2 сразу.
import os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HALO_ICONS = os.environ.get("HALO_ICONS", "")   # папка gfx/interface/icons/buildings оригинала

# key, category, sets, оригинальная иконка, produces(t2), upkeep(t2), planet_modifier(t2), ru, en, ru_desc, en_desc
B = [
 ("vacuum_generator","resource",["generator"],"building_forerunner_vacuum_generator",
  {"energy":250},{"rare_crystals":2},{},
  "Вакуумный генератор Предтеч","Precursor Vacuum Generator",
  "Черпает энергию из ложного вакуума — почти бездонный источник.","Draws power from the false vacuum, a near-bottomless source."),
 ("synthesizer","resource",["farming"],"building_forerunner_nourishment_center",
  {"food":100},{"energy":20},{},
  "Синтезатор Предтеч","Precursor Synthesizer",
  "Репликаторы пищи, пережившие своих создателей.","Food replicators that outlived their makers."),
 ("supply_elevator","manufacturing",["mining"],"building_forerunner_dimensional_fabricator",
  {"minerals":100,"rare_crystals":10,"exotic_gases":10,"volatile_motes":10},{"energy":20},{},
  "Подпространственный лифт снабжения","Slipspace Supply Elevator",
  "Перебрасывает сырьё с дальних приисков через подпространство.","Translocates raw materials from distant claims through slipspace."),
 ("assembler_vats","manufacturing",["industrial","foundry"],"building_forerunner_nano_forge",
  {"alloys":30,"nanites":10},{"minerals":30,"energy":10},{"planet_structures_cost_mult":-0.15,"planet_building_build_speed_mult":0.15},
  "Сборочные чаны Предтеч","Precursor Assembler Vats",
  "Колоссальные чаны нанофабрикации превращают сырьё в сплавы и наниты.","Colossal nanofabrication vats that turn raw matter into alloys and nanites."),
 ("mercatus_vats","manufacturing",["industrial","factory"],"building_forerunner_affluence_center",
  {"consumer_goods":50},{"minerals":25,"energy":10},{},
  "Гражданские чаны Предтеч","Precursor Civilian Vats",
  "Любая материальная потребность может быть удовлетворена здесь.","Any material desire can be met here."),
 ("domain_archive","research",["research"],"building_forerunner_master_archive",
  {"physics_research":100,"society_research":100,"engineering_research":100},{"energy":25},
  {"planet_physicists_physics_research_produces_add":2,"planet_biologists_society_research_produces_add":2,"planet_engineers_engineering_research_produces_add":2,
   "job_physicist_add":200,"job_biologist_add":200,"job_engineer_add":200},
  "Архив Домена","Domain Archive",
  "Хранилище знаний исчезнувшей цивилизации, взломанное нашими агентами.","A vault of a vanished civilization's knowledge, cracked by our agents."),
 ("domicile","amenity",["urban"],"building_forerunner_domicile",
  {},{"energy":10},{"planet_housing_add":2000,"planet_amenities_add":2000},
  "Жилые комплексы из жёсткого света","Hard-Light Domicile",
  "Города из жёсткого света, где удобно прятать подполье.","Cities of hard light — a fine place to hide an underground."),
 ("lifeworker_preserve","amenity",["urban"],"building_forerunner_zeno_zoo",
  {},{"energy":10},{"planet_amenities_add":1500,"planet_housing_add":3000,"job_xeno_zoo_keeper_add":200},
  "Заповедник Жизнетворцев","Lifeworker Preserve",
  "Исследовательский заповедник для изучения инопланетной жизни.","A research preserve for studying alien life."),
 ("line_installation","army",["fortress"],"building_forerunner_stronghold",
  {},{"energy":5},{"planet_orbital_bombardment_damage":-0.5,"job_soldier_add":500},
  "Линейная установка","Line Installation",
  "Оборонный комплекс с арсеналами оружия Предтеч.","A defensive complex with arsenals of precursor weaponry."),
 ("sentinel_foundry","pop_assembly",["government","urban"],"building_sentinel_factory",
  {},{"energy":5},{"planet_pop_assembly_mult":0.15,"army_defense_health_mult":0.15,"planet_buildings_upkeep_mult":-0.15,"job_roboticist_add":200},
  "Кузня Стражей","Sentinel Foundry",
  "Плавучие фабрики выпускают роботов-Стражей для обороны и производства.","Floating factories that turn out Sentinel drones for defence and industry."),
]

def fmt(v):
    v = round(v, 4)
    return str(int(v)) if v == int(v) else ("%g" % v)

def block(d, ind, m):
    return "".join(f"{ind}{k} = {fmt(v*m)}\n" for k, v in d.items())

def building(key, cat, sets, prod, upk, pmod, tier):
    m = 0.5 if tier == 1 else 1.0
    name = f"building_ps_pre_{key}_{tier}"
    s = f"{name} = {{\n\tbase_buildtime = {'@b2_time' if tier==1 else '@b3_time'}\n\tbase_cap_amount = 1\n\tcategory = {cat}\n\n"
    s += "\tbuilding_sets = {\n" + "".join(f"\t\t{x}\n" for x in sets) + "\t}\n\n"
    s += "\tpotential = {\n\t\texists = owner\n\t\towner = { ps_is_partisan_empire = yes }\n\t}\n\n"
    if tier == 2:
        s += ("\t# Строится сразу только с нашими цивиками; остальные — улучшением тира 1\n"
              "\tallow = {\n\t\tcustom_tooltip = {\n\t\t\tfail_text = ps_pre_requires_civic_or_t1\n\t\t\tOR = {\n"
              "\t\t\t\towner = { OR = { has_valid_civic = civic_ps_partisan_network has_valid_civic = civic_ps_shadow_overlord } }\n"
              f"\t\t\t\thas_building = building_ps_pre_{key}_1\n\t\t\t}}\n\t\t}}\n\t}}\n\n")
    else:
        s += f"\tupgrades = {{\n\t\tbuilding_ps_pre_{key}_2\n\t}}\n\n"
    s += "\tdestroy_trigger = {\n\t\texists = owner\n\t\towner = { NOT = { ps_is_partisan_empire = yes } }\n\t}\n\n"
    if pmod:
        s += "\tplanet_modifier = {\n" + block(pmod, "\t\t", m) + "\t}\n\n"
    s += "\tresources = {\n\t\tcategory = planet_buildings\n\t\tcost = {\n"
    s += ("\t\t\tminerals = @b2_minerals\n" if tier == 1 else "\t\t\tminerals = @b3_minerals\n")
    s += "\t\t}\n"
    if upk:
        s += "\t\tupkeep = {\n" + block(upk, "\t\t\t", m) + "\t\t}\n"
    if prod:
        s += "\t\tproduces = {\n" + block(prod, "\t\t\t", m) + "\t\t}\n"
    s += "\t}\n}\n\n"
    return s

out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_precursor_buildings.py\n"
       "# «Наследие Предтеч»: 10 зданий, тир 1 → тир 2 (значения — из оригинального мода о Предтечах).\n"
       "# Цивики «Партизанская сеть» / «Теневой сюзерен» строят тир 2 сразу.\n\n"]
ru = ["﻿l_russian:\n"]; en = ["﻿l_english:\n"]
gfx = ["spriteTypes = {"]
for key, cat, sets, icon, prod, upk, pmod, rn, enn, rd, ed in B:
    for t in (1, 2):
        k = f"building_ps_pre_{key}_{t}"
        out.append(building(key, cat, sets, prod, upk, pmod, t))
        rs = "" if t == 1 else " II"
        ru.append(f' {k}:0 "{rn}{rs}"\n')
        ru.append(f' {k}_desc:0 "{rd}\\n\\n§YНаследие Предтеч — для партизанских империй.§!{"" if t==1 else " С цивиками «Партизанская сеть» и «Теневой сюзерен» строится сразу."}"\n')
        en.append(f' {k}:0 "{enn}{rs}"\n')
        en.append(f' {k}_desc:0 "{ed}\\n\\n§YPrecursor Legacy — for partisan empires.§!{"" if t==1 else " Empires with Partisan Network or Shadow Overlord can build it directly."}"\n')
        dst = os.path.join(ROOT, "gfx/interface/icons/buildings", k + ".dds")
        if HALO_ICONS:
            shutil.copyfile(os.path.join(HALO_ICONS, icon + ".dds"), dst)
        gfx.append(f'\tspriteType = {{\n\t\tname = "GFX_{k}"\n\t\ttexturefile = "gfx/interface/icons/buildings/{k}.dds"\n\t}}')
ru.append(' ps_pre_requires_civic_or_t1:0 "Нужен цивик «Партизанская сеть» или «Теневой сюзерен», иначе — улучшение здания тира 1."\n')
en.append(' ps_pre_requires_civic_or_t1:0 "Requires the Partisan Network or Shadow Overlord civic; otherwise upgrade the tier 1 building."\n')
gfx.append("}\n")
open(os.path.join(ROOT, "common/buildings/ps_precursor_buildings.txt"), "w", encoding="utf-8").write("".join(out))
open(os.path.join(ROOT, "localisation/russian/ps_precursor_l_russian.yml"), "w", encoding="utf-8").write("".join(ru))
open(os.path.join(ROOT, "localisation/english/ps_precursor_l_english.yml"), "w", encoding="utf-8").write("".join(en))
open(os.path.join(ROOT, "interface/ps_precursor_buildings.gfx"), "w", encoding="utf-8").write("\n".join(gfx))
print("ok", len(B) * 2, "buildings", "(icons copied)" if HALO_ICONS else "(icons kept)")
