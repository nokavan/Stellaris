#!/usr/bin/env python3
"""Генератор новых шпионских операций Синдиката (набор 2).

Создаёт:
  common/espionage_operation_types/ps_operations_2.txt
  events/ps_spy2_events.txt            (namespace ps_spy2)
  common/static_modifiers/ps_spy2_modifiers.txt
  localisation/{russian,english}/ps_spy2_l_*.yml

Формат — как у существующих операций (ps_operations.txt / ps_covert_events.txt).
Запуск: python3 tools/gen_spy_ops2.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICON = "gfx/interface/icons/modifiers/mod_ps_partisan.dds"

# key, (diff1, diff2), spy_power, influence, extra_allow, result_effect, modifiers{name: (mods, ru, en)}, ru(name, desc, result), en(...)
OPS = [
    dict(key="bribe_governors", diff=(4, 6), power=30, inf=40,
         allow="",
         effect="""		target = {
			random_owned_planet = {
				limit = { is_capital = no }
				add_modifier = { modifier = ps_spy_bribed_governor days = 1800 }
			}
		}
		owner = { add_resource = { influence = 75 } }
""",
         mods={"ps_spy_bribed_governor": ({"planet_stability_add": -10, "planet_crime_add": 20},
                                          "Подкупленный губернатор", "Bribed Governor")},
         ru=("Подкуп губернаторов", "Губернатор одной из колоний цели начинает работать на нас.",
             "Губернатор взял деньги. Его колония теряет порядок (§R−10§! стабильности, §R+20§! преступности на 5 лет), а мы получаем §G75§! влияния."),
         en=("Bribe Governors", "A governor of one of the target's colonies starts working for us.",
             "The governor took the money. The colony loses order (§R−10§! stability, §R+20§! crime for 5 years) and we gain §G75§! influence.")),
    dict(key="steal_blueprints", diff=(5, 7), power=35, inf=30,
         allow="",
         effect="""		owner = {
			add_monthly_resource_mult = { resource = engineering_research value = 6 min = 200 max = 3000 }
			add_monthly_resource_mult = { resource = physics_research value = 3 min = 100 max = 1500 }
		}
""",
         mods={},
         ru=("Кража чертежей", "Агенты проникают в конструкторские бюро цели и копируют чертежи.",
             "Чертежи у нас: получаем исследования в объёме §Y6§! месяцев инженерных и §Y3§! месяцев физических."),
         en=("Steal Blueprints", "Agents infiltrate the target's design bureaus and copy the blueprints.",
             "The blueprints are ours: we gain §Y6§! months of engineering and §Y3§! months of physics research.")),
    dict(key="counterfeit_credits", diff=(5, 6), power=35, inf=40,
         allow="",
         effect="""		target = { add_modifier = { modifier = ps_spy_counterfeit days = 1800 } }
		owner = { add_resource = { energy = 500 } }
""",
         mods={"ps_spy_counterfeit": ({"country_energy_produces_mult": -0.10},
                                      "Фальшивые кредиты", "Counterfeit Credits")},
         ru=("Фальшивые кредиты", "Синдикат наводняет рынок цели поддельной валютой.",
             "Рынок цели наводнён подделками: её энергия §R−10%§! на 5 лет, мы получаем §G500§! энергии."),
         en=("Counterfeit Credits", "The Syndicate floods the target's market with fake currency.",
             "The target's market is flooded with fakes: its energy §R−10%§! for 5 years, we gain §G500§! energy.")),
    dict(key="turn_vassals", diff=(6, 8), power=50, inf=75,
         allow="""		custom_tooltip = {
			fail_text = operation_ps_target_no_subjects
			target = { any_subject = { always = yes } }
		}
""",
         effect="""		target = {
			save_event_target_as = ps_spy_overlord
			every_subject = {
				save_event_target_as = ps_spy_sv
				event_target:ps_spy_overlord = {
					random_agreement = {
						limit = {
							owner = { is_same_value = event_target:ps_spy_overlord }
							target = { is_same_value = event_target:ps_spy_sv }
						}
						add_loyalty = -40
					}
				}
				set_timed_country_flag = { flag = ps_puppet_council days = 3600 }
				add_opinion_modifier = { who = root.owner modifier = opinion_ps_puppet_council }
			}
		}
""",
         mods={},
         ru=("Перевербовка вассалов", "Агенты убеждают вассалов цели, что настоящий друг — Синдикат.",
             "Вассалы цели колеблются: их лояльность сюзерену §R−40§!, а их советы готовы перейти под нашу руку («Марионеточный совет» на 10 лет)."),
         en=("Turn Their Subjects", "Agents convince the target's subjects that their true friend is the Syndicate.",
             "The target's subjects waver: loyalty to their overlord §R−40§!, and their councils are ready to switch to us («Puppet Council» for 10 years).")),
    dict(key="blackmail_ruler", diff=(6, 7), power=40, inf=50,
         allow="",
         effect="""		target = { add_modifier = { modifier = ps_spy_blackmailed days = 1800 } }
		owner = { add_modifier = { modifier = ps_spy_blackmail_income days = 1800 } }
