#!/usr/bin/env python3
"""Генератор «Управления вассалами» Синдиката Сопротивления.

Создаёт:
  events/ps_vassal_mgmt_events.txt          ps_vm.*  — меню, передача систем, обзор, карточка, бюджет
  common/scripted_effects/ps_vm_effects.txt
  common/scripted_triggers/ps_vm_triggers.txt
  common/scripted_loc/ps_vm_scripted_loc.txt
  common/decisions/ps_vassal_decisions.txt   решение «Управление вассалами» + вассальные проекты
  common/static_modifiers/ps_vm_modifiers.txt
  localisation/{russian,english}/ps_vm_l_*.yml

Проверенные по ванили/модам 4.x конструкции: export_trigger_value_to_variable,
has_monthly_income, resource_stockpile_compare, random_agreement { add_loyalty },
every_subject / any_subject, random_system / random_system_within_border,
has_ground_combat, solar_system.starbase { set_owner }, check_variable с event_target:X.var.

Запуск: python3 tools/gen_vassal_mgmt.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = []  # (path, text)

SUBJ = "is_subject = yes\n\toverlord = { is_same_value = root }"

# ---------------------------------------------------------------------------
# Лестницы значений
# ---------------------------------------------------------------------------
INCOME_RES = ["energy", "minerals", "food", "alloys", "consumer_goods",
              "physics_research", "society_research", "engineering_research",
              "rare_crystals", "exotic_gases", "volatile_motes", "unity", "influence"]
STOCK_RES = ["energy", "minerals", "food", "alloys", "consumer_goods",
             "rare_crystals", "exotic_gases", "volatile_motes", "influence", "unity"]
INC_LADDER = [2000, 1000, 500, 300, 200, 150, 100, 75, 50, 30, 20, 10, 5, 2, 0,
              -2, -5, -10, -20, -50, -100, -200]
INC_SMALL = [100, 50, 30, 20, 15, 10, 5, 3, 2, 1, 0, -1, -2, -3, -5, -10, -20]  # стратегические
STOCK_LADDER = [100000, 50000, 25000, 10000, 5000, 2500, 1000, 500, 250, 100, 0]
STOCK_SMALL = [5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 0]
SMALL = {"rare_crystals", "exotic_gases", "volatile_motes"}

# группа: (переменная, ресурсы, [(порог_нетто, рекомендация_%)...] по убыванию порога)
GROUPS = {
    "basic": (["energy", "minerals", "food"],
              [(300, 75), (150, 50), (75, 25), (25, 10), (0, 0), (-25, -10), (-75, -25), (-150, -50)], -75),
    "adv": (["alloys", "consumer_goods"],
            [(80, 75), (40, 50), (20, 25), (8, 10), (0, 0), (-8, -10), (-20, -25), (-40, -50)], -75),
    "res": (["physics_research", "society_research", "engineering_research"],
            [(300, 75), (150, 50), (75, 25), (25, 10), (0, 0), (-25, -10), (-75, -25), (-150, -50)], -75),
    "str": (["rare_crystals", "exotic_gases", "volatile_motes"],
            [(20, 75), (10, 50), (5, 25), (2, 10), (0, 0), (-2, -10), (-5, -25), (-10, -50)], -75),
}


def ladder_effect(var, cond, steps, lowest):
    """if/else_if по убыванию порога: var = наибольший порог, для которого cond(t) истинно."""
    s = ""
    for i, t in enumerate(steps):
        kw = "if" if i == 0 else "else_if"
        s += f"\t{kw} = {{\n\t\tlimit = {{ {cond(t)} }}\n\t\tset_variable = {{ which = {var} value = {t} }}\n\t}}\n"
    s += f"\telse = {{\n\t\tset_variable = {{ which = {var} value = {lowest} }}\n\t}}\n"
    return s


# ---------------------------------------------------------------------------
# Скриптовые эффекты
# ---------------------------------------------------------------------------
def gen_effects():
    e = ["# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py — правьте генератор\n"]

    # Сбор статистики (scope = страна)
    s = "ps_vm_collect_stats = {\n"
    for trig, var in (("fleet_power", "ps_fp"), ("num_researched_techs", "ps_tech"),
                      ("used_naval_capacity_integer", "ps_nav"), ("max_naval_capacity", "ps_navmax"),
                      ("controlled_systems", "ps_sysn"), ("num_owned_planets", "ps_pops"),
                      ("diplomacy_weight", "ps_dw"), ("expenses", "ps_exp")):
        s += f"\texport_trigger_value_to_variable = {{ trigger = {trig} variable = {var} rounded = yes }}\n"
    for r in INCOME_RES:
        steps = INC_SMALL if r in SMALL else INC_LADDER
        s += ladder_effect(f"ps_inc_{r}",
                           lambda t, r=r: f"has_monthly_income = {{ resource = {r} value >= {t} }}",
                           steps, steps[-1] * 2)
    for r in STOCK_RES:
        steps = STOCK_SMALL if r in SMALL else STOCK_LADDER
        s += ladder_effect(f"ps_stock_{r}",
                           lambda t, r=r: f"resource_stockpile_compare = {{ resource = {r} value >= {t} }}",
                           steps, 0)
    # суммы по группам и рекомендации
    for g, (res, rec, low) in GROUPS.items():
        s += f"\tset_variable = {{ which = ps_inc_{g} value = ps_inc_{res[0]} }}\n"
        for r in res[1:]:
            s += f"\tchange_variable = {{ which = ps_inc_{g} value = ps_inc_{r} }}\n"
        # рекомендация: наибольший порог, который перекрыт балансом группы -> процент
        for i, (t, p) in enumerate(rec):
            kw = "if" if i == 0 else "else_if"
            s += (f"\t{kw} = {{\n\t\tlimit = {{ check_variable = {{ which = ps_inc_{g} value >= {t} }} }}\n"
                  f"\t\tset_variable = {{ which = ps_rec_{g} value = {p} }}\n\t}}\n")
        s += f"\telse = {{\n\t\tset_variable = {{ which = ps_rec_{g} value = {low} }}\n\t}}\n"
    s += "}\n\n"
    e.append(s)

    # Рекомендованная специализация (scope = вассал, event_target:ps_vm_overlord)
    e.append("""# Рекомендация специализации по сильным сторонам вассала (scope = вассал)
ps_vm_recommend_spec = {
	remove_country_flag = ps_rec_spec_strike
	remove_country_flag = ps_rec_spec_trust
	remove_country_flag = ps_rec_spec_exchange
	remove_country_flag = ps_rec_spec_residency
	remove_country_flag = ps_rec_spec_devotee
	remove_country_flag = ps_rec_spec_assault
	if = {
		limit = { check_variable = { which = ps_fp value >= event_target:ps_vm_overlord.ps_fp_half } }
		set_country_flag = ps_rec_spec_strike
	}
	else_if = {
		limit = { check_variable = { which = ps_inc_res value >= 150 } }
		set_country_flag = ps_rec_spec_residency
	}
	else_if = {
		limit = {
			check_variable = { which = ps_inc_minerals value >= 50 }
			check_variable = { which = ps_inc_food value >= 20 }
		}
		set_country_flag = ps_rec_spec_trust
	}
	else_if = {
		limit = { check_variable = { which = ps_inc_energy value >= 50 } }
		set_country_flag = ps_rec_spec_exchange
	}
	else_if = {
		limit = { check_variable = { which = ps_inc_unity value >= 20 } }
		set_country_flag = ps_rec_spec_devotee
	}
	else = {
		set_country_flag = ps_rec_spec_assault
	}
}

