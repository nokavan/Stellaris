#!/usr/bin/env python3
"""Генератор модулей кочевых станций-стоянок (waystations) Синдиката — 100 шт.

Создаёт:
  (+ модуль «Отсеки Синдиката»: ускорение постройки модулей и склад; слоты 10/25/50 — в ship_sizes)
  common/starbase_modules/ps_waystation_modules.txt
  interface/ps_waystation_modules.gfx + DDS-иконки (заглушки)
  localisation/{russian,english}/ps_waystation_l_*.yml

Формат сверен с vanilla 4.x:
  starbase_levels/00_documentation.txt
  starbase_modules/00_waystation_modules.txt, starbase_modules/00_example.txt
  ключи локализации: sm_<module>, sm_<module>_plural, sm_<module>_desc (nomads_1_l_russian.yml)

Запуск из корня репозитория:  python3 tools/gen_waystation_modules.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


M = []


def m(key, cat, tier, ru, en, section="SCIENCE_STARBASE_SECTION", cost=100, upkeep=2, produces=None,
      station=None, country=None, orbit=None, ship=None, net_sys=None, net_country=None, collect=None,
      ally=None, enemy=None, own=None, unique=False):
    M.append(dict(key=key, cat=cat, tier=tier, ru=ru, en=en, section=section, cost=cost, upkeep=upkeep,
                  produces=produces or {}, station=station or {}, country=country or {}, orbit=orbit or {},
                  ship=ship or {}, net_sys=net_sys or {}, net_country=net_country or {}, collect=collect or [],
                  ally=ally or {}, enemy=enemy or {}, own=own or {}, unique=unique))


NAV, DEF, ECO, UTL, PIR = "sm_naval_support_cat", "sm_defense_cat", "sm_economy_cat", "sm_utility_cat", "sm_piracy_cat"
SHIPYARD, ANCHOR, REFINERY, HANGAR, BATTERY, MISSILE = (
    "SHIPYARD_STARBASE_SECTION", "ANCHORAGE_STARBASE_SECTION", "REFINERY_STARBASE_SECTION",
    "HANGAR_STARBASE_SECTION", "BATTERY_STARBASE_SECTION", "MISSILE_STARBASE_SECTION")

# ===== A. Флот и рейды =====
m("raider_dock", NAV, 1, ("Док рейдеров", "Причал для быстрых кораблей Синдиката."), ("Raider Dock", "A berth for the Syndicate's fast ships."),
  section=ANCHOR, country={"country_naval_cap_add": 2}, orbit={"ship_repair_hull_mult": 0.10})
m("crew_barracks", NAV, 1, ("Казармы экипажей", "Новые экипажи проходят здесь партизанскую школу."), ("Crew Barracks", "New crews go through the partisan school here."),
  section=ANCHOR, ship={"ship_starting_experience_add": 50})
m("privateer_berth", NAV, 1, ("Каперский причал", "Каперы чинятся и делят добычу."), ("Privateer Berth", "Privateers repair and split the loot."),
  section=ANCHOR, country={"country_naval_cap_add": 3})
m("field_repair_yard", NAV, 1, ("Полевая ремонтная верфь", "Латает борта прямо на стоянке."), ("Field Repair Yard", "Patches hulls right at the waystation."),
  section=SHIPYARD, orbit={"ship_repair_hull_mult": 0.25, "ship_repair_armor_mult": 0.25})
m("munitions_store", NAV, 1, ("Склад боеприпасов", "Снаряды и ракеты под рукой."), ("Munitions Store", "Shells and missiles close at hand."),
  section=MISSILE, station={"ship_fire_rate_mult": 0.10})
m("ambush_beacon", NAV, 2, ("Маяк засады", "Наши корабли знают короткие пути через систему."), ("Ambush Beacon", "Our ships know the shortcuts through this system."),
  own={"ship_speed_mult": 0.10})
m("fleet_hangar", NAV, 2, ("Флотский ангар", "Дополнительные стапели для флота."), ("Fleet Hangar", "Extra slipways for the fleet."),
  section=SHIPYARD, station={"starbase_shipyard_capacity_add": 1, "starbase_shipyard_build_speed_mult": 0.10})
m("shadow_shipyard", NAV, 2, ("Теневая верфь", "Корабли без флагов и номеров."), ("Shadow Shipyard", "Ships without flags or hull numbers."),
  section=SHIPYARD, station={"starbase_shipyard_build_speed_mult": 0.25})
m("flagship_workshop", NAV, 3, ("Мастерская флагманов", "Ветераны готовят экипажи флагманов."), ("Flagship Workshop", "Veterans train flagship crews."),
  section=SHIPYARD, cost=300, ship={"ship_starting_experience_add": 100})
m("convoy_escort", NAV, 2, ("Пост конвоя", "Ремонтные бригады на всей сети стоянок."), ("Convoy Post", "Repair crews across the whole waystation network."),
  section=ANCHOR, net_sys={"ship_repair_hull_mult": 0.05, "ship_repair_armor_mult": 0.05})
m("wolfpack_hq", NAV, 3, ("Штаб волчьих стай", "Координирует рейды каперов."), ("Wolfpack HQ", "Coordinates privateer raids."),
  section=HANGAR, cost=300, upkeep=4, country={"country_naval_cap_add": 5}, station={"ship_fire_rate_mult": 0.05})
m("sensor_picket", NAV, 1, ("Сенсорный пикет", "Видит врага издалека."), ("Sensor Picket", "Sees the enemy from afar."),
  station={"ship_sensor_range_add": 3, "ship_cloaking_detection_add": 1})

# ===== B. Оборона станции =====
m("armor_plating", DEF, 1, ("Бронеплиты", "Дополнительная броня станции."), ("Armor Plating", "Extra station armor."),
  section=BATTERY, station={"ship_armor_mult": 0.25})
m("hull_bracing", DEF, 1, ("Усиление корпуса", "Распорки и рёбра жёсткости."), ("Hull Bracing", "Struts and stiffening ribs."),
  section=BATTERY, station={"ship_hull_mult": 0.25})
m("shield_capacitors", DEF, 1, ("Щитовые конденсаторы", "Запасают энергию для щитов."), ("Shield Capacitors", "Store energy for the shields."),
  section=BATTERY, station={"ship_shield_mult": 0.25})
m("hardened_bulkheads", DEF, 2, ("Укреплённые переборки", "Снижают пробой брони и щитов."), ("Hardened Bulkheads", "Reduce armor and shield penetration."),
  section=BATTERY, station={"ship_shield_hardening_add": 0.10})
m("point_defense_grid", DEF, 1, ("Сеть точечной обороны", "Сбивает ракеты и истребители."), ("Point Defense Grid", "Shoots down missiles and fighters."),
  section=BATTERY, station={"ship_tracking_add": 10})
m("long_range_guns", DEF, 2, ("Дальнобойные орудия", "Бьют дальше, чем ждёт враг."), ("Long-Range Guns", "Reach further than the enemy expects."),
  section=BATTERY, station={"ship_weapon_range_mult": 0.15})
m("platform_dock", DEF, 1, ("Причал платформ", "Место для оборонительных платформ."), ("Platform Dock", "Room for defense platforms."),
  section=BATTERY, station={"starbase_defense_platform_capacity_add": 2})
m("heavy_platform_dock", DEF, 2, ("Тяжёлый причал платформ", "Больше оборонительных платформ."), ("Heavy Platform Dock", "More defense platforms."),
  section=BATTERY, cost=200, station={"starbase_defense_platform_capacity_add": 4})
m("damage_dampers", DEF, 2, ("Демпферы урона", "Гасят ударные волны."), ("Damage Dampers", "Absorb shockwaves."),
  section=BATTERY, station={"ship_damage_reduction_mult": 0.15})
m("partisan_garrison", DEF, 2, ("Партизанский гарнизон", "Станцию держат те, кто умеет держать."), ("Partisan Garrison", "Held by those who know how to hold."),
  section=BATTERY, station={"ship_fire_rate_mult": 0.10, "ship_hull_mult": 0.10})
m("fortress_core", DEF, 3, ("Ядро крепости", "Станция превращается в цитадель."), ("Fortress Core", "Turns the station into a citadel."),
  section=BATTERY, cost=500, upkeep=4, station={"ship_hull_mult": 0.50, "ship_armor_mult": 0.50, "ship_shield_mult": 0.50})

# ===== C. Сбор ресурсов =====
for key, res, ru, en in [
    ("energy_tap", "energy", "Энергоотвод", "Energy Tap"),
    ("mineral_scoop", "minerals", "Рудный ковш", "Mineral Scoop"),
    ("food_trawler", "food", "Пищевой траулер", "Food Trawler"),
    ("trade_relay", "trade", "Торговый ретранслятор", "Trade Relay"),
    ("physics_siphon", "physics_research", "Физический сифон", "Physics Siphon"),
    ("society_siphon", "society_research", "Социологический сифон", "Society Siphon"),
    ("engineering_siphon", "engineering_research", "Инженерный сифон", "Engineering Siphon"),
    ("unity_beacon", "unity", "Маяк единства", "Unity Beacon"),
]:
    m(key, ECO, 1, (ru, "Собирает ресурс системы в запас станции."), (en, "Collects this system's resource into the station stockpile."),
      section=REFINERY, collect=[res], station={f"starbase_collected_system_{res}_add": 3})
for key, res, ru, en in [
    ("gas_harvester", "exotic_gases", "Сборщик газов", "Gas Harvester"),
    ("crystal_harvester", "rare_crystals", "Сборщик кристаллов", "Crystal Harvester"),
    ("mote_harvester", "volatile_motes", "Сборщик мотов", "Mote Harvester"),
]:
    m(key, ECO, 2, (ru, "Собирает редкий ресурс системы."), (en, "Collects this system's rare resource."),
      section=REFINERY, cost=150, collect=[res])
m("resource_hub", ECO, 2, ("Ресурсный узел", "Ускоряет сбор всех ресурсов станции."), ("Resource Hub", "Speeds up all of the station's collection."),
  section=REFINERY, cost=200, station={"starbase_collected_system_resources_mult": 0.15})
m("big_silo", ECO, 1, ("Большой силос", "Огромное хранилище запасов."), ("Big Silo", "A huge stockpile store."),
  section=REFINERY, station={"starbase_stockpile_capacity_add": 2000})
m("collection_crews", ECO, 2, ("Бригады вывоза", "Корабли быстрее забирают запасы станции."), ("Collection Crews", "Ships pick up the station's stockpile faster."),
  section=ANCHOR, station={"ship_starbase_stockpile_collection_rate_mult": 0.25})

# ===== D. Деньги =====
for key, tier, prod, ru, en in [
    ("smuggler_exchange", 1, {"trade": 3}, ("Биржа контрабандистов", "Всё запрещённое по сходной цене."), ("Smugglers' Exchange", "Everything forbidden at fair prices.")),
    ("black_bank", 1, {"energy": 4}, ("Чёрный банк", "Хавала по-галактически."), ("Black Bank", "Hawala, galactic style.")),
    ("casino_ring", 1, {"energy": 3, "unity": 1}, ("Кольцо казино", "Дом всегда выигрывает."), ("Casino Ring", "The house always wins.")),
    ("loan_office", 1, {"energy": 3}, ("Контора ростовщика", "Деньги сразу, проценты потом."), ("Loan Office", "Cash now, interest later.")),
    ("insurance_office", 1, {"energy": 3}, ("Страховая «Крыша»", "Застрахуйтесь, пока не поздно."), ("«Protection» Insurance", "Insure yourself before it's too late.")),
    ("contraband_vault", 2, {"trade": 2, "energy": 2}, ("Хранилище контрабанды", "Склад того, чего нет в декларациях."), ("Contraband Vault", "Storage for what's not in the manifests.")),
    ("commodity_futures", 2, {"trade": 4}, ("Товарные фьючерсы", "Торговля тем, чего ещё нет."), ("Commodity Futures", "Trading in what doesn't exist yet.")),
    ("tax_haven", 2, {"energy": 5}, ("Налоговая гавань", "Тысяча компаний по одному адресу."), ("Tax Haven", "A thousand companies at one address.")),
    ("currency_mint", 3, {"energy": 6}, ("Монетный двор Синдиката", "Печатает собственную валюту сети."), ("Syndicate Mint", "Prints the network's own currency.")),
    ("offshore_node", 3, {"energy": 4, "influence": 1}, ("Офшорный узел", "Деньги и связи в одном месте."), ("Offshore Node", "Money and connections in one place.")),
]:
    m(key, ECO, tier, ru, en, section=REFINERY, cost=100 * tier + 50, upkeep=1 + tier, produces=prod)

# ===== E. Наука =====
m("stolen_data_core", ECO, 1, ("Ядро краденых данных", "Чужие исследования — наши разработки."), ("Stolen Data Core", "Their research, our development."),
  country={"country_physics_research_produces_mult": 0.01})
m("xeno_lab", ECO, 1, ("Ксенолаборатория", "Изучает местную жизнь и культуры."), ("Xeno Lab", "Studies local life and cultures."),
  collect=["society_research"], station={"starbase_collected_system_society_research_add": 5})
m("engineering_testbed", ECO, 1, ("Испытательный стенд", "Прототипы испытываются в пустоте."), ("Engineering Testbed", "Prototypes tested in the void."),
  collect=["engineering_research"], station={"starbase_collected_system_engineering_research_add": 5})
m("physics_array", ECO, 1, ("Физический массив", "Слушает излучение звезды."), ("Physics Array", "Listens to the star's radiation."),
  collect=["physics_research"], station={"starbase_collected_system_physics_research_add": 5})
m("archive_node", UTL, 2, ("Узел архива", "Редкие технологии со всей сети."), ("Archive Node", "Rare technologies from across the network."),
  net_country={"rare_tech_research_speed_mult": 0.05})
m("research_exchange", UTL, 2, ("Научный обмен", "Делимся знаниями по сети стоянок."), ("Research Exchange", "Knowledge shared across the waystation network."),
  net_country={"research_sharing_mult": 0.05})
m("survey_beacon", UTL, 1, ("Маяк разведки", "Ускоряет исследование систем."), ("Survey Beacon", "Speeds up system surveys."),
  station={"science_ship_survey_speed": 0.20})
m("deep_scanner", UTL, 2, ("Глубокий сканер", "Дальнобойные сенсоры."), ("Deep Scanner", "Long-range sensors."),
  station={"ship_sensor_range_add": 5})

# ===== F. Шпионаж =====
m("listening_array", UTL, 1, ("Массив прослушки", "Перехватывает чужие переговоры."), ("Listening Array", "Intercepts foreign communications."),
  country={"spy_network_levels_add": 2})
m("cipher_vault", UTL, 2, ("Шифровальное хранилище", "Квантовые ключи Синдиката."), ("Cipher Vault", "The Syndicate's quantum keys."),
  country={"intel_encryption_add": 1}, unique=True)
m("decrypt_array", UTL, 2, ("Дешифровальный массив", "Взламывает чужие коды."), ("Decryption Array", "Cracks foreign codes."),
  country={"intel_decryption_add": 1}, unique=True)
m("agent_dropoff", UTL, 1, ("Точка высадки агентов", "Отсюда агенты уходят на задания."), ("Agent Drop-off", "Agents depart on missions from here."),
  country={"spy_network_levels_add": 3})
m("counter_surveillance", UTL, 1, ("Контрнаблюдение", "Находит замаскированных наблюдателей."), ("Counter-Surveillance", "Finds cloaked watchers."),
  station={"ship_cloaking_detection_add": 2})
m("informant_relay", UTL, 2, ("Ретранслятор осведомителей", "Сеть растёт быстрее."), ("Informant Relay", "The network grows faster."),
  country={"spy_network_daily_value_mult": 0.02})
m("envoy_lounge", UTL, 2, ("Салон посланников", "Здесь договариваются неофициально."), ("Envoy Lounge", "Where unofficial deals are made."),
  country={"envoys_add": 1}, unique=True)
m("sabotage_cache", UTL, 1, ("Тайник диверсантов", "Взрывчатка и поддельные пропуска."), ("Saboteur Cache", "Explosives and forged passes."),
  country={"spy_network_levels_add": 2}, produces={"energy": 1})
m("dossier_bank", UTL, 3, ("Банк досье", "Компромат на всех, кто что-то значит."), ("Dossier Bank", "Dirt on everyone who matters."),
  cost=300, country={"spy_network_levels_add": 4})
m("ghost_relay", UTL, 3, ("Призрачный ретранслятор", "Сеть растёт незаметно и быстро."), ("Ghost Relay", "The network grows quietly and quickly."),
  cost=300, country={"spy_network_daily_value_mult": 0.03})

# ===== G. Единство и пропаганда =====
m("pirate_broadcast", UTL, 1, ("Пиратское вещание", "Песни Сопротивления на всех частотах."), ("Pirate Broadcast", "Resistance songs on every frequency."),
  produces={"unity": 2})
m("memorial_beacon", UTL, 1, ("Маяк памяти", "Имена павших транслируются в эфир."), ("Memorial Beacon", "Broadcasts the names of the fallen."),
  produces={"unity": 3})
m("agitprop_relay", UTL, 2, ("Агитационный ретранслятор", "Подтачивает доверие к местной власти."), ("Agitprop Relay", "Erodes trust in the local government."),
  produces={"unity": 1}, enemy={"pop_government_ethic_attraction": -0.15})
m("tradition_archive", UTL, 2, ("Архив традиций", "Удешевляет традиции по всей сети."), ("Tradition Archive", "Cheaper traditions across the network."),
  net_country={"tradition_cost_mult": -0.02})
m("leaders_club", UTL, 2, ("Клуб командиров", "Лидеров проще нанять через сеть."), ("Commanders' Club", "Leaders are easier to hire through the network."),
  net_country={"leaders_cost_mult": -0.05})
m("code_shrine", UTL, 3, ("Святилище Кодекса", "Здесь хранится копия первого Кодекса."), ("Shrine of the Code", "Keeps a copy of the first Code."),
  cost=300, produces={"unity": 4})
m("resistance_radio", UTL, 1, ("Радио Сопротивления", "Ободряет наших граждан в системе."), ("Resistance Radio", "Cheers on our citizens in the system."),
  produces={"unity": 2}, own={"planet_stability_add": 2})
m("diaspora_center", UTL, 2, ("Центр диаспоры", "Лидеры набираются опыта быстрее."), ("Diaspora Center", "Leaders gain experience faster."),
  country={"species_leader_exp_gain": 0.05})

# ===== H. Помощь союзникам (действует, если система принадлежит союзнику) =====
m("ally_repair_dock", NAV, 1, ("Союзный ремонтный док", "Чинит любые дружественные корабли на орбите."), ("Allied Repair Dock", "Repairs any friendly ships in orbit."),
  section=SHIPYARD, orbit={"ship_repair_hull_mult": 0.25, "ship_repair_armor_mult": 0.25})
m("ally_supply_depot", NAV, 1, ("Склад снабжения союзников", "Топливо и запчасти для союзных флотов."), ("Allied Supply Depot", "Fuel and spares for allied fleets."),
  section=ANCHOR, ally={"ship_speed_mult": 0.10})
m("ally_relief_station", UTL, 1, ("Станция помощи", "Гуманитарная помощь союзным колониям."), ("Relief Station", "Humanitarian aid for allied colonies."),
  ally={"planet_stability_add": 5})
m("ally_trade_post", ECO, 1, ("Союзная фактория", "Торговля поднимает экономику союзника."), ("Allied Trading Post", "Trade lifts the ally's economy."),
  section=REFINERY, produces={"trade": 1}, ally={"station_gatherers_produces_mult": 0.10})
m("ally_research_support", UTL, 2, ("Научная поддержка", "Помогаем учёным союзника."), ("Research Support", "Helping the ally's scientists."),
  ally={"station_researchers_produces_mult": 0.15})
for key, res, ru, en in [
    ("ally_food_aid", "food", "Продовольственная помощь", "Food Aid"),
    ("ally_energy_aid", "energy", "Энергетическая помощь", "Energy Aid"),
    ("ally_mining_aid", "minerals", "Горная помощь", "Mining Aid"),
    ("ally_alloy_aid", "alloys", "Помощь сплавами", "Alloy Aid"),
    ("ally_goods_aid", "consumer_goods", "Помощь товарами", "Goods Aid"),
]:
    m(key, ECO, 2, (ru, "Поднимает добычу союзника в системе."), (en, "Boosts the ally's output in this system."),
      section=REFINERY, ally={f"station_gatherers_{res}_produces_mult": 0.20})
m("ally_strategic_aid", ECO, 3, ("Помощь редкими ресурсами", "Поднимает добычу редких ресурсов союзника."), ("Strategic Aid", "Boosts the ally's rare resource output."),
  section=REFINERY, cost=300, ally={"station_gatherers_exotic_gases_produces_mult": 0.15, "station_gatherers_rare_crystals_produces_mult": 0.15,
                                     "station_gatherers_volatile_motes_produces_mult": 0.15})
m("ally_refugee_ship", UTL, 2, ("Корабль беженцев", "Вывозит безработных и успокаивает колонии."), ("Refugee Ship", "Relocates the unemployed and calms colonies."),
  ally={"planet_resettlement_unemployed_mult": 0.25, "planet_stability_add": 2})
m("ally_shield_net", DEF, 2, ("Щитовая сеть союзников", "Прикрывает союзное пространство."), ("Allied Shield Net", "Covers allied space."),
  section=BATTERY, station={"ship_shield_mult": 0.25}, ally={"ship_speed_mult": 0.05})
m("ally_training_school", NAV, 2, ("Школа союзных экипажей", "Обучаем экипажи и ополчение союзника."), ("Allied Crew School", "Training the ally's crews and militia."),
  section=ANCHOR, ship={"ship_starting_experience_add": 50}, ally={"planet_stability_add": 2})
m("ally_network_pact", UTL, 2, ("Торговый пакт сети", "Торговые договоры приносят больше."), ("Network Trade Pact", "Commercial pacts yield more."),
  net_country={"commercial_pact_mult": 0.10})
m("ally_research_pact", UTL, 2, ("Научный пакт сети", "Союзники делятся знаниями охотнее."), ("Network Research Pact", "Allies share knowledge more readily."),
  net_country={"research_sharing_mult": 0.10})
m("ally_embassy_ship", UTL, 2, ("Корабль-посольство", "Плавучее посольство Синдиката."), ("Embassy Ship", "The Syndicate's floating embassy."),
  country={"envoys_add": 1}, ally={"planet_stability_add": 3}, unique=True)
m("ally_war_relief", NAV, 3, ("Военная помощь союзнику", "Ремонт, снабжение и порядок для союзника в войне."), ("War Relief", "Repairs, supplies and order for an ally at war."),
  section=SHIPYARD, cost=400, upkeep=4, orbit={"ship_repair_hull_mult": 0.15},
  ally={"planet_stability_add": 5, "station_gatherers_produces_mult": 0.10})
m("ally_convoy_hub", NAV, 2, ("Узел союзных конвоев", "Союзные конвои ходят быстрее и чинятся по пути."), ("Allied Convoy Hub", "Allied convoys travel faster and repair en route."),
  section=ANCHOR, orbit={"ship_repair_hull_mult": 0.10}, ally={"ship_speed_mult": 0.10})

# ===== I. Подрыв (действует, если система принадлежит сопернику/врагу) =====
m("sub_jammer", PIR, 1, ("Глушилка", "Срывает добычу в чужой системе."), ("Jammer", "Disrupts extraction in a hostile system."),
  enemy={"station_gatherers_produces_mult": -0.15})
m("sub_agitators", PIR, 1, ("Агитаторы", "Поднимают недовольство в чужих колониях."), ("Agitators", "Stir up unrest in hostile colonies."),
  enemy={"planet_stability_add": -5})
m("sub_lab_raid", PIR, 2, ("Налёт на лаборатории", "Сбивает работу чужих учёных."), ("Lab Raid", "Disrupts hostile scientists."),
  enemy={"station_researchers_produces_mult": -0.20})
m("sub_food_blockade", PIR, 2, ("Продовольственная блокада", "Перехватывает чужие поставки еды."), ("Food Blockade", "Intercepts hostile food shipments."),
  enemy={"station_gatherers_food_produces_mult": -0.25})
m("sub_energy_drain", PIR, 2, ("Энергетический отсос", "Воруем энергию из чужих сетей."), ("Energy Drain", "Stealing energy from hostile grids."),
  produces={"energy": 2}, enemy={"station_gatherers_energy_produces_mult": -0.25})
m("sub_mineral_theft", PIR, 2, ("Кража руды", "Чужая руда уходит в наши трюмы."), ("Ore Theft", "Their ore ends up in our holds."),
  produces={"minerals": 2}, enemy={"station_gatherers_minerals_produces_mult": -0.25})
m("sub_ethic_subversion", PIR, 2, ("Идеологическая диверсия", "Граждане врага сомневаются в своей власти."), ("Ideological Subversion", "Enemy citizens doubt their rulers."),
  enemy={"pop_government_ethic_attraction": -0.25})
m("sub_blockade_fleet", PIR, 3, ("Блокадная флотилия", "Перекрывает пути врагу в системе."), ("Blockade Flotilla", "Blocks the enemy's routes in this system."),
  section=MISSILE, cost=400, upkeep=4, enemy={"ship_speed_mult": -0.15, "planet_stability_add": -3})

assert len(M) == 100, len(M)
assert len({x["key"] for x in M}) == 100

TECH = {1: None, 2: "tech_ps_guerrilla_doctrine", 3: "tech_ps_ghost_networks"}
DAYS = {1: 180, 2: 270, 3: 360}

ALLY_TRIGGER = """exists = owner
			space_owner? = {
				NOT = { is_same_value = root.owner }
				OR = {
					is_in_federation_with = root.owner
					has_defensive_pact = root.owner
					is_friendly_to = root.owner
					is_overlord_to = root.owner
					AND = {
						is_subject = yes
						overlord = { is_same_value = root.owner }
					}
				}
			}"""
ENEMY_TRIGGER = """exists = owner
			space_owner? = {
				NOT = { is_same_value = root.owner }
				OR = {
					is_rival = root.owner
					is_at_war_with = root.owner
					opinion_level = {
						who = root.owner
						level <= poor
					}
				}
			}"""
OWN_TRIGGER = """exists = owner
			space_owner? = { is_same_value = root.owner }"""


def g(v):
    return f"{v:g}"


def blk(name, d, ind=1, extra=""):
    if not d:
        return ""
    t = "\t" * ind
    return f"\n{t}{name} = {{\n{extra}" + "".join(f"{t}\t{k} = {g(v)}\n" for k, v in d.items()) + f"{t}}}\n"


def module(x):
    k = f"waystation_ps_{x['key']}"
    o = [f'{k} = {{\n\ticon = "GFX_{k}"\n\tsection = "{x["section"]}"\n\tconstruction_days = {DAYS[x["tier"]]}\n'
         f'\tstarbase_type = waystation\n\tcategory = {x["cat"]}\n']
    o.append("\n\tempire_limit = {\n\t\tbase = 1\n\t}\n" if x["unique"] else "\n\tstarbase_limit = {\n\t\tbase = 1\n\t}\n")
    tech = f"\n\t\t\thas_technology = {TECH[x['tier']]}" if TECH[x["tier"]] else ""
    o.append(f"\n\tpotential = {{\n\t\tis_waystation_starbase = yes\n\t\towner? = {{\n\t\t\tps_is_partisan_empire = yes{tech}\n\t\t}}\n\t}}\n")
    if TECH[x["tier"]]:
        o.append(f'\n\tshow_in_tech = "{TECH[x["tier"]]}"\n\tshow_tech_unlock_if = {{\n\t\tps_is_partisan_empire = yes\n\t\tis_nomadic = yes\n\t}}\n')
    res = f"\n\tresources = {{\n\t\tcategory = starbase_waystations_modules\n\t\tcost = {{\n\t\t\talloys = {x['cost']}\n\t\t}}\n\t\tupkeep = {{\n\t\t\ttrade = {x['upkeep']}\n\t\t}}\n"
    if x["produces"]:
        res += "\t\tproduces = {\n" + "".join(f"\t\t\t{r} = {g(v)}\n" for r, v in x["produces"].items()) + "\t\t}\n"
    o.append(res + "\t}\n")
    if x["collect"]:
        o.append("\n\tcollected_system_resources = {\n" + "".join(f"\t\t{r} = {{\n\t\t\talways = yes\n\t\t}}\n" for r in x["collect"]) + "\t}\n")
    o.append(blk("station_modifier", x["station"]))
    o.append(blk("country_modifier", x["country"]))
    o.append(blk("orbit_modifier", x["orbit"]))
    o.append(blk("ship_modifier", x["ship"]))
    o.append(blk("waystation_network_system_modifier", x["net_sys"]))
    o.append(blk("waystation_network_country_modifier", x["net_country"]))
    for d, trig, tt in ((x["ally"], ALLY_TRIGGER, "ps_waystation_ally_tt"), (x["enemy"], ENEMY_TRIGGER, "ps_waystation_enemy_tt"),
                        (x["own"], OWN_TRIGGER, "ps_waystation_own_tt")):
        if d:
            o.append(f"\n\ttriggered_system_modifier = {{\n\t\tpotential = {{\n\t\t\t{trig}\n\t\t}}\n\t\tcustom_tooltip = {tt}\n"
                     f"\t\tshow_only_custom_tooltip = no\n" + "".join(f"\t\t{kk} = {g(v)}\n" for kk, v in d.items()) + "\t}\n")
    o.append("\n\tai_weight = {\n\t\tweight = 100\n\t}\n}\n")
    return "".join(o)


THEME = {NAV: "star", DEF: "crown", ECO: "press", UTL: "eye", PIR: "net"}


# Особый модуль «Отсеки Синдиката». Раньше давал слоты через triggered_station_modifier, но такие
# модификаторы игра пересчитывает раз в несколько месяцев, и слоты «не появлялись». Теперь вместимость
# 10 / 25 / 50 задана прямо в ship_sizes/00_waystations.txt (как в More Waystation Slots), а модуль
# ускоряет постройку модулей и расширяет склад.
def capacity_module():
    trig = ("\n\tstation_modifier = {\n\t\tstarbase_module_build_speed_mult = 0.5\n"
            "\t\tstarbase_stockpile_capacity_add = 1000\n\t}\n")
    return f"""