""",
         mods={"ps_spy_blackmailed": ({"country_base_influence_produces_add": -1},
                                      "Шантаж правителя", "Blackmailed Ruler"),
               "ps_spy_blackmail_income": ({"country_base_influence_produces_add": 1},
                                           "Плата за молчание", "Hush Money")},
         ru=("Шантаж правителя", "Синдикат находит, чем прижать правителя цели.",
             "Правитель платит за молчание: §R−1§! влияния в месяц у цели и §G+1§! у нас на 5 лет."),
         en=("Blackmail the Ruler", "The Syndicate finds leverage on the target's ruler.",
             "The ruler pays for silence: §R−1§! influence per month for the target and §G+1§! for us for 5 years.")),
    dict(key="market_crash", diff=(6, 8), power=45, inf=60,
         allow="",
         effect="""		target = { add_modifier = { modifier = ps_spy_market_crash days = 1080 } }
		owner = { add_resource = { energy = 300 minerals = 300 } }
""",
         mods={"ps_spy_market_crash": ({"country_consumer_goods_produces_mult": -0.15, "planet_stability_add": -5},
                                       "Обвал биржи", "Market Crash")},
         ru=("Обвал биржи", "Слухи, паника и короткие продажи — биржа цели рушится.",
             "Биржа рухнула: у цели §R−15%§! товаров и §R−5§! стабильности на 3 года, мы скупили активы — §G300§! энергии и минералов."),
         en=("Market Crash", "Rumours, panic and short selling bring the target's exchange down.",
             "The exchange collapsed: the target suffers §R−15%§! goods and §R−5§! stability for 3 years; we bought the assets — §G300§! energy and minerals.")),
    dict(key="brain_drain", diff=(5, 7), power=40, inf=50,
         allow="",
         effect="""		target = { add_modifier = { modifier = ps_spy_brain_drain days = 1800 } }
		owner = { add_modifier = { modifier = ps_spy_defectors days = 1800 } }
""",
         mods={"ps_spy_brain_drain": ({"country_physics_research_produces_mult": -0.10, "country_society_research_produces_mult": -0.10,
                                       "country_engineering_research_produces_mult": -0.10},
                                      "Утечка мозгов", "Brain Drain"),
               "ps_spy_defectors": ({"country_physics_research_produces_mult": 0.05, "country_society_research_produces_mult": 0.05,
                                     "country_engineering_research_produces_mult": 0.05},
                                    "Учёные-перебежчики", "Defector Scientists")},
         ru=("Вербовка перебежчиков", "Лучших учёных цели переманивают в лаборатории Синдиката.",
             "Учёные бежали к нам: у цели §R−10%§! к науке, у нас §G+5%§! на 5 лет."),
         en=("Recruit Defectors", "The target's best scientists are lured to Syndicate labs.",
             "The scientists defected to us: the target suffers §R−10%§! research, we gain §G+5%§! for 5 years.")),
    dict(key="smuggle_alloys", diff=(4, 6), power=30, inf=30,
         allow="",
         effect="""		target = { add_modifier = { modifier = ps_spy_alloy_theft days = 1080 } }
		owner = { add_resource = { alloys = 250 } }
""",
         mods={"ps_spy_alloy_theft": ({"country_alloys_produces_mult": -0.10},
                                      "Хищения со складов", "Warehouse Theft")},
         ru=("Контрабанда сплавов", "Со складов цели «пропадают» эшелоны сплавов.",
             "Эшелоны ушли налево: у цели §R−10%§! сплавов на 3 года, у нас §G+250§! сплавов."),
         en=("Smuggle Alloys", "Trainloads of alloys «go missing» from the target's warehouses.",
             "The trains went astray: the target suffers §R−10%§! alloys for 3 years, we gain §G+250§! alloys.")),
]


def fmt(v):
    return f"{v:g}"


def main():
    ops = ["# АВТОГЕНЕРАЦИЯ: tools/gen_spy_ops2.py — правьте генератор\n# Синдикат Сопротивления — шпионские операции, набор 2\n"]
    ev = ["# АВТОГЕНЕРАЦИЯ: tools/gen_spy_ops2.py\nnamespace = ps_spy2\n",
          """# Этап 1 (общий для всех операций набора): агенты на месте