# Подготовка меню (scope = сюзерен): выбранная ячейка и курсор системы
ps_vm_prepare = {
	save_event_target_as = ps_vm_overlord
	random_playable_country = {
		limit = {
			is_subject = yes
			overlord = { is_same_value = root }
			has_country_flag = ps_cell_selected
		}
		save_event_target_as = ps_cell
	}
	if = {
		limit = { NOT = { exists = event_target:ps_cell } }
		random_playable_country = {
			limit = {
				is_subject = yes
				overlord = { is_same_value = root }
			}
			set_country_flag = ps_cell_selected
			save_event_target_as = ps_cell
		}
	}
	random_system = {
		limit = {
			has_star_flag = ps_sys_cursor
			exists = space_owner
			space_owner = {
				OR = {
					is_same_value = root
					AND = {
						is_subject = yes
						overlord = { is_same_value = root }
					}
				}
			}
		}
		save_event_target_as = ps_sys
		space_owner = { save_event_target_as = ps_sys_owner }
	}
	# цена: 25 влияния + 50 за каждую колонию владельца в системе
	set_variable = { which = ps_sys_cost value = 25 }
	set_variable = { which = ps_sys_colonies value = 0 }
	if = {
		limit = { exists = event_target:ps_sys }
		event_target:ps_sys = {
			every_system_planet = {
				limit = {
					exists = owner
					owner = { is_same_value = event_target:ps_sys_owner }
				}
				root = {
					change_variable = { which = ps_sys_cost value = 50 }
					change_variable = { which = ps_sys_colonies value = 1 }
				}
			}
		}
	}
}

ps_vm_cursor_clear = {
	every_system = {
		limit = { has_star_flag = ps_sys_cursor }
		remove_star_flag = ps_sys_cursor
	}
}

# Курсор по системам страны OWNER (каждая система по разу за круг)
ps_vm_cursor_in = {
	ps_vm_cursor_clear = yes
	$OWNER$ = {
		if = {
			limit = { NOT = { any_system_within_border = { NOT = { has_star_flag = $SEEN$ } } } }
			every_system_within_border = { remove_star_flag = $SEEN$ }
		}
		random_system_within_border = {
			limit = { NOT = { has_star_flag = $SEEN$ } }
			set_star_flag = $SEEN$
			set_star_flag = ps_sys_cursor
		}
	}
}

# Курсор по системам любых вассалов сюзерена (scope = сюзерен)
ps_vm_cursor_vassals = {
	ps_vm_cursor_clear = yes
	if = {
		limit = {
			NOT = {
				any_system = {
					exists = space_owner
					space_owner = { is_subject = yes overlord = { is_same_value = root } }
					NOT = { has_star_flag = ps_sys_seen_v }
				}
			}
		}
		every_system = {
			limit = { has_star_flag = ps_sys_seen_v }
			remove_star_flag = ps_sys_seen_v
		}
	}
	random_system = {
		limit = {
			exists = space_owner
			space_owner = { is_subject = yes overlord = { is_same_value = root } }
			NOT = { has_star_flag = ps_sys_seen_v }
		}
		set_star_flag = ps_sys_seen_v
		set_star_flag = ps_sys_cursor
	}
}

# Оплата передачи (scope = сюзерен)
ps_vm_pay_transfer = {
	add_resource = { influence = -25 }
	event_target:ps_sys = {
		every_system_planet = {
			limit = {
				exists = owner
				owner = { is_same_value = event_target:ps_sys_owner }
			}
			root = { add_resource = { influence = -50 } }
		}
	}
}

# Передача системы (scope = система). Чужие объекты (станции кочевников и т. п.) не трогаются.
ps_vm_transfer_system = {
	every_system_planet = {
		limit = {
			exists = owner
			owner = { is_same_value = $GIVER$ }
		}
		set_owner = $RECEIVER$
		set_controller = $RECEIVER$
	}
	starbase = { set_owner = $RECEIVER$ }
	set_timed_star_flag = { flag = ps_sys_transfer_cd days = 1800 }
	remove_star_flag = ps_sys_cursor
}

# Изъятие у вассала: -10 лояльности (scope = сюзерен)
ps_vm_loyalty_penalty = {
	random_agreement = {
		limit = {
			owner = { is_same_value = root }
			target = { is_same_value = $WHO$ }
		}
		add_loyalty = -10
	}
}

# Следующая ячейка (scope = сюзерен)
ps_vm_next_cell = {
	every_subject = {
		limit = { has_country_flag = ps_cell_selected }
		remove_country_flag = ps_cell_selected
		set_timed_country_flag = { flag = ps_cell_skip days = 1 }
	}
	random_playable_country = {
		limit = {
			is_subject = yes
			overlord = { is_same_value = root }
			NOT = { has_country_flag = ps_cell_skip }
		}
		set_country_flag = ps_cell_selected
	}
	# если вассал один — оставить его выбранным
	if = {
		limit = { NOT = { any_subject = { has_country_flag = ps_cell_selected } } }
		random_playable_country = {
			limit = {
				is_subject = yes
				overlord = { is_same_value = root }
			}
			set_country_flag = ps_cell_selected
		}
	}
}
""")
    # Лидеры и отстающие
    s = "# Лидеры и отстающие среди вассалов (scope = сюзерен)\nps_vm_rank = {\n"
    for m in ("fp", "tech", "nav", "inc_basic"):
        s += f"""	every_subject = {{
		save_event_target_as = ps_vm_cmp
		if = {{
			limit = {{ root = {{ NOT = {{ any_subject = {{ check_variable = {{ which = ps_{m} value > event_target:ps_vm_cmp.ps_{m} }} }} }} }} }}
			save_event_target_as = ps_vm_lead_{m}
		}}
		if = {{
			limit = {{ root = {{ NOT = {{ any_subject = {{ check_variable = {{ which = ps_{m} value < event_target:ps_vm_cmp.ps_{m} }} }} }} }} }}
			save_event_target_as = ps_vm_lag_{m}
		}}
	}}
"""
    s += "}\n"
    e.append(s)
    OUT.append(("common/scripted_effects/ps_vm_effects.txt", "\n".join(e)))


# ---------------------------------------------------------------------------
# Триггеры передачи
# ---------------------------------------------------------------------------
def gen_triggers():
    afford = "ps_vm_can_afford = {\n\tcustom_tooltip = {\n\t\tfail_text = ps_vm_no_influence\n\t\tOR = {\n"
    for n in range(0, 21):
        c = 25 + 50 * n
        afford += (f"\t\t\tAND = {{ check_variable = {{ which = ps_sys_colonies value = {n} }} "
                   f"resource_stockpile_compare = {{ resource = influence value >= {c} }} }}\n")
    afford += "\t\t}\n\t}\n}\n"
    t = """# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py — правьте генератор

# Можно ли передать систему (scope = система). GIVER — текущий владелец, RECEIVER — получатель.
ps_vm_sys_ok = {
	custom_tooltip = {
		fail_text = ps_vm_fail_peace
		root = { is_at_war = no }
		$GIVER$ = { is_at_war = no }
		$RECEIVER$ = { is_at_war = no }
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_same
		NOT = { $RECEIVER$ = { is_same_value = $GIVER$ } }
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_outpost
		exists = starbase
		starbase = {
			exists = controller
			controller = { is_same_value = $GIVER$ }
		}
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_colonies
		NOT = {
			any_system_planet = {
				exists = owner
				owner = { is_same_value = $GIVER$ }
				OR = {
					NOT = { exists = controller }
					NOT = { controller = { is_same_value = $GIVER$ } }
				}
			}
		}
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_capital
		NOT = { any_system_planet = { is_capital = yes } }
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_last
		$GIVER$ = { any_system_within_border = { NOT = { has_star_flag = ps_sys_cursor } } }
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_combat
		NOT = { any_system_planet = { has_ground_combat = yes } }
	}
	# колония в процессе основания: у планеты уже есть владелец, но ещё нет населения
	custom_tooltip = {
		fail_text = ps_vm_fail_colonizing
		NOT = {
			any_system_planet = {
				exists = owner
				NOT = { any_owned_pop_group = { always = yes } }
			}
		}
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_foreign
		NOT = {
			any_system_planet = {
				exists = owner
				NOT = { owner = { is_same_value = $GIVER$ } }
			}
		}
	}
	custom_tooltip = {
		fail_text = ps_vm_fail_cooldown
		NOT = { has_star_flag = ps_sys_transfer_cd }
	}
}

