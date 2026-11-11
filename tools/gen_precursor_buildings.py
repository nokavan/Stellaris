# Генератор зданий «Наследие Предтеч» (идеи — из мода о Предтечах, с разрешения авторов;
# в присланной копии файл зданий был пуст, поэтому здания написаны заново).
# Тир 1 улучшается до тира 2. Империи с цивиками «Партизанская сеть» или
# «Теневой сюзерен» могут строить тир 2 сразу, минуя тир 1.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# key, category, set, produces t1 (dict), mult t2, extra planet mod, extra country mod, ru name, en name, ru desc, en desc
B = [
 ("vacuum_generator","resource","generator",{"energy":12},None,None,
  "Вакуумный генератор Предтеч","Precursor Vacuum Generator",
  "Черпает энергию из ложного вакуума — почти бездонный источник.","Draws power from the false vacuum, a near-bottomless source."),
 ("synthesizer","resource","farming",{"food":12},None,None,
  "Синтезатор Предтеч","Precursor Synthesizer",
  "Репликаторы пищи, переживших своих создателей.","Food replicators that outlived their makers."),
 ("supply_elevator","resource","mining",{"minerals":12},None,None,
  "Подпространственный лифт снабжения","Slipspace Supply Elevator",
  "Перебрасывает сырьё с дальних приисков через подпространство.","Translocates raw materials from distant claims through slipspace."),
 ("assembler_vats","manufacturing","foundry",{"alloys":5},None,None,
  "Сборочные чаны Предтеч","Precursor Assembler Vats",
  "Колоссальные чаны нанофабрикации превращают сырьё в сплавы.","Colossal nanofabrication vats that turn raw matter into alloys."),
 ("mercatus_vats","manufacturing","factory",{"consumer_goods":6},None,None,
  "Гражданские чаны Предтеч","Precursor Civilian Vats",
  "Любая материальная потребность может быть удовлетворена здесь.","Any material desire can be met here."),
 ("domain_archive","research","research",{"physics_research":4,"society_research":4,"engineering_research":4},None,None,
  "Архив Домена","Domain Archive",
  "Хранилище знаний исчезнувшей цивилизации, взломанное нашими агентами.","A vault of a vanished civilization's knowledge, cracked by our agents."),
 ("domicile","government","urban",{"unity":5},{"planet_stability_add":3},None,
  "Жилые комплексы из жёсткого света","Hard-Light Domicile",
  "Города из жёсткого света, где удобно прятать подполье.","Cities of hard light — a fine place to hide an underground."),
 ("lifeworker_preserve","research","society",{"society_research":6,"unity":2},None,None,
  "Заповедник Жизнетворцев","Lifeworker Preserve",
  "Исследовательский заповедник для изучения инопланетной жизни.","A research preserve for studying alien life."),
 ("line_installation","army","fortress",{},{"planet_stability_add":5},{"army_damage_mult":0.05},
  "Линейная установка","Line Installation",
  "Оборонный комплекс с арсеналами оружия Предтеч.","A defensive complex with arsenals of precursor weaponry."),
 ("sentinel_foundry","manufacturing","foundry",{"alloys":3},None,{"country_naval_cap_add":8},
  "Кузня Стражей","Sentinel Foundry",
  "Плавучие фабрики выпускают роботов-Стражей для обороны и флота.","Floating factories that turn out Sentinel drones for defence and the fleet."),
]

CIVIC_DIRECT = """OR = {
				has_valid_civic = civic_ps_partisan_network
				has_valid_civic = civic_ps_shadow_overlord
			}"""

def block(d, ind):
    return "".join(f"{ind}{k} = {v}\n" for k,v in d.items())

def fmt(v):
    return ("%g" % v)

def building(key, cat, bset, prod, pmod, cmod, tier):
    m = 1 if tier == 1 else 2
    name = f"building_ps_pre_{key}_{tier}"
    s = f"{name} = {{\n\tbase_buildtime = {'@b1_time' if tier==1 else '@b2_time'}\n\tcategory = {cat}\n\n"
    s += f"\tbuilding_sets = {{\n\t\t{bset}\n\t}}\n\n"
    s += "\tpotential = {\n\t\texists = owner\n\t\towner = { ps_is_partisan_empire = yes }\n\t}\n\n"
    if tier == 2:
        s += ("\t# Строится сразу только с нашими цивиками; остальные — улучшением тира 1\n"
              "\tallow = {\n\t\tcustom_tooltip = {\n\t\t\tfail_text = ps_pre_requires_civic_or_t1\n\t\t\tOR = {\n"
              f"\t\t\t\towner = {{ {CIVIC_DIRECT.replace(chr(10)+chr(9)*3, ' ').replace(chr(9),'')} }}\n"
              f"\t\t\t\thas_building = building_ps_pre_{key}_1\n\t\t\t}}\n\t\t}}\n\t}}\n\n")
    else:
        s += f"\tupgrades = {{\n\t\tbuilding_ps_pre_{key}_2\n\t}}\n\n"
    s += "\tdestroy_trigger = {\n\t\texists = owner\n\t\towner = { NOT = { ps_is_partisan_empire = yes } }\n\t}\n\n"
    if pmod:
        s += "\tplanet_modifier = {\n" + block({k: fmt(v*m) for k,v in pmod.items()}, "\t\t") + "\t}\n\n"
    if cmod:
        s += "\tcountry_modifier = {\n" + block({k: fmt(v*m) for k,v in cmod.items()}, "\t\t") + "\t}\n\n"
    s += "\tresources = {\n\t\tcategory = planet_buildings\n\t\tcost = {\n"
    s += ("\t\t\tminerals = 400\n" if tier == 1 else "\t\t\tminerals = 600\n\t\t\talloys = 100\n")
    s += "\t\t}\n\t\tupkeep = {\n" + f"\t\t\tenergy = {2*m}\n" + "\t\t}\n"
    if prod:
        s += "\t\tproduces = {\n" + block({k: fmt(v*m) for k,v in prod.items()}, "\t\t\t") + "\t\t}\n"
    s += "\t}\n}\n\n"
    return s

