#!/usr/bin/env python3
"""Генератор кризисов Синдиката — 5 ситуаций, вызываемых шпионскими операциями.

Создаёт:
  common/situations/ps_crises.txt                         5 ситуаций (кризисов) у жертвы
  common/espionage_operation_types/ps_crisis_operations.txt  5 операций-запалов
  common/static_modifiers/ps_crisis_modifiers.txt
  events/ps_crisis_events.txt                             запуск, финалы, награды покровителю
  localisation/{russian,english}/ps_crises_l_*.yml

Формат ситуаций сверен с vanilla 4.x:
  situations/99_README_SITUATIONS.txt, 01_overlord_situations.txt, 02_strategic_situations.txt
  (stages/end/modifier, approach/resources/ai_weight, monthly_progress/modifier/add/desc,
   current_situation_approach, start_situation = { type = ... } в скоупе страны).

Запуск из корня репозитория:  python3 tools/gen_crises.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Каждый кризис:
#   stages: список из 4 словарей модификаторов страны-жертвы (стадии 25/50/75/100)
#   approaches: (ключ, иконка, фон, upkeep{}, modifier{}, снижение прогресса, ru, en)
#   finale: текст эффекта финала (в scope ситуации: root = ситуация, owner = жертва)
CRISES = [
    {
        "key": "general_strike",
        "picture": "GFX_evt_alien_propaganda",
        "op_cats": "op_cat_sabotage op_cat_economy",
        "ru": ("Великая забастовка",
               "Профсоюзы, подкупленные иностранным синдикатом, поднимают одну отрасль за другой. Заводы стоят, порты пусты, а забастовочные комитеты требуют всё больше."),
        "en": ("The Great Strike",
               "Unions bribed by a foreign syndicate bring out one industry after another. Factories stand idle, ports are empty, and the strike committees demand more and more."),
        "stages": [
            {"planet_jobs_produces_mult": -0.05, "planet_stability_add": -2},
            {"planet_jobs_produces_mult": -0.10, "planet_stability_add": -4},
            {"planet_jobs_produces_mult": -0.15, "planet_stability_add": -6},
            {"planet_jobs_produces_mult": -0.20, "planet_stability_add": -8},
        ],
        "approaches": [
            ("concessions", "GFX_situation_approach_amenities", "GFX_situation_approach_bg_green",
             {"consumer_goods": 20, "energy": 20}, {}, 3,
             ("Уступки профсоюзам", "Concessions to the Unions"), ("Повышаем зарплаты и закупаем товары.", "Raise wages and buy goods.")),
            ("crackdown", "GFX_situation_approach_whip", "GFX_situation_approach_bg_red",
             {"unity": 30}, {"planet_stability_add": -5}, 2,
             ("Разгон пикетов", "Break the Pickets"), ("Полиция и штрейкбрехеры.", "Police and strikebreakers.")),
        ],
        "finale_ru": "Экономика жертвы парализована на 3 года (§R-25%§! производства, §R-10§! стабильности), а на всех её планетах, кроме столицы, начинается §RСмута§!.",
        "finale_en": "The victim's economy is paralysed for 3 years (§R-25%§! output, §R-10§! stability), and §RUnrest§! breaks out on all its planets except the capital.",
        "finale": """
		owner = {
			add_modifier = { modifier = ps_crisis_strike_aftermath days = 1080 }
			every_owned_planet = {
				limit = { is_capital = no }
				add_modifier = { modifier = ps_sown_dissent days = 1800 }
				if = {
					limit = { exists = event_target:ps_sponsor }
					carrier_event = { id = ps_revolt.50 }
				}
			}
		}""",
        "final_mod": {"planet_jobs_produces_mult": -0.25, "planet_stability_add": -10},
        "final_mod_ru": ("Последствия Великой забастовки", "Экономика ещё не оправилась от забастовки."),
        "final_mod_en": ("Aftermath of the Great Strike", "The economy has not yet recovered from the strike."),
    },
    {
        "key": "insurgency",
        "picture": "GFX_evt_alien_propaganda",
        "op_cats": "op_cat_provocation op_cat_military",
        "ru": ("Партизанская война в тылу",
               "В лесах, шахтах и трущобах империи действуют вооружённые отряды. Патрули исчезают, склады горят, а население помогает партизанам."),
        "en": ("Insurgency in the Rear",
               "Armed bands operate in the empire's forests, mines and slums. Patrols vanish, depots burn, and the population helps the partisans."),
        "stages": [
            {"planet_stability_add": -3, "planet_crime_add": 5},
            {"planet_stability_add": -5, "planet_crime_add": 10, "army_defense_damage_mult": -0.10},
            {"planet_stability_add": -7, "planet_crime_add": 15, "army_defense_damage_mult": -0.20},
            {"planet_stability_add": -10, "planet_crime_add": 20, "army_defense_damage_mult": -0.30},
        ],
        "approaches": [
            ("counterinsurgency", "GFX_situation_approach_whip", "GFX_situation_approach_bg_red",
             {"unity": 30, "energy": 20}, {"pop_happiness": -0.05}, 3,
             ("Контрпартизанская операция", "Counter-Insurgency"), ("Облавы, блокпосты, комендантский час.", "Raids, checkpoints, curfew.")),
            ("amnesty", "GFX_situation_approach_unity", "GFX_situation_approach_bg_green",
             {"influence": 1}, {"pop_happiness": 0.05}, 2,
             ("Амнистия", "Amnesty"), ("Прощаем тех, кто сложит оружие.", "Pardon those who lay down their arms.")),
        ],
        "finale_ru": "На трёх самых нестабильных планетах жертвы (кроме столицы) поднимается §Rвооружённый бунт§!: появляются партизанские отряды, начинается наземный бой.",
        "finale_en": "An §Rarmed uprising§! breaks out on the victim's three least stable planets (except the capital): partisan detachments appear and ground combat begins.",
        "finale": """
		while = {
			count = 3
			owner = {
				random_owned_planet = {
					limit = {
						is_capital = no
						NOT = { has_modifier = ps_armed_underground }
					}
					add_modifier = { modifier = ps_armed_underground days = 1080 }
					carrier_event = { id = ps_sabotage.50 }
					if = {
						limit = { exists = event_target:ps_sponsor }
						carrier_event = { id = ps_revolt.50 }
					}
				}
			}
		}""",
        "final_mod": None,
    },
    {
        "key": "financial_collapse",
        "picture": "GFX_evt_spy_network",
        "op_cats": "op_cat_sabotage op_cat_economy",
        "ru": ("Финансовый крах",
               "Фальшивые деньги, обвал бирж и бегство капитала в офшоры Синдиката. Валюта империи дешевеет с каждым днём."),
        "en": ("Financial Collapse",
               "Counterfeit money, crashing exchanges and capital flight into Syndicate offshores. The empire's currency loses value every day."),
        "stages": [
            {"country_energy_produces_mult": -0.05},
            {"country_energy_produces_mult": -0.10, "country_trade_produces_mult": -0.10},
            {"country_energy_produces_mult": -0.15, "country_trade_produces_mult": -0.15},
            {"country_energy_produces_mult": -0.20, "country_trade_produces_mult": -0.20, "planet_stability_add": -5},
        ],
        "approaches": [
            ("bailout", "GFX_situation_approach_amenities", "GFX_situation_approach_bg_green",
             {"energy": 50}, {}, 4,
             ("Спасение банков", "Bank Bailout"), ("Печатаем деньги и спасаем банки.", "Print money and save the banks.")),
            ("austerity", "GFX_situation_approach_whip", "GFX_situation_approach_bg_red",
             {}, {"pop_happiness": -0.10}, 3,
             ("Жёсткая экономия", "Austerity"), ("Режем расходы на всё.", "Cut spending on everything.")),
        ],
        "finale_ru": "Валюта жертвы обрушена: §R-25%§! энергии на 3 года, а её покровители-партизаны получают §G2000§! энергии.",
        "finale_en": "The victim's currency collapses: §R-25%§! energy for 3 years, and its partisan sponsors receive §G2000§! energy.",
        "finale": """
		owner = {
			add_modifier = { modifier = ps_crisis_bankrupt days = 1080 }
		}
		every_playable_country = {
			limit = { has_country_flag = ps_crisis_sponsor@root.owner }
			add_resource = { energy = 2000 }
		}""",
        "final_mod": {"country_energy_produces_mult": -0.25, "ships_upkeep_mult": 0.15},
        "final_mod_ru": ("Дефолт", "Государство объявило дефолт."),
        "final_mod_en": ("Default", "The state has defaulted on its debts."),
    },
    {
        "key": "legitimacy",
        "picture": "GFX_evt_alien_propaganda",
        "op_cats": "op_cat_manipulation op_cat_government",
        "ru": ("Кризис легитимности",
               "Слитые документы, скандалы и пиратское радио. Люди всё громче спрашивают, по какому праву ими правят."),
        "en": ("Crisis of Legitimacy",
               "Leaked documents, scandals and pirate radio. People ask ever louder by what right they are ruled."),
        "stages": [
            {"country_unity_produces_mult": -0.05, "pop_government_ethic_attraction": -0.10},
            {"country_unity_produces_mult": -0.10, "pop_government_ethic_attraction": -0.20},
            {"country_unity_produces_mult": -0.15, "pop_government_ethic_attraction": -0.30, "country_influence_produces_mult": -0.10},
            {"country_unity_produces_mult": -0.20, "pop_government_ethic_attraction": -0.40, "country_influence_produces_mult": -0.20},
        ],
        "approaches": [
            ("propaganda", "GFX_situation_approach_unity", "GFX_situation_approach_bg_green",
             {"unity": 40}, {}, 3,
             ("Ответная пропаганда", "Counter-Propaganda"), ("Государственные СМИ работают круглосуточно.", "State media work around the clock.")),
            ("reforms", "GFX_situation_approach_amenities", "GFX_situation_approach_bg_yellow",
             {"influence": 2}, {"pop_happiness": 0.05}, 3,
             ("Реформы", "Reforms"), ("Даём людям то, чего они просят.", "Give people what they ask for.")),
        ],
        "finale_ru": "Правитель жертвы §Rсвергнут и убит§!. Империя на 2 года погружается в кризис наследования, а на 5 лет — в глубокое недоверие к власти.",
        "finale_en": "The victim's ruler is §Roverthrown and killed§!. The empire sinks into a succession crisis for 2 years and deep distrust of its government for 5 years.",
        "finale": """
		owner = {
			add_modifier = { modifier = ps_succession_crisis days = 720 }
			add_modifier = { modifier = ps_crisis_regime_discredited days = 1800 }
			if = {
				limit = { exists = ruler }
				ruler = { kill_leader = { show_notification = yes } }
			}
		}""",
        "final_mod": {"pop_government_ethic_attraction": -0.50, "planet_stability_add": -5},
        "final_mod_ru": ("Дискредитированный режим", "Власти никто не верит."),
        "final_mod_en": ("Discredited Regime", "No one trusts the government."),
    },
    {
        "key": "naval_mutiny",
        "picture": "GFX_evt_spy_network",
        "op_cats": "op_cat_subterfuge op_cat_military",
        "ru": ("Мятеж флота",
               "На кораблях ходят листовки, офицеры шепчутся в кают-компаниях, а экипажи всё чаще отказываются выполнять приказы."),
        "en": ("Naval Mutiny",
               "Leaflets circulate aboard ships, officers whisper in the wardrooms, and crews refuse orders more and more often."),
        "stages": [
            {"ship_fire_rate_mult": -0.05},
            {"ship_fire_rate_mult": -0.10, "ship_speed_mult": -0.05},
            {"ship_fire_rate_mult": -0.15, "ship_speed_mult": -0.10},
            {"ship_fire_rate_mult": -0.20, "ship_speed_mult": -0.15, "country_naval_cap_mult": -0.10},
        ],
        "approaches": [
            ("purge_officers", "GFX_situation_approach_whip", "GFX_situation_approach_bg_red",
             {"unity": 30}, {"ship_fire_rate_mult": -0.05}, 3,
             ("Чистка офицеров", "Purge the Officers"), ("Трибуналы и расстрелы.", "Tribunals and executions.")),
            ("pay_raise", "GFX_situation_approach_amenities", "GFX_situation_approach_bg_green",
             {"energy": 40}, {}, 3,
             ("Прибавка жалованья", "Pay Raise"), ("Платим экипажам больше и вовремя.", "Pay the crews more, and on time.")),
        ],
        "finale_ru": "Экипажи поднимают мятеж: эскадра около §R10%§! вместимости флота жертвы уходит к её покровителям-партизанам, а флот жертвы на 2 года деморализован.",
        "finale_en": "The crews mutiny: a squadron of about §R10%§! of the victim's naval capacity defects to its partisan sponsors, and the victim's fleet is demoralised for 2 years.",
        "finale": """
		owner = {
			add_modifier = { modifier = ps_crisis_fleet_purged days = 720 }
			if = {
				limit = { exists = event_target:ps_sponsor }
				create_fleet_from_naval_cap = 0.10
				last_created_fleet = {
					set_owner = event_target:ps_sponsor
				}
			}
		}""",
        "final_mod": {"ship_fire_rate_mult": -0.15, "country_naval_cap_mult": -0.20},
        "final_mod_ru": ("Флот после мятежа", "Командование больше не доверяет экипажам."),
        "final_mod_en": ("Fleet After the Mutiny", "Command no longer trusts its crews."),
    },
]


def g(v):
    return f"{v:g}"


def mods(d, ind):
    t = "\t" * ind
    return "".join(f"{t}{k} = {g(v)}\n" for k, v in d.items())


def situation(c, idx):
    k = f"situation_ps_{c['key']}"
    st = ""
    for i, sm in enumerate(c["stages"], 1):
        st += (f"\t\tps_{c['key']}_stage_{i} = {{\n\t\t\ticon = GFX_situation_stage_{i}\n"
               f"\t\t\ticon_background = GFX_situation_stage_frame_red\n\t\t\tend = {25 * i}\n"
               f"\t\t\tmodifier = {{\n{mods(sm, 4)}\t\t\t}}\n\t\t}}\n")
    ap = (f"\tapproach = {{\n\t\tname = ps_crisis_ignore\n\t\ticon = GFX_situation_approach_this_is_fine\n"
          f"\t\ticon_background = GFX_situation_approach_bg_yellow\n\t\tdefault = yes\n\t\ton_select = {{\n\t\t\tcustom_tooltip = ps_crisis_ignore_tt\n\t\t}}\n\t\tai_weight = {{\n\t\t\tbase = 1\n\t\t}}\n\t}}\n")
    mp = ""
    for (ak, icon, bg, up, am, red, *_t) in c["approaches"]:
        a = f"ps_{c['key']}_{ak}"
        ap += f"\n\tapproach = {{\n\t\tname = {a}\n\t\ticon = {icon}\n\t\ticon_background = {bg}\n"
        if am:
            ap += f"\t\tmodifier = {{\n{mods(am, 3)}\t\t}}\n"
        if up:
            ap += f"\t\tresources = {{\n\t\t\tcategory = situations\n\t\t\tupkeep = {{\n{mods(up, 4)}\t\t\t}}\n\t\t}}\n"
        ap += "\t\tai_weight = {\n\t\t\tbase = 3\n\t\t}\n\t}\n"
        mp += (f"\t\tmodifier = {{\n\t\t\tsubtract = {red}\n\t\t\tdesc = {a}\n"
               f"\t\t\tcurrent_situation_approach = {a}\n\t\t}}\n")
    return f"""
{k} = {{
	picture = {c['picture']}
	category = negative
	situation_log_category = urgent_matters

	fail_icon = GFX_situation_outcome_meh
	fail_icon_frame = GFX_situation_outcome_frame_green
	complete_icon = GFX_situation_outcome_revolt
	complete_icon_frame = GFX_situation_outcome_frame_red

	initial_progress = 20

	stages = {{
{st}	}}

	monthly_progress = {{
		base = 2
		modifier = {{
			add = 1
			desc = ps_crisis_progress_unrest
			owner = {{
				any_owned_planet = {{ planet_stability < 30 }}
			}}
		}}
		modifier = {{
			add = 1
			desc = ps_crisis_progress_agents
			any_playable_country = {{ has_country_flag = ps_crisis_agents@root.owner }}
		}}
{mp}	}}

{ap}
	on_progress_complete = {{
		custom_tooltip = {k}_complete_tooltip
		hidden_effect = {{
			situation_event = {{ id = ps_crisis.{100 + idx} }}
		}}
	}}

	on_fail = {{
		custom_tooltip = ps_crisis_fail_tooltip
		hidden_effect = {{
			owner = {{ add_modifier = {{ modifier = ps_crisis_overcome days = 1800 }} }}
			destroy_situation = this
		}}
	}}
}}
"""


def operation(c, idx):
    return f"""