"""
    OUT.append(("common/scripted_triggers/ps_vm_triggers.txt", t + afford))


# ---------------------------------------------------------------------------
# Scripted loc (текст по условиям)
# ---------------------------------------------------------------------------
SPECS = [("preset_ps_strike", "specialist_ps_strike"), ("preset_ps_assault", "specialist_ps_assault"),
         ("preset_ps_raiders", "specialist_ps_raiders"), ("preset_ps_residency", "specialist_ps_residency"),
         ("preset_ps_exchange", "specialist_ps_exchange"), ("preset_ps_trust", "specialist_ps_trust"),
         ("preset_ps_devotee", "specialist_ps_devotee"), ("preset_ps_client_regime", "preset_ps_client_regime"),
         ("preset_bulwark", "preset_bulwark"), ("preset_prospectorium", "preset_prospectorium"),
         ("preset_scholarium", "preset_scholarium"), ("preset_vassal", "preset_vassal"),
         ("preset_tributary", "preset_tributary"), ("preset_protectorate", "preset_protectorate")]
AUTH = ["auth_democratic", "auth_oligarchic", "auth_dictatorial", "auth_imperial", "auth_corporate",
        "auth_hive_mind", "auth_machine_intelligence"]
AXES = [("Mil", "is_militarist", "ethic_militarist", "is_pacifist", "ethic_pacifist"),
        ("Xen", "is_xenophile", "ethic_xenophile", "is_xenophobe", "ethic_xenophobe"),
        ("Ega", "is_egalitarian", "ethic_egalitarian", "is_authoritarian", "ethic_authoritarian"),
        ("Mat", "is_materialist", "ethic_materialist", "is_spiritualist", "ethic_spiritualist")]


def gen_scripted_loc():
    s = ["# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py\n"]
    t = "defined_text = {\n\tname = PsVmSpec\n"
    for preset, key in SPECS:
        t += f"\ttext = {{\n\t\ttrigger = {{ any_agreement = {{ agreement_preset = {preset} }} }}\n\t\tlocalization_key = {key}\n\t}}\n"
    t += "\ttext = {\n\t\tlocalization_key = ps_vm_none\n\t}\n}\n"
    s.append(t)
    t = "defined_text = {\n\tname = PsVmAuth\n"
    for a in AUTH:
        t += f"\ttext = {{\n\t\ttrigger = {{ has_authority = {a} }}\n\t\tlocalization_key = {a}\n\t}}\n"
    t += "\ttext = {\n\t\tlocalization_key = ps_vm_none\n\t}\n}\n"
    s.append(t)
    for name, t1, k1, t2, k2 in AXES:
        t = (f"defined_text = {{\n\tname = PsVmEth{name}\n"
             f"\ttext = {{\n\t\ttrigger = {{ {t1} = yes }}\n\t\tlocalization_key = {k1}\n\t}}\n"
             f"\ttext = {{\n\t\ttrigger = {{ {t2} = yes }}\n\t\tlocalization_key = {k2}\n\t}}\n"
             f"\ttext = {{\n\t\tlocalization_key = ps_vm_neutral\n\t}}\n}}\n")
        s.append(t)
    t = "defined_text = {\n\tname = PsVmRecSpec\n"
    for f, key in (("strike", "specialist_ps_strike"), ("residency", "specialist_ps_residency"),
                   ("trust", "specialist_ps_trust"), ("exchange", "specialist_ps_exchange"),
                   ("devotee", "specialist_ps_devotee"), ("assault", "specialist_ps_assault")):
        t += f"\ttext = {{\n\t\ttrigger = {{ has_country_flag = ps_rec_spec_{f} }}\n\t\tlocalization_key = ps_vm_recspec_{f}\n\t}}\n"
    t += "\ttext = {\n\t\tlocalization_key = ps_vm_none\n\t}\n}\n"
    s.append(t)
    for g in GROUPS:
        t = (f"defined_text = {{\n\tname = PsVmRec_{g}\n"
             f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ which = ps_rec_{g} value > 0 }} }}\n\t\tlocalization_key = ps_vm_rec_tax\n\t}}\n"
             f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ which = ps_rec_{g} value < 0 }} }}\n\t\tlocalization_key = ps_vm_rec_subsidy\n\t}}\n"
             f"\ttext = {{\n\t\tlocalization_key = ps_vm_rec_keep\n\t}}\n}}\n")
        s.append(t)
    OUT.append(("common/scripted_loc/ps_vm_scripted_loc.txt", "\n".join(s)))


# ---------------------------------------------------------------------------
# Вассальные проекты (решения на столице) и поддержка
# ---------------------------------------------------------------------------
def res3(v):
    return {"country_physics_research_produces_mult": v, "country_society_research_produces_mult": v,
            "country_engineering_research_produces_mult": v}


PROJECTS = [
    ("chancellery", "Имперская канцелярия", "Imperial Chancellery",
     "Канцелярия сюзерена ведёт дела всех вассалов: они лояльнее и спокойнее.",
     "The overlord's chancellery handles the affairs of every subject: they are more loyal and stable.",
     lambda t: {"monthly_loyalty_from_subjects": t, "country_subject_acceptance_add": 10 * t},
     lambda t: {"planet_stability_add": 2 * t}),
    ("development_bank", "Банк развития вассалов", "Subject Development Bank",
     "Дешёвые кредиты для экономики вассалов и процент — сюзерену.",
     "Cheap loans for subject economies, and interest for the overlord.",
     lambda t: {"country_base_energy_produces_add": 5 * t},
     lambda t: {"country_energy_produces_mult": 0.05 * t, "country_minerals_produces_mult": 0.05 * t,
                "country_food_produces_mult": 0.05 * t}),
    ("governor_academy", "Академия наместников", "Academy of Governors",
     "Администраторы, обученные в столице, управляют мирами вассалов.",
     "Administrators trained in the capital govern the subjects' worlds.",
     lambda t: {"leaders_upkeep_mult": -0.05 * t},
     lambda t: {"empire_size_pops_mult": -0.05 * t, "country_unity_produces_mult": 0.05 * t}),
    ("war_college", "Военная коллегия", "War College",
     "Общий штаб сюзерена и вассалов.",
     "A joint staff of the overlord and the subjects.",
     lambda t: {"country_naval_capacity_contribution_from_subjects_mult": 0.05 * t},
     lambda t: {"country_naval_cap_mult": 0.05 * t, "army_damage_mult": 0.05 * t}),
    ("science_exchange", "Научный обмен", "Science Exchange",
     "Учёные вассалов и сюзерена работают в общих институтах.",
     "Subject and overlord scientists work in joint institutes.",
     lambda t: res3(0.02 * t),
     lambda t: res3(0.05 * t)),
]
TIER_COST = {1: {"energy": 2000, "alloys": 500, "influence": 100},
             2: {"energy": 4000, "alloys": 1000, "influence": 200},
             3: {"energy": 8000, "alloys": 2000, "influence": 300}}
ROMAN = {1: "I", 2: "II", 3: "III"}


def fmt(v):
    v = round(v, 4)
    return str(int(v)) if v == int(v) else f"{v:g}"


def mods_block(d, ind="\t"):
    return "".join(f"{ind}{k} = {fmt(v)}\n" for k, v in d.items())


def gen_decisions_and_modifiers():
    d = ["# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py\n# Управление вассалами и вассальные проекты (решения на столице, root = планета)\n",
         """decision_ps_vassal_management = {
	owned_planets_only = yes

	potential = {
		is_capital = yes
		owner = { is_ai = no }
	}

	allow = {
		custom_tooltip = {
			fail_text = decision_ps_no_cells
			owner = { any_subject = { always = yes } }
		}
	}

	effect = {
		owner = { country_event = { id = ps_vm.1 } }
	}
}
"""]
    m = ["# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py\n@ps_vm_icon = \"gfx/interface/icons/modifiers/mod_ps_partisan.dds\"\n",
         """ps_vm_econ_support = {
	icon = @ps_vm_icon
	icon_frame = 1
	country_energy_produces_mult = 0.10
	country_minerals_produces_mult = 0.10
	country_food_produces_mult = 0.10
	country_alloys_produces_mult = 0.05
}