out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_precursor_buildings.py\n"
       "# Синдикат Сопротивления — «Наследие Предтеч»: 10 зданий, тир 1 → тир 2.\n"
       "# Цивики «Партизанская сеть» / «Теневой сюзерен» строят тир 2 сразу.\n\n"]
ru = ["﻿l_russian:\n"]; en = ["﻿l_english:\n"]
for key,cat,bset,prod,pmod,cmod,rn,enn,rd,ed in B:
    for t in (1,2):
        out.append(building(key,cat,bset,prod,pmod,cmod,t))
        rs = "" if t==1 else " II"
        ru.append(f' building_ps_pre_{key}_{t}:0 "{rn}{rs}"\n')
        ru.append(f' building_ps_pre_{key}_{t}_desc:0 "{rd}\\n\\n§YНаследие Предтеч — для партизанских империй.§!{"" if t==1 else " С цивиками «Партизанская сеть» и «Теневой сюзерен» строится сразу."}"\n')
        en.append(f' building_ps_pre_{key}_{t}:0 "{enn}{rs}"\n')
        en.append(f' building_ps_pre_{key}_{t}_desc:0 "{ed}\\n\\n§YPrecursor Legacy — for partisan empires.§!{"" if t==1 else " Empires with Partisan Network or Shadow Overlord can build it directly."}"\n')
ru.append(' ps_pre_requires_civic_or_t1:0 "Нужен цивик «Партизанская сеть» или «Теневой сюзерен», иначе — улучшение здания тира 1."\n')
en.append(' ps_pre_requires_civic_or_t1:0 "Requires the Partisan Network or Shadow Overlord civic; otherwise upgrade the tier 1 building."\n')
open(os.path.join(ROOT,"common/buildings/ps_precursor_buildings.txt"),"w",encoding="utf-8").write("".join(out))
open(os.path.join(ROOT,"localisation/russian/ps_precursor_l_russian.yml"),"w",encoding="utf-8").write("".join(ru))
open(os.path.join(ROOT,"localisation/english/ps_precursor_l_english.yml"),"w",encoding="utf-8").write("".join(en))
print("ok", len(B)*2, "buildings")

# Иконки и спрайты (простая геометрия: бирюзовый «глиф Предтеч» + точки тира)
from PIL import Image, ImageDraw
import math
gfx = ["spriteTypes = {"]
COL = {"resource":(70,200,190),"manufacturing":(220,170,60),"research":(90,140,230),
       "government":(190,110,220),"army":(210,70,60)}
for i,(key,cat,*_rest) in enumerate(B):
    for t in (1,2):
        k = f"building_ps_pre_{key}_{t}"
        img = Image.new("RGBA",(64,64),(25,30,40,255)); d = ImageDraw.Draw(img)
        c = COL.get(cat,(150,150,150))
        pts=[(32+24*math.cos(math.radians(60*j+30)),32+24*math.sin(math.radians(60*j+30))) for j in range(6)]
        d.polygon(pts, outline=c+(255,), fill=(c[0]//4,c[1]//4,c[2]//4,255))
        r = 6 + (i % 5) * 2
        d.ellipse([32-r,32-r,32+r,32+r], fill=c+(255,))
        d.line([(32,10),(32,54)], fill=(230,240,240,255), width=2)
        for p in range(t):
            d.rectangle([6+p*9,52,12+p*9,58], fill=(240,220,120,255))
        p = os.path.join(ROOT,"gfx/interface/icons/buildings",k+".dds")
        img.save(p, format="DDS")
        gfx.append(f'\tspriteType = {{\n\t\tname = "GFX_{k}"\n\t\ttexturefile = "gfx/interface/icons/buildings/{k}.dds"\n\t}}')
gfx.append("}\n")
open(os.path.join(ROOT,"interface/ps_precursor_buildings.gfx"),"w",encoding="utf-8").write("\n".join(gfx))
print("icons ok")