operation_ps_crisis_{c['key']} = {{
	target = none
	categories = {{ {c['op_cats']} }}
	picture = {c['picture']}
	desc = operation_ps_crisis_{c['key']}_desc
	stages = 4
	spy_power_cost = 80

	resources = {{
		category = operations
		cost = {{ influence = 200 }}
		upkeep = {{ energy = 15 }}
	}}

	potential = {{
		has_nemesis = yes
		owner = {{ ps_is_partisan_empire = yes }}
		target = {{ is_country_type = default }}
	}}
	allow = {{
		custom_tooltip = {{
			fail_text = operation_ps_crisis_already
			target = {{ ps_has_active_crisis = no }}
		}}
		custom_tooltip = {{
			fail_text = operation_ps_crisis_cooldown
			target = {{ NOT = {{ has_country_flag = ps_crisis_cooldown }} }}
		}}
		custom_tooltip = {{
			is_running_espionage_operation = no
			fail_text = operation_one_at_a_time
		}}
	}}
	stage = {{
		difficulty = 8
		icon = GFX_espionage_chapter_icon_surveillance
		event = ps_crisis.1
	}}
	stage = {{
		difficulty = 9
		icon = GFX_espionage_chapter_icon_document
		event = ps_crisis.1
	}}
	stage = {{
		difficulty = 10
		icon = GFX_espionage_chapter_icon_target
		event = ps_crisis.1
	}}
	stage = {{
		difficulty = 11
		icon = GFX_espionage_chapter_icon_success
		event = ps_crisis.{10 + idx}
	}}
	on_roll_failed = {{
		standard_espionage_operation_on_roll_failed = {{ RANDOM_EVENTS = operation_random_events_generic }}
	}}
	on_create = {{
		target = {{
			set_timed_country_flag = {{
				flag = espionage_operation_targeted_by@root.owner
				days = 10800
			}}
		}}
	}}
}}
"""


def events():
    o = ["""#####################################################
