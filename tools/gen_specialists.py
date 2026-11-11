#!/usr/bin/env python3
"""Генератор специализированных вассалов Синдиката Сопротивления.

Все типы описаны в таблице TYPES ниже. Скрипт создаёт:
  common/specialist_subject_types/ps_specialist_subject_types.txt
  common/specialist_subject_perks/ps_specialist_subject_perks.txt
  common/agreement_term_values/ps_agreement_term_values.txt
  common/agreement_presets/ps_specialist_presets.txt
  common/message_types/ps_message_types.txt  (уведомления о новом уровне)
  interface/ps_specialists.gfx  + DDS-иконки (заглушки)
  localisation/{russian,english}/ps_specialists_l_*.yml

Формат сверен с vanilla 4.x:
  specialist_subject_types/00_specialist_subject_types.txt
  specialist_subject_perks/00_specialist_subject_perks.txt
  agreement_term_values/00_agreement_term_values.txt
  agreement_presets/00_agreement_presets.txt

Запуск из корня репозитория:  python3 tools/gen_specialists.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

def research(v):
    return {
        "country_physics_research_produces_mult": v,
        "country_society_research_produces_mult": v,
        "country_engineering_research_produces_mult": v,
    }


# ---------------------------------------------------------------------------
# ДАННЫЕ
# perk: (ключ_суффикс, {subject_modifier}, {overlord_modifier}, flag_or_None,
#        ru_name, ru_desc, en_name, en_desc)
# ---------------------------------------------------------------------------
TYPES = [
    {
        "key": "ps_strike",
        "ethic": "ethic_militarist", "anti": "ethic_pacifist",
        "ethic_ru": "Милитаристы", "anti_ru": "Пацифисты",
        "ethic_en": "Militarist", "anti_en": "Pacifist",
        "subsidy": -0.2,
        "color": (190, 40, 40),
        "ru": ("Ударный легион", "Атакующий вассал. Вся экономика подчинена флоту: верфи работают круглосуточно, а лучшие экипажи служат в ударных эскадрах Синдиката."),
        "en": ("Strike Legion", "An offensive subject. The whole economy serves the fleet: shipyards run around the clock and the best crews serve in the Syndicate's strike squadrons."),
        "levels": [
            {"main": {"ship_fire_rate_mult": 0.10, "ship_weapon_damage": 0.05, "country_naval_cap_mult": 0.15},
             "pen": {**research(-0.20), "country_unity_produces_mult": -0.10},
             "perks": [
                 ("overlord_modifier", {}, {"ship_fire_rate_mult": 0.03}, None,
                  "Ударная доктрина", "Сюзерен перенимает тактику легиона.",
                  "Strike Doctrine", "The overlord adopts the legion's tactics."),
                 ("drills", {"ship_speed_mult": 0.10}, {}, None,
                  "Учения на марше", "Флот легиона учится бить и уходить до прихода подкреплений.",
                  "Drills on the Move", "The legion's fleet learns to strike and withdraw before reinforcements arrive."),
             ]},
            {"main": {"ship_fire_rate_mult": 0.15, "ship_weapon_damage": 0.10, "country_naval_cap_mult": 0.25},
             "pen": {**research(-0.30), "country_unity_produces_mult": -0.15},
             "perks": [
                 ("admirals", {"country_commander_cap_add": 1, "commander_initial_skill": 1}, {}, None,
                  "Адмиралы Сопротивления", "Легион растит собственных флотоводцев.",
                  "Admirals of the Resistance", "The legion raises its own fleet commanders."),
                 ("overlord_fleet", {}, {"country_naval_cap_add": 15}, None,
                  "Флот под рукой", "Эскадры легиона входят в резерв сюзерена.",
                  "Fleet on Call", "The legion's squadrons join the overlord's reserve."),
             ]},
            {"main": {"ship_fire_rate_mult": 0.20, "ship_weapon_damage": 0.15, "country_naval_cap_mult": 0.35},
             "pen": {**research(-0.40), "country_unity_produces_mult": -0.20},
             "perks": [
                 ("iron_fist", {}, {"ship_weapon_damage": 0.05}, None,
                  "Кулак Синдиката", "Залпы легиона и сюзерена бьют как один.",
                  "Fist of the Syndicate", "The legion's and the overlord's volleys strike as one."),
             ]},
        ],
    },
    {
        "key": "ps_assault",
        "ethic": "ethic_authoritarian", "anti": "ethic_egalitarian",
        "ethic_ru": "Авторитаристы", "anti_ru": "Эгалитаристы",
        "ethic_en": "Authoritarian", "anti_en": "Egalitarian",
        "subsidy": -0.2,
        "color": (150, 90, 40),
        "ru": ("Штурмовой корпус", "Атакующий вассал. Мир-казарма, поставляющий Синдикату штурмовые армии для высадок и партизанских рейдов в тылу врага."),
        "en": ("Assault Corps", "An offensive subject. A barracks world supplying the Syndicate with assault armies for landings and partisan raids behind enemy lines."),
        "levels": [
            {"main": {"army_damage_mult": 0.25, "army_health": 0.15, "army_morale": 0.15, "planet_army_build_speed_mult": 0.25},
             "pen": {"country_naval_cap_mult": -0.25, "country_energy_produces_mult": -0.10},
             "perks": [
                 ("overlord_modifier", {}, {"army_damage_mult": 0.05}, None,
                  "Штурмовые инструкторы", "Инструкторы корпуса тренируют армии сюзерена.",
                  "Assault Instructors", "Corps instructors train the overlord's armies."),
                 ("veterans", {"army_starting_experience_add": 100}, {}, None,
                  "Ветераны лесов", "Новобранцы проходят школу партизанской войны.",
                  "Forest Veterans", "Recruits go through the school of partisan warfare."),
             ]},
            {"main": {"army_damage_mult": 0.40, "army_health": 0.25, "army_morale": 0.25, "planet_army_build_speed_mult": 0.50},
             "pen": {"country_naval_cap_mult": -0.35, "country_energy_produces_mult": -0.15},
             "perks": [
                 ("generals", {"country_commander_cap_add": 1, "commander_initial_skill": 1}, {}, None,
                  "Генералы подполья", "Корпус растит собственных командиров.",
                  "Underground Generals", "The corps raises its own commanders."),
                 ("overlord_veterans", {}, {"army_starting_experience_add": 50}, None,
                  "Обмен опытом", "Армии сюзерена начинают службу обстрелянными.",
                  "Shared Experience", "The overlord's armies start their service battle-tested."),
             ]},
            {"main": {"army_damage_mult": 0.60, "army_health": 0.35, "army_morale": 0.35, "planet_army_build_speed_mult": 0.75},
             "pen": {"country_naval_cap_mult": -0.50, "country_energy_produces_mult": -0.20},
             "perks": [
                 ("storm", {}, {"army_damage_mult": 0.10, "army_health": 0.10}, None,
                  "Штурм без остановки", "Высадки сюзерена идут волнами, одна за другой.",
                  "Relentless Storm", "The overlord's landings come in wave after wave."),
             ]},
        ],
    },
    {
        "key": "ps_raiders",
        "ethic": "ethic_xenophobe", "anti": "ethic_xenophile",
        "ethic_ru": "Ксенофобы", "anti_ru": "Ксенофилы",
        "ethic_en": "Xenophobe", "anti_en": "Xenophile",
        "subsidy": 0.0,
        "color": (40, 110, 150),
        "ru": ("Каперская флотилия", "Атакующий вассал. Каперы с грамотами Синдиката: в мирное время контрабанда, в войну — рейды по вражеским торговым путям."),
        "en": ("Privateer Flotilla", "An offensive subject. Privateers holding Syndicate letters of marque: smuggling in peacetime, raids on enemy trade routes in war."),
        "levels": [
            {"main": {"ship_evasion_add": 10, "ship_speed_mult": 0.15, "country_energy_produces_mult": 0.10},
             "pen": {"country_unity_produces_mult": -0.15, "pop_happiness": -0.05},
             "perks": [
                 ("overlord_modifier", {}, {"ship_speed_mult": 0.05}, None,
                  "Тайные маршруты", "Каперы делятся с сюзереном своими тропами.",
                  "Hidden Lanes", "The privateers share their routes with the overlord."),
                 ("letters_of_marque", {}, {}, "ps_raiders_1",
                  "Каперские грамоты", "Когда сюзерен воюет, флотилия грабит его врагов: §G+100§! энергии сюзерену в год, а враги получают модификатор «Каперские рейды».",
                  "Letters of Marque", "While the overlord is at war, the flotilla raids its enemies: §G+100§! energy per year to the overlord, and enemies suffer «Privateer Raids»."),
             ]},
            {"main": {"ship_evasion_add": 15, "ship_speed_mult": 0.20, "country_energy_produces_mult": 0.15},
             "pen": {"country_unity_produces_mult": -0.20, "pop_happiness": -0.05},
             "perks": [
                 ("prize_crews", {}, {}, "ps_raiders_2",
                  "Призовые команды", "Добыча с войны растёт до §G+200§! энергии в год.",
                  "Prize Crews", "War loot grows to §G+200§! energy per year."),
             ]},
            {"main": {"ship_evasion_add": 20, "ship_speed_mult": 0.25, "country_energy_produces_mult": 0.20},
             "pen": {"country_unity_produces_mult": -0.25, "pop_happiness": -0.10},
             "perks": [
                 ("wolfpacks", {}, {"ship_evasion_add": 3}, "ps_raiders_3",
                  "Волчьи стаи", "Добыча — §G+300§! энергии в год. Корабли сюзерена учатся уклоняться, как каперы.",
                  "Wolfpacks", "Loot rises to §G+300§! energy per year. The overlord's ships learn to evade like privateers."),
             ]},
        ],
    },
    {
        "key": "ps_residency",
        "ethic": "ethic_xenophile", "anti": "ethic_xenophobe",
        "ethic_ru": "Ксенофилы", "anti_ru": "Ксенофобы",
        "ethic_en": "Xenophile", "anti_en": "Xenophobe",
        "subsidy": -0.1,
        "color": (90, 70, 160),
        "ru": ("Шпионская резидентура", "Вассал-разведка. Его посольства, торговцы и туристы — глаза и уши Синдиката по всей галактике."),
        "en": ("Spy Residency", "An intelligence subject. Its embassies, merchants and tourists are the Syndicate's eyes and ears across the galaxy."),
        "levels": [
            {"main": {"intel_encryption_add": 2, "intel_decryption_add": 1, "spy_network_daily_value_mult": 0.20},
             "pen": {"country_naval_cap_mult": -0.25, "army_damage_mult": -0.20},
             "perks": [
                 ("overlord_modifier", {}, {"intel_decryption_add": 1}, None,
                  "Общий шифр", "Сюзерен получает доступ к шифрам резидентуры.",
                  "Shared Cipher", "The overlord gains access to the residency's ciphers."),
                 ("network", {}, {"spy_network_daily_value_mult": 0.10}, "ps_residency_active",
                  "Агентура на местах", "Шпионские сети сюзерена растут быстрее, а агентурные операции Синдиката чаще успешны.",
                  "Agents on the Ground", "The overlord's spy networks grow faster and Syndicate agent operations succeed more often."),
             ]},
            {"main": {"intel_encryption_add": 3, "intel_decryption_add": 2, "spy_network_daily_value_mult": 0.35},
             "pen": {"country_naval_cap_mult": -0.35, "army_damage_mult": -0.30},
             "perks": [
                 ("envoys", {}, {"envoys_add": 1}, None,
                  "Нелегалы", "Резидентура выделяет сюзерену агента-посланника.",
                  "Illegals", "The residency lends the overlord an agent envoy."),
             ]},
            {"main": {"intel_encryption_add": 4, "intel_decryption_add": 3, "spy_network_daily_value_mult": 0.50},
             "pen": {"country_naval_cap_mult": -0.45, "army_damage_mult": -0.40},
             "perks": [
                 ("ghosts", {}, {"intel_encryption_add": 2, "spy_network_daily_value_mult": 0.15}, None,
                  "Призраки", "Агентов резидентуры невозможно отличить от обычных граждан.",
                  "Ghosts", "The residency's agents are indistinguishable from ordinary citizens."),
             ]},
        ],
    },
    {
        "key": "ps_exchange",
        "ethic": "ethic_egalitarian", "anti": "ethic_authoritarian",
        "ethic_ru": "Эгалитаристы", "anti_ru": "Авторитаристы",
        "ethic_en": "Egalitarian", "anti_en": "Authoritarian",
        "subsidy": 0.3,
        "color": (200, 160, 60),
        "ru": ("Теневая биржа", "Экономический вассал. Через его биржи отмываются доходы Синдиката, а дивиденды уходят сюзерену."),
        "en": ("Shadow Exchange", "An economic subject. The Syndicate's income is laundered through its exchanges, and dividends flow to the overlord."),
        "levels": [
            {"main": {"country_energy_produces_mult": 0.25},
             "pen": {"planet_crime_add": 10, "country_naval_cap_mult": -0.20},
             "perks": [
                 ("overlord_modifier", {}, {"country_base_energy_produces_add": 10}, None,
                  "Дивиденды", "Биржа ежемесячно перечисляет сюзерену долю.",
                  "Dividends", "The exchange transfers a share to the overlord every month."),
                 ("ledgers", {}, {}, "ps_exchange_active",
                  "Двойная бухгалтерия", "Операция «Обчистить казну» у сюзерена чаще успешна.",
                  "Double Bookkeeping", "The overlord's «Empty their treasury» operation succeeds more often."),
             ]},
            {"main": {"country_energy_produces_mult": 0.35},
             "pen": {"planet_crime_add": 15, "country_naval_cap_mult": -0.30},
             "perks": [
                 ("dividends", {}, {"country_base_energy_produces_add": 15, "country_base_influence_produces_add": 0.5}, None,
                  "Чёрная касса", "Сюзерен получает больше энергии и немного влияния.",
                  "Black Fund", "The overlord receives more energy and a little influence."),
             ]},
            {"main": {"country_energy_produces_mult": 0.50},
             "pen": {"planet_crime_add": 20, "country_naval_cap_mult": -0.40},
             "perks": [
                 ("cartel", {}, {"country_energy_produces_mult": 0.05}, None,
                  "Картель", "Биржа управляет ценами по всей сети Синдиката.",
                  "Cartel", "The exchange controls prices across the Syndicate network."),
             ]},
        ],
    },
    {
        "key": "ps_trust",
        "ethic": "ethic_materialist", "anti": "ethic_spiritualist",
        "ethic_ru": "Материалисты", "anti_ru": "Спиритуалисты",
        "ethic_en": "Materialist", "anti_en": "Spiritualist",
        "subsidy": 0.45,
        "color": (90, 160, 80),
        "ru": ("Ресурсный трест", "Экономический вассал. Шахты, фермы, литейные и банки работают на Синдикат: трест добывает ресурсы, торгует ими и переводит деньги сюзерену."),
        "en": ("Resource Trust", "An economic subject. Mines, farms, foundries and banks work for the Syndicate: the trust extracts resources, trades them and sends money to the overlord."),
        "levels": [
            {"main": {"country_minerals_produces_mult": 0.20, "country_food_produces_mult": 0.20,
                      "country_energy_produces_mult": 0.15, "country_alloys_produces_mult": 0.10},
             "pen": {**research(-0.15), "country_naval_cap_mult": -0.25, "army_damage_mult": -0.15},
             "perks": [
                 ("overlord_modifier", {}, {"country_base_minerals_produces_add": 10, "country_base_energy_produces_add": 5}, None,
                  "Поставки треста", "Трест ежемесячно отгружает сюзерену минералы и энергию.",
                  "Trust Shipments", "The trust ships minerals and energy to the overlord every month."),
                 ("stockpiles", {"country_resource_max_add": 2000}, {"country_resource_max_add": 1000}, None,
                  "Склады треста", "Огромные хранилища для ресурсов треста и сюзерена.",
                  "Trust Warehouses", "Huge storage for the trust's and the overlord's resources."),
             ]},
            {"main": {"country_minerals_produces_mult": 0.30, "country_food_produces_mult": 0.30,
                      "country_energy_produces_mult": 0.25, "country_alloys_produces_mult": 0.15,
                      "country_rare_crystals_produces_mult": 0.15, "country_exotic_gases_produces_mult": 0.15,
                      "country_volatile_motes_produces_mult": 0.15},
             "pen": {**research(-0.25), "country_naval_cap_mult": -0.35, "army_damage_mult": -0.25},
             "perks": [
                 ("strategic", {}, {"country_base_rare_crystals_produces_add": 1, "country_base_exotic_gases_produces_add": 1,
                                    "country_base_volatile_motes_produces_add": 1}, None,
                  "Стратегический резерв", "Трест поставляет сюзерену редкие ресурсы.",
                  "Strategic Reserve", "The trust supplies the overlord with rare resources."),
                 ("bank", {}, {"country_base_energy_produces_add": 15, "country_base_alloys_produces_add": 3}, None,
                  "Банк треста", "Деньги и сплавы текут в казну сюзерена.",
                  "Trust Bank", "Money and alloys flow into the overlord's treasury."),
             ]},
            {"main": {"country_minerals_produces_mult": 0.40, "country_food_produces_mult": 0.40,
                      "country_energy_produces_mult": 0.35, "country_alloys_produces_mult": 0.25,
                      "country_rare_crystals_produces_mult": 0.25, "country_exotic_gases_produces_mult": 0.25,
                      "country_volatile_motes_produces_mult": 0.25},
             "pen": {**research(-0.35), "country_naval_cap_mult": -0.45, "army_damage_mult": -0.35},
             "perks": [
                 ("monopoly", {}, {"country_minerals_produces_mult": 0.05, "country_alloys_produces_mult": 0.05,
                                   "country_energy_produces_mult": 0.05}, None,
                  "Монополия", "Трест контролирует рынки всей империи сюзерена.",
                  "Monopoly", "The trust controls the markets of the overlord's whole empire."),
             ]},
        ],
    },
]

LEVEL_RU = ["I", "II", "III"]


# ---------------------------------------------------------------------------
def block(name, d, ind):
    if not d:
        return ""
    t = "\t" * ind
    lines = [f"{t}{name} = {{"]
    for k, v in d.items():
        lines.append(f"{t}\t{k} = {v:g}")
    lines.append(f"{t}}}")
    return "\n".join(lines) + "\n"


def perk_key(tkey, lvl, suffix):
    return f"{tkey}_{lvl}_{suffix}"


def gen_types():
    out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_specialists.py — правьте генератор, а не этот файл\n",
           "@ps_level_2_xp_cost = 1200\n@ps_level_3_xp_cost = 3600\n@ps_conversion_time = 30\n"]
    for T in TYPES:
        k = T["key"]
        out.append(f"""