ps_vm_admin_support = {
	icon = @ps_vm_icon
	icon_frame = 1
	planet_stability_add = 5
	empire_size_pops_mult = -0.10
	country_unity_produces_mult = 0.10
}
"""]
    ru, en = [], []
    for key, rn, enn, rd, ed, ov, sub in PROJECTS:
        for t in (1, 2, 3):
            dk = f"decision_ps_vp_{key}_{t}"
            prev = f"\n\t\t\thas_country_flag = ps_vp_{key}_{t-1}" if t > 1 else ""
            rem_prev = f"\t\t\t\tremove_modifier = ps_vp_{key}_ov_{t-1}\n" if t > 1 else ""
            cost = mods_block(TIER_COST[t], "\t\t\t")
            d.append(f"""{dk} = {{
	owned_planets_only = yes

	resources = {{
		category = decisions
		cost = {{
{cost}		}}
	}}

	potential = {{
		is_capital = yes
		owner = {{{prev}
			NOT = {{ has_country_flag = ps_vp_{key}_{t} }}
		}}
	}}

	allow = {{
		custom_tooltip = {{
			fail_text = decision_ps_no_cells
			owner = {{ any_subject = {{ always = yes }} }}
		}}
		custom_tooltip = {{
			fail_text = ps_vp_cooldown
			owner = {{ NOT = {{ has_country_flag = ps_vp_cd }} }}
		}}
	}}

	effect = {{
		custom_tooltip = {dk}_tooltip
		hidden_effect = {{
			owner = {{
				set_country_flag = ps_vp_{key}_{t}
				set_timed_country_flag = {{ flag = ps_vp_cd days = 720 }}
{rem_prev}				add_modifier = {{ modifier = ps_vp_{key}_ov_{t} days = -1 }}
				country_event = {{ id = ps_vm.90 }}
			}}
		}}
	}}

	ai_weight = {{
		weight = 0
	}}
}}
""")
            m.append(f"ps_vp_{key}_ov_{t} = {{\n\ticon = @ps_vm_icon\n\ticon_frame = 1\n{mods_block(ov(t))}}}\n")
            m.append(f"ps_vp_{key}_sub_{t} = {{\n\ticon = @ps_vm_icon\n\ticon_frame = 1\n{mods_block(sub(t))}}}\n")
            cost_ru = f"§Y{TIER_COST[t]['energy']}§! энергии, §Y{TIER_COST[t]['alloys']}§! сплавов, §Y{TIER_COST[t]['influence']}§! влияния"
            ru += [f' {dk}:0 "Проект: {rn} {ROMAN[t]}"\n',
                   f' {dk}_desc:0 "{rd}"\n',
                   f' {dk}_tooltip:0 "Навсегда: сюзерен получает §Y$ps_vp_{key}_ov_{t}$§!, все вассалы — §Y$ps_vp_{key}_sub_{t}$§! (обновляется каждый год и для новых вассалов). Следующий проект — не раньше чем через 2 года."\n',
                   f' ps_vp_{key}_ov_{t}:0 "{rn} {ROMAN[t]}"\n',
                   f' ps_vp_{key}_sub_{t}:0 "{rn} {ROMAN[t]} (вассал)"\n']
            en += [f' {dk}:0 "Project: {enn} {ROMAN[t]}"\n',
                   f' {dk}_desc:0 "{ed}"\n',
                   f' {dk}_tooltip:0 "Permanently: the overlord gains §Y$ps_vp_{key}_ov_{t}$§!, every subject gains §Y$ps_vp_{key}_sub_{t}$§! (refreshed yearly, also for new subjects). Next project no sooner than in 2 years."\n',
                   f' ps_vp_{key}_ov_{t}:0 "{enn} {ROMAN[t]}"\n',
                   f' ps_vp_{key}_sub_{t}:0 "{enn} {ROMAN[t]} (subject)"\n']
    OUT.append(("common/decisions/ps_vassal_decisions.txt", "\n".join(d)))
    OUT.append(("common/static_modifiers/ps_vm_modifiers.txt", "\n".join(m)))
    return ru, en


def gen_project_sync():
    """ps_vm.90: вассалы получают модификаторы проектов сюзерена (scope = сюзерен)."""
    s = "\t\tevery_subject = {\n"
    for key, *_ in PROJECTS:
        for t in (1, 2, 3):
            s += f"\t\t\tremove_modifier = ps_vp_{key}_sub_{t}\n"
        for t in (3, 2, 1):
            kw = "if" if t == 3 else "else_if"
            s += (f"\t\t\t{kw} = {{\n\t\t\t\tlimit = {{ root = {{ has_country_flag = ps_vp_{key}_{t} }} }}\n"
                  f"\t\t\t\tadd_modifier = {{ modifier = ps_vp_{key}_sub_{t} days = -1 }}\n\t\t\t}}\n")
    s += "\t\t}\n"
    return s


# ---------------------------------------------------------------------------
# События
# ---------------------------------------------------------------------------
def gen_events():
    proj_trigger = "\n".join(f"\t\t\thas_country_flag = ps_vp_{k}_1" for k, *_ in PROJECTS)
    sync = gen_project_sync()
    ev = f"""# АВТОГЕНЕРАЦИЯ: tools/gen_vassal_mgmt.py — правьте генератор
#####################################################
# Управление вассалами
#  ps_vm.1   главное меню
#  ps_vm.10  передача систем (курсор системы + выбранная ячейка)
#  ps_vm.11  уведомление вассалу
#  ps_vm.20  обзор: лидеры и отстающие
#  ps_vm.30  карточка вассала (+ поддержка)
#  ps_vm.31  бюджет, запасы и рекомендации
#  ps_vm.90  вассальные проекты: синхронизация модификаторов вассалов
#####################################################

namespace = ps_vm

country_event = {{
	id = ps_vm.1
	title = ps_vm.1.name
	desc = ps_vm.1.desc
	picture = GFX_ps_evt_syndicate
	is_triggered_only = yes

	trigger = {{ any_subject = {{ always = yes }} }}

	immediate = {{ ps_vm_prepare = yes }}

	option = {{
		name = ps_vm.1.systems
		hidden_effect = {{ country_event = {{ id = ps_vm.10 }} }}
	}}
	option = {{
		name = ps_vm.1.overview
		hidden_effect = {{ country_event = {{ id = ps_vm.20 }} }}
	}}
	option = {{
		name = ps_vm.1.card
		hidden_effect = {{ country_event = {{ id = ps_vm.30 }} }}
	}}
	option = {{
		name = ps_vm.1.budget
		hidden_effect = {{ country_event = {{ id = ps_vm.31 }} }}
	}}
	option = {{
		name = ps_vm.1.next
		hidden_effect = {{
			ps_vm_next_cell = yes
			country_event = {{ id = ps_vm.1 }}
		}}
	}}
	option = {{
		name = ps_vm.1.panel
		trigger = {{ ps_is_shadow_overlord = yes }}
		hidden_effect = {{ country_event = {{ id = ps_panel.1 }} }}
	}}
	option = {{
		name = ps_vm.close
	}}
}}