# АВТОГЕНЕРАЦИЯ: tools/gen_crises.py — правьте генератор, а не этот файл
# Синдикат Сопротивления — 5 кризисов
#  ps_crisis.1        общий этап операций
#  ps_crisis.11-15    финал операции: запуск кризиса у цели
#  ps_crisis.101-105  финал кризиса (scope = ситуация, owner = жертва)
#  ps_crisis.200      уведомление покровителю
#####################################################

namespace = ps_crisis

espionage_operation_event = {
	id = ps_crisis.1
	title = ps_crisis.1.name
	desc = ps_crisis.1.desc
	espionage_operation = yes
	picture = GFX_evt_spy_network
	show_sound = event_default
	is_triggered_only = yes

	option = { name = ps_crisis.1.a }
}
"""]
    for i, c in enumerate(CRISES, 1):
        k = c["key"]
        o.append(f"""
# Запуск кризиса «{c['ru'][0]}»
espionage_operation_event = {{
	id = ps_crisis.{10 + i}
	title = situation_ps_{k}
	desc = ps_crisis.{10 + i}.desc
	espionage_operation = yes
	picture = {c['picture']}
	show_sound = event_espionage_concluded
	is_triggered_only = yes

	option = {{
		name = ps_crisis.launch.a
		custom_tooltip = ps_crisis.launch.tooltip
		owner = {{
			set_timed_country_flag = {{ flag = ps_crisis_sponsor@root.target days = 3600 }}
			set_timed_country_flag = {{ flag = ps_crisis_agents@root.target days = 1080 }}
		}}
		target = {{
			set_timed_country_flag = {{ flag = ps_crisis_cooldown days = 3600 }}
			start_situation = {{ type = situation_ps_{k} }}
		}}
	}}

	after = {{ destroy_espionage_operation = this }}
}}