specialist_{k} = {{
	icon = "GFX_diplomacy_specialist_subject_{k}"
	icon_large = "GFX_diplomacy_specialist_subject_{k}_large"
	preferred_ethic = {T['ethic']}
	base_conversion_time = @ps_conversion_time

	levels = {{""")
        for i, L in enumerate(T["levels"], 1):
            perks = [f"{k}_{i}_modifier", f"{k}_{i}_penalties"] + [perk_key(k, i, p[0]) for p in L["perks"]]
            xp = f"\n\t\t\texperience_needed_for_next_level = @ps_level_{i + 1}_xp_cost" if i < 3 else ""
            out.append(f"""
		# Level {i}
		{{{xp}
			perks = {{
{chr(10).join(chr(9) * 4 + p for p in perks)}
			}}
		}}""")
        out.append("\n\t}\n}\n")
    return "".join(out)


def gen_perks():
    out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_specialists.py — правьте генератор, а не этот файл\n"]
    for T in TYPES:
        k = T["key"]
        out.append(f"\n######## {T['en'][0]} ########\n")
        for i, L in enumerate(T["levels"], 1):
            out.append(f"\n{k}_{i}_modifier = {{\n\tmain_perk = yes\n{block('subject_modifier', L['main'], 1)}}}\n")
            out.append(f"\n{k}_{i}_penalties = {{\n\tmain_perk = yes\n{block('subject_modifier', L['pen'], 1)}}}\n")
            for (suf, sub, ov, flag, *_t) in L["perks"]:
                pk = perk_key(k, i, suf)
                body = f'\ticon = "GFX_specialist_perk_{pk}"\n'
                body += block("subject_modifier", sub, 1)
                body += block("overlord_modifier", ov, 1)
                if flag:
                    body += (f"\tactivate_effect = {{\n\t\ttarget = {{ set_country_flag = {flag} }}\n\t}}\n"
                             f"\tdeactivate_effect = {{\n\t\ttarget = {{ remove_country_flag = {flag} }}\n\t}}\n")
                body += f"\tdesc = {{\n\t\tdescription = {pk}_desc\n\t}}\n"
                out.append(f"\n{pk} = {{\n{body}}}\n")
    return "".join(out)


def gen_term_values():
    out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_specialists.py — правьте генератор, а не этот файл\n"
           "# owner = сюзерен, target = вассал\n"]
    for T in TYPES:
        k = T["key"]
        out.append(f"""
specialist_{k} = {{
	term = specialist_type
	triggered_loyalty_change = {{
		trigger = {{
			target = {{ has_ethic = {T['ethic']} }}
		}}
		loyalty_change = 5
		ai_acceptance = {{
			subject = 25
		}}
	}}
	triggered_loyalty_change = {{
		trigger = {{
			target = {{ has_ethic = {T['anti']} }}
		}}
		loyalty_change = -20
		ai_acceptance = {{
			subject = -100
		}}
	}}
	# Тайный переворот (операция Синдиката) делает совет цели сговорчивым
	triggered_loyalty_change = {{
		trigger = {{
			target = {{ has_country_flag = ps_puppet_council }}
		}}
		loyalty_change = 10
		ai_acceptance = {{
			subject = 150
		}}
	}}
	activate_effect = {{
		convert_to_specialist = specialist_{k}
	}}
	potential = {{
		agreement_preset = preset_{k}
	}}
}}
""")
    return "".join(out)


DISCRETE = [
    ("subject_integration", "subject_can_not_be_integrated"),
    ("subject_diplomacy", "subject_can_do_diplomacy_but_not_vote"),
    ("subject_expand", "subject_can_expand"),
    ("joins_overlord_wars", None),
    ("joins_subject_wars", "joins_subject_wars_defensive"),
    ("subject_holdings_limit", "subject_holdings_limit_1"),
    ("subject_loyalty", "subject_loyalty_effects"),
    ("protectorate", "subject_is_not_protectorate"),
]
OFFENSIVE = {"ps_strike", "ps_assault", "ps_raiders"}


def gen_presets():
    out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_specialists.py — правьте генератор, а не этот файл\n"
           "# potential: this = вассал, FROM = сюзерен (как в vanilla preset_bulwark)\n"]
    for T in TYPES:
        k = T["key"]
        terms = [("specialist_type", f"specialist_{k}")]
        for key, val in DISCRETE:
            if key == "joins_overlord_wars":
                val = "joins_overlord_wars_all" if k in OFFENSIVE else "joins_overlord_wars_defensive"
            terms.append((key, val))
        terms_txt = "".join(f"\t\t\t{{\n\t\t\t\tkey = {a}\n\t\t\t\tvalue = {b}\n\t\t\t}}\n" for a, b in terms)
        out.append(f"""
preset_{k} = {{
	specialist_type = specialist_{k}
	term_data = {{
		resource_terms = {{
			{{
				key = resource_subsidies_basic
				value = {T['subsidy']:g}
			}}
		}}
		discrete_terms = {{
{terms_txt}		}}
	}}

	overlord_weight = {{
		base = 50
		modifier = {{
			add = 50
			has_ethic = {T['ethic']}
		}}
	}}

	subject_weight = {{
		base = 25
		modifier = {{
			add = 50
			has_ethic = {T['ethic']}
		}}
		modifier = {{
			add = -50
			has_ethic = {T['anti']}
		}}
		modifier = {{
			add = 300
			has_country_flag = ps_puppet_council
		}}
	}}

	potential = {{
		has_overlord_dlc = yes
		FROM = {{ ps_is_shadow_overlord = yes }}
		NOR = {{
			is_nomadic = yes
			has_civic = civic_inwards_perfection
			FROM = {{ has_civic = civic_inwards_perfection }}
			FROM = {{ has_country_flag = heir_of_the_khan_khan }}
			has_origin = origin_nomadic_purger
		}}
		OR = {{
			any_agreement = {{ agreement_preset = preset_{k} }}
			has_country_flag = specialistion_subject_conversion_flag
			has_country_flag = ps_puppet_council
			tech_unlocked_ratio = {{
				who = from
				ratio >= 0.4
			}}
		}}
		FROM = {{ is_nomadic = no }}
		is_nomadic = no
	}}
}}
""")
    return "".join(out)


MSG_ICON = {"ps_strike": "bulwark", "ps_assault": "bulwark", "ps_raiders": "bulwark",
            "ps_residency": "scholarium", "ps_exchange": "prospectorium", "ps_trust": "prospectorium"}


def gen_message_types():
    """Сообщения о повышении уровня — как в vanilla common/message_types/00_message_types.txt."""
    out = ["# АВТОГЕНЕРАЦИЯ: tools/gen_specialists.py — правьте генератор, а не этот файл\n"]
    for T in TYPES:
        k = T["key"]
        for who in ("SUBJECT", "WE"):
            out.append(f"""
message_type = {{
	key = "{who}_LEVEL_UP_specialist_{k}"
	icon = "GFX_message_{MSG_ICON[k]}_level_up"
	icon_frame = 1

	sound = "discovery"
	ping = "mixed_notification_green"

	category = diplomacy
}}
""")
    return "".join(out)


def gen_gfx():
    lines = ["spriteTypes = {"]
    for T in TYPES:
        k = T["key"]
        for suf, size in (("", 40), ("_large", 80)):
            lines.append(f'\tspriteType = {{\n\t\tname = "GFX_diplomacy_specialist_subject_{k}{suf}"\n'
                         f'\t\ttexturefile = "gfx/interface/icons/specialists/{k}{suf}.dds"\n\t}}')
        for i, L in enumerate(T["levels"], 1):
            for p in L["perks"]:
                pk = perk_key(k, i, p[0])
                lines.append(f'\tspriteType = {{\n\t\tname = "GFX_specialist_perk_{pk}"\n'
                             f'\t\ttexturefile = "gfx/interface/icons/specialists/perks/{pk}.dds"\n\t}}')
    lines.append("}")
    return "\n".join(lines) + "\n"


def loc(lang):
    ru = lang == "russian"
    L = [f"l_{lang}:"]
    for T in TYPES:
        k = T["key"]
        name, desc = T["ru"] if ru else T["en"]
        eth, anti = (T["ethic_ru"], T["anti_ru"]) if ru else (T["ethic_en"], T["anti_en"])
        offensive = k in OFFENSIVE
        wars = ("Вступает во §Yвсе§! войны сюзерена." if ru else "Joins §Yall§! of the overlord's wars.") if offensive else \
               ("Вступает только в оборонительные войны." if ru else "Joins defensive wars only.")
        pref = (f"Предпочитают: §G{eth}§!. Против: §R{anti}§!." if ru else f"Preferred: §G{eth}§!. Opposed: §R{anti}§!.")
        full = f"{desc}\\n\\n{wars}\\n{pref}"
        L += [f' specialist_{k}:0 "{name}"',
              f' specialist_{k}_desc:0 "{full}"',
              f' preset_{k}:0 "{name}"',
              f' preset_{k}_desc:0 "{full}"',
              f' preset_{k}_flavor_desc:0 "${"preset_" + k}_desc$"',
              f' specialist_{k}_summary:0 "{name}: {desc}"',
              f' MESSAGE_SUBJECT_LEVEL_UP_specialist_{k}_TITLE:0 "{("Новый уровень: " if ru else "Specialist level up: ") + name}"',
              f' MESSAGE_WE_LEVEL_UP_specialist_{k}_TITLE:0 "$MESSAGE_WE_LEVEL_UP_TITLE$: {name}"']
        for i, Lv in enumerate(T["levels"], 1):
            lvl = LEVEL_RU[i - 1]
            L += [f' {k}_{i}_modifier:0 "{name} {lvl}"',
                  f' {k}_{i}_penalties:0 "{"Издержки специализации" if ru else "Specialization Costs"} {lvl}"']
            for (suf, sub, ov, flag, rn, rd, en, ed) in Lv["perks"]:
                pk = perk_key(k, i, suf)
                L += [f' {pk}:0 "{rn if ru else en}"', f' {pk}_desc:0 "{rd if ru else ed}"']
    return "\n".join(L) + "\n"


def main():
    w = lambda rel, txt: ((ROOT / rel).parent.mkdir(parents=True, exist_ok=True), (ROOT / rel).write_text(txt, encoding="utf-8"))
    w("common/specialist_subject_types/ps_specialist_subject_types.txt", gen_types())
    w("common/specialist_subject_perks/ps_specialist_subject_perks.txt", gen_perks())
    w("common/agreement_term_values/ps_agreement_term_values.txt", gen_term_values())
    w("common/agreement_presets/ps_specialist_presets.txt", gen_presets())
    w("interface/ps_specialists.gfx", gen_gfx())
    w("common/message_types/ps_message_types.txt", gen_message_types())
    for lang in ("russian", "english"):
        p = ROOT / f"localisation/{lang}/ps_specialists_l_{lang}.yml"
        p.write_bytes(b"\xef\xbb\xbf" + loc(lang).encode("utf-8"))

    # иконки-заглушки
    try:
        from build_assets import icon, save_dds  # noqa
        from PIL import ImageDraw
    except ImportError:
        print("Pillow не найден — иконки не созданы")
        return
    kinds = {"ps_trust": "press", "ps_strike": "star", "ps_assault": "tree", "ps_raiders": "net", "ps_residency": "eye", "ps_exchange": "crown"}
    for T in TYPES:
        k = T["key"]
        save_dds(icon(kinds[k], 40), f"gfx/interface/icons/specialists/{k}.dds")
        save_dds(icon(kinds[k], 80), f"gfx/interface/icons/specialists/{k}_large.dds")
        for i, Lv in enumerate(T["levels"], 1):
            for p in Lv["perks"]:
                img = icon(kinds[k], 48)
                d = ImageDraw.Draw(img)
                for j in range(i):  # точки = уровень
                    d.ellipse([6 + j * 8, 38, 12 + j * 8, 44], fill=T["color"] + (255,))
                save_dds(img, f"gfx/interface/icons/specialists/perks/{perk_key(k, i, p[0])}.dds")
    print("ok")


if __name__ == "__main__":
    main()