waystation_ps_cell_bays = {{
	icon = "GFX_waystation_ps_cell_bays"
	section = "ANCHORAGE_STARBASE_SECTION"
	construction_days = 120
	starbase_type = waystation
	category = sm_utility_cat

	starbase_limit = {{
		base = 1
	}}

	potential = {{
		is_waystation_starbase = yes
		owner? = {{ ps_is_partisan_empire = yes }}
	}}

	resources = {{
		category = starbase_waystations_modules
		cost = {{
			alloys = 200
		}}
		upkeep = {{
			trade = 2
		}}
	}}
{trig}
	ai_weight = {{
		weight = 1000
	}}
}}
"""


# Подписи условных эффектов: игра не показывает цифры triggered_system_modifier в подсказке,
# поэтому они вписываются в описание модуля.
FX_NAMES = {
    "planet_resettlement_unemployed_mult": ("Переселение безработных", "Unemployed resettlement"),
    "planet_stability_add": ("Стабильность планет", "Planet stability"),
    "pop_government_ethic_attraction": ("Привлекательность этики правительства", "Government ethic attraction"),
    "ship_speed_mult": ("Скорость кораблей", "Ship speed"),
    "station_gatherers_produces_mult": ("Добыча станций", "Station output"),
    "station_gatherers_energy_produces_mult": ("Добыча энергии станциями", "Station energy output"),
    "station_gatherers_minerals_produces_mult": ("Добыча минералов станциями", "Station mineral output"),
    "station_gatherers_food_produces_mult": ("Добыча еды станциями", "Station food output"),
    "station_gatherers_exotic_gases_produces_mult": ("Добыча экзотических газов", "Exotic gas output"),
    "station_gatherers_rare_crystals_produces_mult": ("Добыча редких кристаллов", "Rare crystal output"),
    "station_gatherers_volatile_motes_produces_mult": ("Добыча летучих частиц", "Volatile mote output"),
    "station_researchers_produces_mult": ("Исследования станций", "Station research"),
}


def fx_lines(d, ru):
    out = []
    for k, v in d.items():
        name = FX_NAMES.get(k, (k, k))[0 if ru else 1]
        if k.endswith("_mult") or k == "pop_government_ethic_attraction":
            val = f"{v * 100:+g}%"
        else:
            val = f"{v:+g}"
        col = "G" if v > 0 else "R"
        out.append(f"\\n  {name}: §{col}{val}§!")
    return "".join(out)


def main():
    (ROOT / "common/starbase_modules").mkdir(parents=True, exist_ok=True)
    hdr = "# АВТОГЕНЕРАЦИЯ: tools/gen_waystation_modules.py — правьте генератор, а не этот файл\n# 100 модулей станций-стоянок Синдиката\n\n"
    (ROOT / "common/starbase_modules/ps_waystation_modules.txt").write_text(hdr + capacity_module() + "\n".join(module(x) for x in M), encoding="utf-8")

    gfx = ["spriteTypes = {",
           '\tspriteType = {\n\t\tname = "GFX_waystation_ps_cell_bays"\n\t\ttexturefile = "gfx/interface/icons/waystation/ps_cell_bays.dds"\n\t}'] + [
        f'\tspriteType = {{\n\t\tname = "GFX_waystation_ps_{x["key"]}"\n\t\ttexturefile = "gfx/interface/icons/waystation/ps_{x["key"]}.dds"\n\t}}'
        for x in M] + ["}\n"]
    (ROOT / "interface/ps_waystation_modules.gfx").write_text("\n".join(gfx), encoding="utf-8")

    for lang in ("russian", "english"):
        ru = lang == "russian"
        L = [f"l_{lang}:"]
        bay_n, bay_d = (("Отсеки Синдиката", "Монтажные отсеки Синдиката: модули стоянки строятся на §G50%§! быстрее, склад станции §G+1000§!.") if ru else
                        ("Syndicate Bays", "Syndicate assembly bays: station modules build §G50%§! faster, station stockpile §G+1000§!."))
        L += [f' sm_waystation_ps_cell_bays:0 "{bay_n}"', f' sm_waystation_ps_cell_bays_plural:0 "{bay_n}"', f' sm_waystation_ps_cell_bays_desc:0 "{bay_d}"']
        for x in M:
            k = f"sm_waystation_ps_{x['key']}"
            name, desc = x["ru"] if ru else x["en"]
            if x["ally"]:
                desc += "\\n\\n§Y" + ("Если система принадлежит союзнику (вассалу, сюзерену, члену федерации, партнёру по оборонному пакту или дружественной империи):" if ru else
                                     "If the system belongs to an ally (subject, overlord, federation member, defensive pact partner or friendly empire):") + "§!" + fx_lines(x["ally"], ru)
            if x["enemy"]:
                desc += "\\n\\n§R" + ("Если система принадлежит сопернику, врагу или недружественной империи:" if ru else
                                     "If the system belongs to a rival, enemy or unfriendly empire:") + "§!" + fx_lines(x["enemy"], ru)
            if x["own"]:
                desc += "\\n\\n§G" + ("Если система наша:" if ru else "If the system is ours:") + "§!" + fx_lines(x["own"], ru)
            L += [f' {k}:0 "{name}"', f' {k}_plural:0 "{name}"', f' {k}_desc:0 "{desc}"']
        if ru:
            L += [' ps_waystation_ally_tt:0 "§YЕсли система принадлежит союзнику:§!"',
                  ' ps_waystation_enemy_tt:0 "§RЕсли система принадлежит сопернику или врагу:§!"',
                  ' ps_waystation_own_tt:0 "§GЕсли система наша:§!"']
        else:
            L += [' ps_waystation_ally_tt:0 "§YIf the system belongs to an ally:§!"',
                  ' ps_waystation_enemy_tt:0 "§RIf the system belongs to a rival or enemy:§!"',
                  ' ps_waystation_own_tt:0 "§GIf the system is ours:§!"']
        (ROOT / f"localisation/{lang}/ps_waystation_l_{lang}.yml").write_bytes(b"\xef\xbb\xbf" + ("\n".join(L) + "\n").encode())

    try:
        from build_assets import icon, save_dds
        from PIL import ImageDraw
    except ImportError:
        print("Pillow не найден — иконки не созданы")
        return
    tier_c = {1: (120, 200, 120, 255), 2: (220, 180, 60, 255), 3: (220, 60, 60, 255)}
    for x in M:
        img = icon(THEME[x["cat"]], 64)
        d = ImageDraw.Draw(img)
        for j in range(x["tier"]):
            d.ellipse([8 + j * 10, 50, 15 + j * 10, 57], fill=tier_c[x["tier"]])
        if x["ally"]:
            d.rectangle([48, 6, 58, 16], fill=(60, 160, 220, 255))
        if x["enemy"]:
            d.rectangle([48, 6, 58, 16], fill=(200, 30, 30, 255))
        save_dds(img, f"gfx/interface/icons/waystation/ps_{x['key']}.dds")
    save_dds(icon("crown", 64), "gfx/interface/icons/waystation/ps_cell_bays.dds")
    from collections import Counter
    print("ok:", len(M), "modules;", dict(Counter(x["cat"] for x in M)))


if __name__ == "__main__":
    main()