# ПЕРЕДАЧА СИСТЕМ
country_event = {{
	id = ps_vm.10
	title = ps_vm.10.name
	desc = {{
		trigger = {{ exists = event_target:ps_sys }}
		text = ps_vm.10.desc
	}}
	desc = {{
		trigger = {{ NOT = {{ exists = event_target:ps_sys }} }}
		text = ps_vm.10.desc_none
	}}
	picture = GFX_ps_evt_syndicate
	is_triggered_only = yes

	immediate = {{ ps_vm_prepare = yes }}

	option = {{
		name = ps_vm.10.next_own
		hidden_effect = {{
			ps_vm_cursor_in = {{ OWNER = root SEEN = ps_sys_seen_r }}
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	option = {{
		name = ps_vm.10.next_cell
		hidden_effect = {{
			ps_vm_cursor_in = {{ OWNER = event_target:ps_cell SEEN = ps_sys_seen_c }}
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	option = {{
		name = ps_vm.10.next_vassal
		hidden_effect = {{
			ps_vm_cursor_vassals = yes
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	option = {{
		name = ps_vm.10.switch_cell
		hidden_effect = {{
			ps_vm_next_cell = yes
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	# Передать выбранной ячейке (свою систему — без штрафа; систему другого вассала — изъятие)
	option = {{
		name = ps_vm.10.give
		trigger = {{
			exists = event_target:ps_sys
			NOT = {{ event_target:ps_sys_owner = {{ is_same_value = event_target:ps_cell }} }}
		}}
		allow = {{
			event_target:ps_sys = {{ ps_vm_sys_ok = {{ GIVER = event_target:ps_sys_owner RECEIVER = event_target:ps_cell }} }}
			ps_vm_can_afford = yes
		}}
		custom_tooltip = ps_vm.10.give.tooltip
		hidden_effect = {{
			ps_vm_pay_transfer = yes
			if = {{
				limit = {{ NOT = {{ event_target:ps_sys_owner = {{ is_same_value = root }} }} }}
				ps_vm_loyalty_penalty = {{ WHO = event_target:ps_sys_owner }}
			}}
			event_target:ps_sys = {{ ps_vm_transfer_system = {{ GIVER = event_target:ps_sys_owner RECEIVER = event_target:ps_cell }} }}
			event_target:ps_cell = {{ country_event = {{ id = ps_vm.11 }} }}
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	# Забрать себе
	option = {{
		name = ps_vm.10.take
		trigger = {{
			exists = event_target:ps_sys
			NOT = {{ event_target:ps_sys_owner = {{ is_same_value = root }} }}
		}}
		allow = {{
			event_target:ps_sys = {{ ps_vm_sys_ok = {{ GIVER = event_target:ps_sys_owner RECEIVER = root }} }}
			ps_vm_can_afford = yes
		}}
		custom_tooltip = ps_vm.10.take.tooltip
		hidden_effect = {{
			ps_vm_pay_transfer = yes
			ps_vm_loyalty_penalty = {{ WHO = event_target:ps_sys_owner }}
			event_target:ps_sys = {{ ps_vm_transfer_system = {{ GIVER = event_target:ps_sys_owner RECEIVER = root }} }}
			country_event = {{ id = ps_vm.10 }}
		}}
	}}
	option = {{
		name = ps_vm.back
		hidden_effect = {{ country_event = {{ id = ps_vm.1 }} }}
	}}
}}

country_event = {{
	id = ps_vm.11
	title = ps_vm.11.name
	desc = ps_vm.11.desc
	picture = GFX_ps_evt_syndicate
	is_triggered_only = yes

	option = {{ name = ps_vm.11.a }}
}}

# ОБЗОР
country_event = {{
	id = ps_vm.20
	title = ps_vm.20.name
	desc = ps_vm.20.desc
	picture = GFX_ps_evt_spy
	is_triggered_only = yes

	immediate = {{
		ps_vm_prepare = yes
		ps_vm_collect_stats = yes
		every_subject = {{ ps_vm_collect_stats = yes }}
		ps_vm_rank = yes
	}}

	option = {{
		name = ps_vm.back
		hidden_effect = {{ country_event = {{ id = ps_vm.1 }} }}
	}}
	option = {{ name = ps_vm.close }}
}}

# КАРТОЧКА ВАССАЛА
country_event = {{
	id = ps_vm.30
	title = ps_vm.30.name
	desc = ps_vm.30.desc
	picture = GFX_ps_evt_spy
	is_triggered_only = yes

	immediate = {{
		ps_vm_prepare = yes
		ps_vm_collect_stats = yes
		event_target:ps_cell = {{ ps_vm_collect_stats = yes }}
	}}

	option = {{
		name = ps_vm.30.econ
		allow = {{
			resource_stockpile_compare = {{ resource = energy value >= 1000 }}
			resource_stockpile_compare = {{ resource = alloys value >= 250 }}
			custom_tooltip = {{
				fail_text = ps_vm_support_cd
				event_target:ps_cell = {{ NOT = {{ has_country_flag = ps_vm_econ_cd }} }}
			}}
		}}
		add_resource = {{ energy = -1000 alloys = -250 }}
		event_target:ps_cell = {{
			set_timed_country_flag = {{ flag = ps_vm_econ_cd days = 1800 }}
			add_modifier = {{ modifier = ps_vm_econ_support days = 3600 }}
		}}
		hidden_effect = {{ country_event = {{ id = ps_vm.30 }} }}
	}}
	option = {{
		name = ps_vm.30.admin
		allow = {{
			resource_stockpile_compare = {{ resource = influence value >= 100 }}
			resource_stockpile_compare = {{ resource = unity value >= 500 }}
			custom_tooltip = {{
				fail_text = ps_vm_support_cd
				event_target:ps_cell = {{ NOT = {{ has_country_flag = ps_vm_admin_cd }} }}
			}}
		}}
		add_resource = {{ influence = -100 unity = -500 }}
		event_target:ps_cell = {{
			set_timed_country_flag = {{ flag = ps_vm_admin_cd days = 1800 }}
			add_modifier = {{ modifier = ps_vm_admin_support days = 3600 }}
		}}
		hidden_effect = {{
			random_agreement = {{
				limit = {{
					owner = {{ is_same_value = root }}
					target = {{ is_same_value = event_target:ps_cell }}
				}}
				add_loyalty = 10
			}}
			country_event = {{ id = ps_vm.30 }}
		}}
	}}
	option = {{
		name = ps_vm.1.budget
		hidden_effect = {{ country_event = {{ id = ps_vm.31 }} }}
	}}
	option = {{
		name = ps_vm.1.next
		hidden_effect = {{
			ps_vm_next_cell = yes
			country_event = {{ id = ps_vm.30 }}
		}}
	}}
	option = {{
		name = ps_vm.back
		hidden_effect = {{ country_event = {{ id = ps_vm.1 }} }}
	}}
}}

# БЮДЖЕТ И РЕКОМЕНДАЦИИ
country_event = {{
	id = ps_vm.31
	title = ps_vm.31.name
	desc = ps_vm.31.desc
	picture = GFX_ps_evt_spy
	is_triggered_only = yes

	immediate = {{
		ps_vm_prepare = yes
		ps_vm_collect_stats = yes
		set_variable = {{ which = ps_fp_half value = ps_fp }}
		multiply_variable = {{ which = ps_fp_half value = 0.5 }}
		event_target:ps_cell = {{
			ps_vm_collect_stats = yes
			ps_vm_recommend_spec = yes
		}}
	}}

	option = {{
		name = ps_vm.1.next
		hidden_effect = {{
			ps_vm_next_cell = yes
			country_event = {{ id = ps_vm.31 }}
		}}
	}}
	option = {{
		name = ps_vm.1.card
		hidden_effect = {{ country_event = {{ id = ps_vm.30 }} }}
	}}
	option = {{
		name = ps_vm.back
		hidden_effect = {{ country_event = {{ id = ps_vm.1 }} }}
	}}
}}

# Новый вассал (on_becoming_subject: root = вассал, from = сюзерен) — получить проекты сюзерена
country_event = {{
	id = ps_vm.91
	hide_window = yes
	is_triggered_only = yes

	immediate = {{
		from = {{ country_event = {{ id = ps_vm.90 }} }}
	}}
}}

# ВАССАЛЬНЫЕ ПРОЕКТЫ: модификаторы вассалов (scope = сюзерен; ежегодно, при покупке и при новом вассале)
country_event = {{
	id = ps_vm.90
	hide_window = yes
	is_triggered_only = yes

	trigger = {{
		OR = {{
{proj_trigger}
		}}
	}}

	immediate = {{
{sync}	}}
}}
"""
    OUT.append(("events/ps_vassal_mgmt_events.txt", ev))


# ---------------------------------------------------------------------------
# Локализация
# ---------------------------------------------------------------------------
def gen_loc(ru_proj, en_proj):
    B = "\\n"
    budget_ru = (f"§HДоход в месяц (≈ нижняя граница)§!{B}"
                 "£energy£ [ps_cell.ps_inc_energy]  £minerals£ [ps_cell.ps_inc_minerals]  £food£ [ps_cell.ps_inc_food]  "
                 "£alloys£ [ps_cell.ps_inc_alloys]  £consumer_goods£ [ps_cell.ps_inc_consumer_goods]  £unity£ [ps_cell.ps_inc_unity]  £influence£ [ps_cell.ps_inc_influence]" + B +
                 "§HИсследования:§! £physics£ [ps_cell.ps_inc_physics_research]  £society£ [ps_cell.ps_inc_society_research]  £engineering£ [ps_cell.ps_inc_engineering_research]" + B +
                 "§HСтратегические:§! £rare_crystals£ [ps_cell.ps_inc_rare_crystals]  £exotic_gases£ [ps_cell.ps_inc_exotic_gases]  £volatile_motes£ [ps_cell.ps_inc_volatile_motes]" + B +
                 f"§HРасходы всего:§! [ps_cell.ps_exp]{B}{B}"
                 "§HЗапасы (≈ не меньше)§!" + B +
                 "£energy£ [ps_cell.ps_stock_energy]  £minerals£ [ps_cell.ps_stock_minerals]  £food£ [ps_cell.ps_stock_food]  "
                 "£alloys£ [ps_cell.ps_stock_alloys]  £consumer_goods£ [ps_cell.ps_stock_consumer_goods]  £influence£ [ps_cell.ps_stock_influence]  £unity£ [ps_cell.ps_stock_unity]" + B +
                 "£rare_crystals£ [ps_cell.ps_stock_rare_crystals]  £exotic_gases£ [ps_cell.ps_stock_exotic_gases]  £volatile_motes£ [ps_cell.ps_stock_volatile_motes]")
    rec_ru = (f"{B}{B}§HРекомендации по договору§! (баланс группы → выплаты):{B}"
              f"Базовые (энергия, минералы, еда): [ps_cell.ps_inc_basic]/мес → [ps_cell.PsVmRec_basic] §Y[ps_cell.ps_rec_basic]%§!{B}"
              f"Продвинутые (сплавы, товары): [ps_cell.ps_inc_adv]/мес → [ps_cell.PsVmRec_adv] §Y[ps_cell.ps_rec_adv]%§!{B}"
              f"Исследования: [ps_cell.ps_inc_res]/мес → [ps_cell.PsVmRec_res] §Y[ps_cell.ps_rec_res]%§!{B}"
              f"Стратегические: [ps_cell.ps_inc_str]/мес → [ps_cell.PsVmRec_str] §Y[ps_cell.ps_rec_str]%§!{B}{B}"
              f"§HПодходящая специализация:§! [ps_cell.PsVmRecSpec]{B}"
              "§gОценка приблизительная: игра не отдаёт точные доходы в скрипт, поэтому значения округлены вниз по шкале.§!")
    budget_en = (budget_ru.replace("Доход в месяц (≈ нижняя граница)", "Monthly income (≈ lower bound)")
                 .replace("Исследования:", "Research:").replace("Стратегические:", "Strategic:")
                 .replace("Расходы всего:", "Total expenses:").replace("Запасы (≈ не меньше)", "Stockpiles (≈ at least)"))
    rec_en = (f"{B}{B}§HTreaty recommendations§! (group balance → payments):{B}"
              f"Basic (energy, minerals, food): [ps_cell.ps_inc_basic]/mo → [ps_cell.PsVmRec_basic] §Y[ps_cell.ps_rec_basic]%§!{B}"
              f"Advanced (alloys, goods): [ps_cell.ps_inc_adv]/mo → [ps_cell.PsVmRec_adv] §Y[ps_cell.ps_rec_adv]%§!{B}"
              f"Research: [ps_cell.ps_inc_res]/mo → [ps_cell.PsVmRec_res] §Y[ps_cell.ps_rec_res]%§!{B}"
              f"Strategic: [ps_cell.ps_inc_str]/mo → [ps_cell.PsVmRec_str] §Y[ps_cell.ps_rec_str]%§!{B}{B}"
              f"§HSuggested specialization:§! [ps_cell.PsVmRecSpec]{B}"
              "§gEstimate only: the game does not expose exact income to script, so values are rounded down on a scale.§!")

    def rank(lang):
        names = {"ru": [("fp", "Мощь флота"), ("tech", "Наука (изучено технологий)"), ("nav", "Флот (занято вместимости)"), ("inc_basic", "Экономика (баланс базовых)")],
                 "en": [("fp", "Fleet power"), ("tech", "Science (techs researched)"), ("nav", "Fleet (naval capacity used)"), ("inc_basic", "Economy (basic balance)")]}[lang]
        lead, lag = ("лидер", "отстаёт") if lang == "ru" else ("leader", "lagging")
        s = ""
        for m, n in names:
            s += f"§H{n}:§! {lead} §G[ps_vm_lead_{m}.GetName]§! ([ps_vm_lead_{m}.ps_{m}]), {lag} §R[ps_vm_lag_{m}.GetName]§! ([ps_vm_lag_{m}.ps_{m}]); [Root.GetName]: [Root.ps_{m}]{B}"
        return s

    card_ru = (f"§H[ps_cell.GetName]§!{B}"
               f"Специализация: §Y[ps_cell.PsVmSpec]§!{B}Власть: §Y[ps_cell.PsVmAuth]§!{B}"
               f"Принципы: [ps_cell.PsVmEthMil], [ps_cell.PsVmEthXen], [ps_cell.PsVmEthEga], [ps_cell.PsVmEthMat]{B}"
               f"Лояльность — в окне вассала (дипломатия).{B}{B}"
               f"§HСравнение (вассал / сюзерен)§!{B}"
               f"Мощь флота: [ps_cell.ps_fp] / [Root.ps_fp]{B}"
               f"Флот: [ps_cell.ps_nav] из [ps_cell.ps_navmax] / [Root.ps_nav] из [Root.ps_navmax]{B}"
               f"Технологий: [ps_cell.ps_tech] / [Root.ps_tech]{B}"
               f"Систем: [ps_cell.ps_sysn] / [Root.ps_sysn]{B}"
               f"Колоний: [ps_cell.ps_pops] / [Root.ps_pops]{B}"
               f"Дипломатический вес: [ps_cell.ps_dw] / [Root.ps_dw]{B}"
               f"Баланс базовых ресурсов: [ps_cell.ps_inc_basic] / [Root.ps_inc_basic]{B}{B}"
               "§HПоддержка:§! экономическая — +10% к энергии, минералам и еде и +5% к сплавам на 10 лет; административная — +5 к стабильности, −10% к размеру империи, +10% к единству на 10 лет и §G+10§! лояльности. Каждая — раз в 5 лет.")
    card_en = (card_ru.replace("Специализация:", "Specialization:").replace("Власть:", "Authority:")
               .replace("Принципы:", "Ethics:").replace("Лояльность — в окне вассала (дипломатия).", "Loyalty: see the subject's diplomacy window.")
               .replace("Сравнение (вассал / сюзерен)", "Comparison (subject / overlord)").replace("Мощь флота:", "Fleet power:")
               .replace("Флот:", "Fleet:").replace(" из ", " of ").replace("Технологий:", "Techs:").replace("Систем:", "Systems:")
               .replace("Колоний:", "Colonies:").replace("Дипломатический вес:", "Diplomatic weight:")
               .replace("Баланс базовых ресурсов:", "Basic resource balance:")
               .replace("§HПоддержка:§! экономическая — +10% к энергии, минералам и еде и +5% к сплавам на 10 лет; административная — +5 к стабильности, −10% к размеру империи, +10% к единству на 10 лет и §G+10§! лояльности. Каждая — раз в 5 лет.",
                        "§HSupport:§! economic — +10% energy, minerals and food and +5% alloys for 10 years; administrative — +5 stability, −10% empire size, +10% unity for 10 years and §G+10§! loyalty. Each once per 5 years."))

    sys_ru = (f"Выбранная система: §Y[ps_sys.GetName]§!, владелец §Y[ps_sys_owner.GetName]§!, колоний владельца: [Root.ps_sys_colonies].{B}"
              f"Получатель при передаче: ячейка §Y[ps_cell.GetName]§!.{B}"
              f"Цена: §Y[Root.ps_sys_cost]§! влияния (25 + 50 за колонию).{B}{B}"
              "Передавайте системы вассалам, забирайте их территории или перераспределяйте системы между ними. Общая граница не требуется." + B + B +
              "§HПравила:§! изъятие у вассала — §R−10§! лояльности; передача своей системы — без штрафа. Повторно ту же систему можно передать через 5 лет. Нужен мир, контроль форпоста и колоний. Столица и последняя система владельца защищены. Основание колонии, наземные бои и чужие обычные планеты мешают передаче. Чужие объекты (например, станции кочевников) сохраняют владельца.")
    sys_en = (f"Selected system: §Y[ps_sys.GetName]§!, owner §Y[ps_sys_owner.GetName]§!, owner's colonies: [Root.ps_sys_colonies].{B}"
              f"Receiver on transfer: cell §Y[ps_cell.GetName]§!.{B}"
              f"Cost: §Y[Root.ps_sys_cost]§! influence (25 + 50 per colony).{B}{B}"
              "Transfer systems to subjects, take their territory or redistribute systems between them. No shared border required." + B + B +
              "§HRules:§! taking from a subject — §R−10§! loyalty; giving your own system — no penalty. The same system can be transferred again after 5 years. Requires peace and control of the outpost and colonies. Capital and the owner's last system are protected. Colonization in progress, ground combat and foreign regular planets block the transfer. Foreign objects (e.g. nomad stations) keep their owner.")

    ru = ["﻿l_russian:\n",
          ' decision_ps_vassal_management:0 "Управление вассалами"\n',
          ' decision_ps_vassal_management_desc:0 "Передача систем, обзор и карточки вассалов, бюджет и рекомендации по договорам."\n',
          ' ps_vm.1.name:0 "Управление вассалами"\n',
          f' ps_vm.1.desc:0 "Выбранная ячейка: §Y[ps_cell.GetName]§!.{B}{B}Передача систем, сводка по вассалам, карточка выбранного вассала, его бюджет и рекомендации по договору."\n',
          ' ps_vm.1.systems:0 "Передача систем"\n',
          ' ps_vm.1.overview:0 "Обзор вассалов"\n',
          ' ps_vm.1.card:0 "Карточка вассала"\n',
          ' ps_vm.1.budget:0 "Бюджет и рекомендации"\n',
          ' ps_vm.1.next:0 "Следующий вассал"\n',
          ' ps_vm.1.panel:0 "Панель ячеек Синдиката"\n',
          ' ps_vm.back:0 "Назад"\n',
          ' ps_vm.close:0 "Закрыть"\n',
          ' ps_vm.10.name:0 "Передача систем"\n',
          f' ps_vm.10.desc:0 "{sys_ru}"\n',
          f' ps_vm.10.desc_none:0 "Система не выбрана. Выберите систему кнопками ниже.{B}{B}Получатель при передаче: ячейка §Y[ps_cell.GetName]§!."\n',
          ' ps_vm.10.next_own:0 "Следующая наша система"\n',
          ' ps_vm.10.next_cell:0 "Следующая система выбранной ячейки"\n',
          ' ps_vm.10.next_vassal:0 "Следующая система любого вассала"\n',
          ' ps_vm.10.switch_cell:0 "Сменить получателя (следующая ячейка)"\n',
          ' ps_vm.10.give:0 "Передать систему ячейке §Y[ps_cell.GetName]§!"\n',
          ' ps_vm.10.give.tooltip:0 "Колонии владельца и форпост переходят к ячейке. Если система принадлежит другому вассалу — это изъятие: §R−10§! его лояльности."\n',
          ' ps_vm.10.take:0 "Забрать систему себе"\n',
          ' ps_vm.10.take.tooltip:0 "Колонии и форпост вассала переходят к нам. Лояльность вассала §R−10§!."\n',
          ' ps_vm.11.name:0 "Новые земли"\n',
          ' ps_vm.11.desc:0 "Сюзерен передал нам систему §Y[ps_sys.GetName]§!."\n',
          ' ps_vm.11.a:0 "Принять"\n',
          ' ps_vm_no_influence:0 "Не хватает влияния (25 + 50 за колонию)."\n',
          ' ps_vm_fail_peace:0 "Нужен мир: ни мы, ни владелец, ни получатель не должны воевать."\n',
          ' ps_vm_fail_same:0 "Система уже принадлежит получателю."\n',
          ' ps_vm_fail_outpost:0 "Владелец должен контролировать форпост системы."\n',
          ' ps_vm_fail_colonies:0 "Владелец должен контролировать все свои колонии в системе."\n',
          ' ps_vm_fail_capital:0 "Столичную систему передать нельзя."\n',
          ' ps_vm_fail_last:0 "Это последняя система владельца."\n',
          ' ps_vm_fail_combat:0 "В системе идут наземные бои."\n',
          ' ps_vm_fail_colonizing:0 "В системе основывается колония."\n',
          ' ps_vm_fail_foreign:0 "В системе есть обычные планеты третьих стран."\n',
          ' ps_vm_fail_cooldown:0 "Эту систему уже передавали в последние 5 лет."\n',
          ' ps_vm.20.name:0 "Обзор вассалов"\n',
          f' ps_vm.20.desc:0 "Лидеры и отстающие среди вассалов, в скобках — значение; в конце строки — для сравнения наши показатели.{B}{B}{rank("ru")}"\n',
          ' ps_vm.30.name:0 "Карточка вассала"\n',
          f' ps_vm.30.desc:0 "{card_ru}"\n',
          ' ps_vm.30.econ:0 "Экономическая поддержка: §Y1000§! энергии и §Y250§! сплавов"\n',
          ' ps_vm.30.admin:0 "Административная поддержка: §Y100§! влияния и §Y500§! единства"\n',
          ' ps_vm_support_cd:0 "Эту поддержку ячейка уже получала в последние 5 лет."\n',
          ' ps_vm_econ_support:0 "Экономическая поддержка сюзерена"\n',
          ' ps_vm_econ_support_desc:0 "Сюзерен вкладывается в нашу экономику."\n',
          ' ps_vm_admin_support:0 "Административная поддержка сюзерена"\n',
          ' ps_vm_admin_support_desc:0 "Советники сюзерена помогают нам управлять мирами."\n',
          ' ps_vm.31.name:0 "Бюджет и рекомендации: [ps_cell.GetName]"\n',
          f' ps_vm.31.desc:0 "{budget_ru}{rec_ru}"\n',
          ' ps_vm_none:0 "нет"\n',
          ' ps_vm_neutral:0 "нейтрально"\n',
          ' ps_vm_rec_tax:0 "можно поднять выплаты сюзерену до"\n',
          ' ps_vm_rec_subsidy:0 "нужна субсидия от сюзерена"\n',
          ' ps_vm_rec_keep:0 "оставить как есть"\n',
          ' ps_vm_recspec_strike:0 "$specialist_ps_strike$ (флот вассала силён — не меньше половины нашего)"\n',
          ' ps_vm_recspec_residency:0 "$specialist_ps_residency$ (сильная наука)"\n',
          ' ps_vm_recspec_trust:0 "$specialist_ps_trust$ (минералы и еда в избытке)"\n',
          ' ps_vm_recspec_exchange:0 "$specialist_ps_exchange$ (энергия в избытке)"\n',
          ' ps_vm_recspec_devotee:0 "$specialist_ps_devotee$ (высокое единство)"\n',
          ' ps_vm_recspec_assault:0 "$specialist_ps_assault$ (явных сильных сторон нет — армии)"\n',
          ' ps_vp_cooldown:0 "Новый вассальный проект можно начать не раньше чем через 2 года после предыдущего."\n',
          ] + ru_proj
    en = ["﻿l_english:\n",
          ' decision_ps_vassal_management:0 "Subject Management"\n',
          ' decision_ps_vassal_management_desc:0 "System transfers, subject overview and cards, budgets and treaty recommendations."\n',
          ' ps_vm.1.name:0 "Subject Management"\n',
          f' ps_vm.1.desc:0 "Selected cell: §Y[ps_cell.GetName]§!.{B}{B}System transfers, subject overview, the selected subject\'s card, its budget and treaty recommendations."\n',
          ' ps_vm.1.systems:0 "System transfers"\n',
          ' ps_vm.1.overview:0 "Subject overview"\n',
          ' ps_vm.1.card:0 "Subject card"\n',
          ' ps_vm.1.budget:0 "Budget and recommendations"\n',
          ' ps_vm.1.next:0 "Next subject"\n',
          ' ps_vm.1.panel:0 "Syndicate cell panel"\n',
          ' ps_vm.back:0 "Back"\n',
          ' ps_vm.close:0 "Close"\n',
          ' ps_vm.10.name:0 "System Transfers"\n',
          f' ps_vm.10.desc:0 "{sys_en}"\n',
          f' ps_vm.10.desc_none:0 "No system selected. Pick one with the buttons below.{B}{B}Receiver on transfer: cell §Y[ps_cell.GetName]§!."\n',
          ' ps_vm.10.next_own:0 "Next system of ours"\n',
          ' ps_vm.10.next_cell:0 "Next system of the selected cell"\n',
          ' ps_vm.10.next_vassal:0 "Next system of any subject"\n',
          ' ps_vm.10.switch_cell:0 "Change receiver (next cell)"\n',
          ' ps_vm.10.give:0 "Give the system to §Y[ps_cell.GetName]§!"\n',
          ' ps_vm.10.give.tooltip:0 "The owner\'s colonies and outpost pass to the cell. If another subject owns the system, it is a seizure: §R−10§! loyalty for it."\n',
          ' ps_vm.10.take:0 "Take the system"\n',
          ' ps_vm.10.take.tooltip:0 "The subject\'s colonies and outpost pass to us. Subject loyalty §R−10§!."\n',
          ' ps_vm.11.name:0 "New Lands"\n',
          ' ps_vm.11.desc:0 "Our overlord has granted us the §Y[ps_sys.GetName]§! system."\n',
          ' ps_vm.11.a:0 "Accept"\n',
          ' ps_vm_no_influence:0 "Not enough influence (25 + 50 per colony)."\n',
          ' ps_vm_fail_peace:0 "Requires peace: neither we, the owner nor the receiver may be at war."\n',
          ' ps_vm_fail_same:0 "The system already belongs to the receiver."\n',
          ' ps_vm_fail_outpost:0 "The owner must control the system\'s outpost."\n',
          ' ps_vm_fail_colonies:0 "The owner must control all its colonies in the system."\n',
          ' ps_vm_fail_capital:0 "A capital system cannot be transferred."\n',
          ' ps_vm_fail_last:0 "This is the owner\'s last system."\n',
          ' ps_vm_fail_combat:0 "Ground combat is under way in the system."\n',
          ' ps_vm_fail_colonizing:0 "A colony is being founded in the system."\n',
          ' ps_vm_fail_foreign:0 "The system contains regular planets of third parties."\n',
          ' ps_vm_fail_cooldown:0 "This system was already transferred in the last 5 years."\n',
          ' ps_vm.20.name:0 "Subject Overview"\n',
          f' ps_vm.20.desc:0 "Leaders and laggards among subjects, value in brackets; our own value at the end of each line.{B}{B}{rank("en")}"\n',
          ' ps_vm.30.name:0 "Subject Card"\n',
          f' ps_vm.30.desc:0 "{card_en}"\n',
          ' ps_vm.30.econ:0 "Economic support: §Y1000§! energy and §Y250§! alloys"\n',
          ' ps_vm.30.admin:0 "Administrative support: §Y100§! influence and §Y500§! unity"\n',
          ' ps_vm_support_cd:0 "This cell already received this support in the last 5 years."\n',
          ' ps_vm_econ_support:0 "Overlord Economic Support"\n',
          ' ps_vm_econ_support_desc:0 "The overlord invests in our economy."\n',
          ' ps_vm_admin_support:0 "Overlord Administrative Support"\n',
          ' ps_vm_admin_support_desc:0 "The overlord\'s advisers help us govern our worlds."\n',
          ' ps_vm.31.name:0 "Budget and Recommendations: [ps_cell.GetName]"\n',
          f' ps_vm.31.desc:0 "{budget_en}{rec_en}"\n',
          ' ps_vm_none:0 "none"\n',
          ' ps_vm_neutral:0 "neutral"\n',
          ' ps_vm_rec_tax:0 "payments to the overlord can be raised to"\n',
          ' ps_vm_rec_subsidy:0 "needs an overlord subsidy of"\n',
          ' ps_vm_rec_keep:0 "keep as is"\n',
          ' ps_vm_recspec_strike:0 "$specialist_ps_strike$ (strong fleet — at least half of ours)"\n',
          ' ps_vm_recspec_residency:0 "$specialist_ps_residency$ (strong research)"\n',
          ' ps_vm_recspec_trust:0 "$specialist_ps_trust$ (surplus minerals and food)"\n',
          ' ps_vm_recspec_exchange:0 "$specialist_ps_exchange$ (surplus energy)"\n',
          ' ps_vm_recspec_devotee:0 "$specialist_ps_devotee$ (high unity)"\n',
          ' ps_vm_recspec_assault:0 "$specialist_ps_assault$ (no clear strengths — armies)"\n',
          ' ps_vp_cooldown:0 "A new subject project can start no sooner than 2 years after the previous one."\n',
          ] + en_proj
    OUT.append(("localisation/russian/ps_vm_l_russian.yml", "".join(ru)))
    OUT.append(("localisation/english/ps_vm_l_english.yml", "".join(en)))


def main():
    gen_effects()
    gen_triggers()
    gen_scripted_loc()
    ru_p, en_p = gen_decisions_and_modifiers()
    gen_events()
    gen_loc(ru_p, en_p)
    for rel, text in OUT:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print("ok:", len(OUT), "files")


if __name__ == "__main__":
    main()