espionage_operation_event = {
	id = ps_spy2.1
	title = ps_spy2.1.name
	desc = ps_spy2.1.desc
	espionage_operation = yes
	picture = GFX_evt_spy_network
	show_sound = event_default
	is_triggered_only = yes

	option = { name = ps_spy2.1.a }
}
"""]
    mods = [f'# АВТОГЕНЕРАЦИЯ: tools/gen_spy_ops2.py\n@ps_spy2_icon = "{ICON}"\n']
    ru = ["﻿l_russian:\n",
          ' ps_spy2.1.name:0 "Агенты на месте"\n',
          ' ps_spy2.1.desc:0 "Наши люди в §Y[target.GetName]§! получили доступ, документы и легенду. Осталось сделать дело."\n',
          ' ps_spy2.1.a:0 "Продолжайте."\n',
          ' operation_ps_target_no_subjects:0 "У цели нет вассалов."\n']
    en = ["﻿l_english:\n",
          ' ps_spy2.1.name:0 "Agents in Place"\n',
          ' ps_spy2.1.desc:0 "Our people in §Y[target.GetName]§! have access, papers and a cover story. All that remains is the job."\n',
          ' ps_spy2.1.a:0 "Proceed."\n',
          ' operation_ps_target_no_subjects:0 "The target has no subjects."\n']
    for i, o in enumerate(OPS, start=10):
        k = f"operation_ps_{o['key']}"
        ops.append(f"""{k} = {{
	target = none
	categories = {{ op_cat_subterfuge op_cat_economy }}
	picture = GFX_evt_spy_network
	desc = {k}_desc
	stages = 2
	spy_power_cost = {o['power']}
	resources = {{
		category = operations
		cost = {{ influence = {o['inf']} }}
		upkeep = {{ energy = 5 }}
	}}
	potential = {{
		has_nemesis = yes
		owner = {{ ps_is_partisan_empire = yes }}
		target = {{ is_country_type = default }}
	}}
	allow = {{
{o['allow']}		custom_tooltip = {{
			is_running_espionage_operation = no
			fail_text = operation_one_at_a_time
		}}
	}}
	stage = {{
		difficulty = {o['diff'][0]}
		icon = GFX_espionage_chapter_icon_surveillance
		event = ps_spy2.1
	}}
	stage = {{
		difficulty = {o['diff'][1]}
		icon = GFX_espionage_chapter_icon_success
		event = ps_spy2.{i}
	}}
	on_roll_failed = {{
		standard_espionage_operation_on_roll_failed = {{ RANDOM_EVENTS = operation_random_events_generic }}
	}}
	on_create = {{}}
}}
""")
        ev.append(f"""espionage_operation_event = {{
	id = ps_spy2.{i}
	title = ps_spy2.{i}.name
	desc = ps_spy2.{i}.desc
	espionage_operation = yes
	picture = GFX_evt_spy_network
	show_sound = event_espionage_concluded
	is_triggered_only = yes

	option = {{
		name = ps_spy2.{i}.a
{o['effect']}	}}

	after = {{ destroy_espionage_operation = this }}
}}
""")
        for mk, (md, rn, enn) in o["mods"].items():
            mods.append(f"{mk} = {{\n\ticon = @ps_spy2_icon\n\ticon_frame = 1\n" +
                        "".join(f"\t{a} = {fmt(b)}\n" for a, b in md.items()) + "}\n")
            ru.append(f' {mk}:0 "{rn}"\n')
            en.append(f' {mk}:0 "{enn}"\n')
        rn, rd, rr = o["ru"]
        en_n, en_d, en_r = o["en"]
        ru += [f' {k}:0 "{rn}"\n', f' {k}_desc:0 "{rd}"\n',
               f' ps_spy2.{i}.name:0 "{rn}: успех"\n', f' ps_spy2.{i}.desc:0 "{rr}"\n', f' ps_spy2.{i}.a:0 "Отличная работа."\n']
        en += [f' {k}:0 "{en_n}"\n', f' {k}_desc:0 "{en_d}"\n',
               f' ps_spy2.{i}.name:0 "{en_n}: Success"\n', f' ps_spy2.{i}.desc:0 "{en_r}"\n', f' ps_spy2.{i}.a:0 "Excellent work."\n']
    out = {
        "common/espionage_operation_types/ps_operations_2.txt": "\n".join(ops),
        "events/ps_spy2_events.txt": "\n".join(ev),
        "common/static_modifiers/ps_spy2_modifiers.txt": "\n".join(mods),
        "localisation/russian/ps_spy2_l_russian.yml": "".join(ru),
        "localisation/english/ps_spy2_l_english.yml": "".join(en),
    }
    for rel, text in out.items():
        (ROOT / rel).write_text(text, encoding="utf-8")
    print("ok:", len(OPS), "operations")


if __name__ == "__main__":
    main()