# Финал кризиса «{c['ru'][0]}»
situation_event = {{
	id = ps_crisis.{100 + i}
	hide_window = yes
	is_triggered_only = yes

	immediate = {{
		random_playable_country = {{
			limit = {{ has_country_flag = ps_crisis_sponsor@root.owner }}
			save_event_target_as = ps_sponsor
		}}
{c['finale']}
		owner = {{ country_event = {{ id = ps_crisis.{150 + i} }} }}
		every_playable_country = {{
			limit = {{ has_country_flag = ps_crisis_sponsor@root.owner }}
			add_resource = {{ unity = 500 influence = 50 }}
			country_event = {{ id = ps_crisis.200 }}
		}}
		destroy_situation = this
	}}
}}

# Жертве: кризис разразился
country_event = {{
	id = ps_crisis.{150 + i}
	title = situation_ps_{k}
	desc = ps_crisis.{150 + i}.desc
	picture = {c['picture']}
	is_triggered_only = yes

	option = {{ name = ps_crisis.victim.a }}
}}
""")
    o.append("""
# Покровителю: кризис у цели разразился
country_event = {
	id = ps_crisis.200
	title = ps_crisis.200.name
	desc = ps_crisis.200.desc
	picture = GFX_ps_evt_partisans
	is_triggered_only = yes

	option = { name = ps_crisis.200.a }
}
""")
    return "".join(o)


def static_modifiers():
    o = ["# АВТОГЕНЕРАЦИЯ: tools/gen_crises.py\n\n@ps_icon = \"gfx/interface/icons/modifiers/mod_ps_partisan.dds\"\n\n"
         "ps_crisis_overcome = {\n\ticon = @ps_icon\n\ticon_frame = 1\n\tplanet_stability_add = 5\n\tcountry_unity_produces_mult = 0.05\n}\n"]
    for c in CRISES:
        if c["final_mod"]:
            name = {"general_strike": "ps_crisis_strike_aftermath", "financial_collapse": "ps_crisis_bankrupt",
                    "legitimacy": "ps_crisis_regime_discredited", "naval_mutiny": "ps_crisis_fleet_purged"}[c["key"]]
            c["final_mod_key"] = name
            o.append(f"\n{name} = {{\n\ticon = @ps_icon\n\ticon_frame = 3\n{mods(c['final_mod'], 1)}}}\n")
    return "".join(o)


def loc(lang):
    ru = lang == "russian"
    L = [f"l_{lang}:"]
    for i, c in enumerate(CRISES, 1):
        k = c["key"]
        name, desc = c["ru"] if ru else c["en"]
        finale = c["finale_ru"] if ru else c["finale_en"]
        sk = f"situation_ps_{k}"
        L += [f' {sk}:0 "{name}"', f' {sk}_type:0 "{name}"', f' {sk}_desc:0 "{desc}"',
              f' {sk}_monthly_change_tooltip:0 "' + ("Кризис растёт сам. Его ускоряют нестабильные планеты и действующие агенты. Замедлить можно подходами." if ru else
                                                      "The crisis grows by itself, faster with unstable planets and active agents. Approaches slow it down.") + '"',
              f' {sk}_complete_tooltip:0 "{finale}"']
        stage_names = (["Брожение", "Волнения", "Кризис", "На грани"] if ru else ["Ferment", "Unrest", "Crisis", "On the Brink"])
        for s in range(1, 5):
            L.append(f' ps_{k}_stage_{s}:0 "{stage_names[s - 1]}"')
        for (ak, _i, _b, _u, _m, red, (anr, ane), (adr, ade)) in c["approaches"]:
            L += [f' ps_{k}_{ak}:0 "{anr if ru else ane}"',
                  f' ps_{k}_{ak}_desc:0 "{(adr if ru else ade)} ' + (f"Прогресс кризиса §G-{red}§! в месяц." if ru else f"Crisis progress §G-{red}§! per month.") + '"']
        L += [f' operation_ps_crisis_{k}:0 "' + ("Кризис: " if ru else "Crisis: ") + f'{name}"',
              f' operation_ps_crisis_{k}_desc:0 "' + (f"Запустить у цели кризис «{name}». " if ru else f"Trigger the «{name}» crisis in the target. ") + f'{desc}\\n\\n' +
              ("§YЕсли цель не справится:§! " if ru else "§YIf the target fails to cope:§! ") + f'{finale}"',
              f' ps_crisis.{10 + i}.desc:0 "' + (f"Всё готово. Сеть Синдиката в империи §Y[target.GetName]§! получила сигнал, и кризис «{name}» начался." if ru else
                                                 f"Everything is ready. The Syndicate network in §Y[target.GetName]§! has received the signal, and the «{name}» crisis has begun.") + '"',
              f' ps_crisis.{150 + i}.desc:0 "{desc}\\n\\n' + ("Мы не справились. " if ru else "We failed to cope. ") + f'{finale}"']
        if c.get("final_mod_key"):
            n, d = c["final_mod_ru"] if ru else c["final_mod_en"]
            L += [f' {c["final_mod_key"]}:0 "{n}"', f' {c["final_mod_key"]}_desc:0 "{d}"']
    if ru:
        L += [' ps_crisis_ignore:0 "Переждать"', ' ps_crisis_ignore_desc:0 "Ничего не предпринимать и надеяться, что само пройдёт."', ' ps_crisis_ignore_tt:0 "Без расходов и бонусов: кризис развивается сам."',
              ' ps_crisis_progress_unrest:0 "Нестабильные планеты"', ' ps_crisis_progress_agents:0 "Иностранные агенты"',
              ' ps_crisis_fail_tooltip:0 "Кризис преодолён: §G+5§! стабильности и §G+5%§! единства на 5 лет."',
              ' ps_crisis_overcome:0 "Кризис преодолён"', ' ps_crisis_overcome_desc:0 "Мы выстояли, и это нас сплотило."',
              ' operation_ps_crisis_already:0 "В империи цели уже идёт кризис Синдиката."',
              ' operation_ps_crisis_cooldown:0 "Цель недавно пережила кризис Синдиката (раз в 10 лет)."',
              ' ps_crisis.1.name:0 "Подготовка кризиса"', ' ps_crisis.1.desc:0 "Агенты Синдиката закладывают основу кризиса в империи §Y[target.GetName]§!."', ' ps_crisis.1.a:0 "Продолжайте."',
              ' ps_crisis.launch.a:0 "Начинаем."', ' ps_crisis.launch.tooltip:0 "У цели начинается §Rкризис§!. Первые 3 года наши агенты ускоряют его (§R+1§! в месяц). Если цель не справится, мы получаем §G500§! единства и §G50§! влияния. Следующий кризис у этой цели — не раньше чем через 10 лет."',
              ' ps_crisis.victim.a:0 "Проклятые партизаны!"',
              ' ps_crisis.200.name:0 "Кризис разразился"', ' ps_crisis.200.desc:0 "Кризис, который наши агенты запустили в чужой империи, достиг пика. Цель не справилась."', ' ps_crisis.200.a:0 "Сеть делает своё дело."']
    else:
        L += [' ps_crisis_ignore:0 "Wait It Out"', ' ps_crisis_ignore_desc:0 "Do nothing and hope it passes."', ' ps_crisis_ignore_tt:0 "No costs or bonuses: the crisis runs its course."',
              ' ps_crisis_progress_unrest:0 "Unstable planets"', ' ps_crisis_progress_agents:0 "Foreign agents"',
              ' ps_crisis_fail_tooltip:0 "Crisis overcome: §G+5§! stability and §G+5%§! unity for 5 years."',
              ' ps_crisis_overcome:0 "Crisis Overcome"', ' ps_crisis_overcome_desc:0 "We endured, and it brought us together."',
              ' operation_ps_crisis_already:0 "A Syndicate crisis is already under way in the target empire."',
              ' operation_ps_crisis_cooldown:0 "The target recently went through a Syndicate crisis (once per 10 years)."',
              ' ps_crisis.1.name:0 "Preparing the Crisis"', ' ps_crisis.1.desc:0 "Syndicate agents lay the groundwork for a crisis in §Y[target.GetName]§!."', ' ps_crisis.1.a:0 "Proceed."',
              ' ps_crisis.launch.a:0 "Begin."', ' ps_crisis.launch.tooltip:0 "A §Rcrisis§! begins in the target. For the first 3 years our agents accelerate it (§R+1§! per month). If the target fails to cope, we gain §G500§! unity and §G50§! influence. The next crisis for this target is possible in 10 years at the earliest."',
              ' ps_crisis.victim.a:0 "Cursed partisans!"',
              ' ps_crisis.200.name:0 "The Crisis Erupts"', ' ps_crisis.200.desc:0 "The crisis our agents started in a foreign empire has peaked. The target failed to cope."', ' ps_crisis.200.a:0 "The network does its work."']
    return "\n".join(L) + "\n"


def main():
    hdr = "# АВТОГЕНЕРАЦИЯ: tools/gen_crises.py — правьте генератор, а не этот файл\n# Синдикат Сопротивления — 5 кризисов (ситуации у жертвы)\n"
    (ROOT / "common/situations").mkdir(parents=True, exist_ok=True)
    (ROOT / "common/static_modifiers/ps_crisis_modifiers.txt").write_text(static_modifiers(), encoding="utf-8")
    (ROOT / "common/situations/ps_crises.txt").write_text(hdr + "".join(situation(c, i) for i, c in enumerate(CRISES, 1)), encoding="utf-8")
    (ROOT / "common/espionage_operation_types/ps_crisis_operations.txt").write_text(
        hdr.replace("5 кризисов (ситуации у жертвы)", "операции, запускающие кризисы") + "".join(operation(c, i) for i, c in enumerate(CRISES, 1)), encoding="utf-8")
    (ROOT / "events/ps_crisis_events.txt").write_text(events(), encoding="utf-8")
    for lang in ("russian", "english"):
        (ROOT / f"localisation/{lang}/ps_crises_l_{lang}.yml").write_bytes(b"\xef\xbb\xbf" + loc(lang).encode("utf-8"))
    print("ok:", len(CRISES), "crises")


if __name__ == "__main__":
    main()
