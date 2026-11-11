#!/usr/bin/env python3
"""Генератор зданий филиалов Синдиката Сопротивления (100 шт.).

Каждая строка таблицы BUILDINGS — одно здание. Скрипт создаёт:
  common/buildings/ps_branch_offices.txt
  interface/ps_buildings.gfx + DDS-иконки (заглушки)
  localisation/{russian,english}/ps_buildings_l_*.yml

Формат сверен с vanilla 4.x common/buildings/14_branch_office_buildings.txt:
  triggered_country_modifier -> ВЛАДЕЛЬЦУ филиала (owner), масштабируется ценностью филиала
  triggered_planet_modifier  -> планете-хозяину (host)
  inline_script jobs/*_add   -> должности на планете-хозяине

Запуск из корня репозитория:  python3 tools/gen_branch_buildings.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# ---- короткие имена модификаторов -----------------------------------------
# Ресурсы владельцу (за месяц, умножаются на ценность филиала)
E, M, F, A, U, I = (f"country_base_{r}_produces_add" for r in ("energy", "minerals", "food", "alloys", "unity", "influence"))
CG, RC, EG, VM = (f"country_base_{r}_produces_add" for r in ("consumer_goods", "rare_crystals", "exotic_gases", "volatile_motes"))
SPY = "spy_network_levels_add"
NAVAL = "country_naval_cap_add"
# Модификаторы, которые НЕ масштабируются ценностью филиала (проценты, лимиты)
STATIC = {
    "army_damage_mult", "army_starting_experience_add", "spy_network_daily_value_mult",
    "starbase_shipyard_build_speed_mult", "ship_speed_mult", "country_resource_max_add",
    "country_physics_research_produces_mult", "country_society_research_produces_mult",
    "country_engineering_research_produces_mult",
}
PHY, SOC, ENG = ("country_physics_research_produces_mult", "country_society_research_produces_mult",
                 "country_engineering_research_produces_mult")

# requires: None | "ally" | "enemy"
# jobs: [(script, amount)] или [("job_criminal_add", 100)] для прямых job_*_add
# Колонки: key, тема(категория), tier, owner{}, host{}, jobs, requires, ru_name, ru_desc, en_name, en_desc
B = []


def b(key, cat, tier, owner, host=None, jobs=None, req=None, ru=("", ""), en=("", "")):
    B.append(dict(key=key, cat=cat, tier=tier, owner=owner, host=host or {}, jobs=jobs or [], req=req,
                  ru=ru, en=en))


CRIM = [("job_criminal_add", 100)]

# ===== A. Партизанская сеть =====
b("partisan_cell", "army", 1, {SPY: 2, E: 2}, {"planet_crime_add": 15, "planet_stability_add": -2}, CRIM,
  ru=("Партизанская ячейка", "Под вывеской склада — оружейный схрон, явка и радиостанция."),
  en=("Partisan Cell", "Behind a warehouse sign: an arms cache, a safehouse and a radio station."))
b("arms_cache", "army", 1, {A: 1, "army_damage_mult": 0.01}, {"planet_crime_add": 5},
  ru=("Оружейный схрон", "Ящики с оружием под полом заброшенного депо."),
  en=("Arms Cache", "Crates of weapons beneath the floor of an abandoned depot."))
b("safehouse", "army", 1, {SPY: 1, U: 1},
  ru=("Явочная квартира", "Связные отдыхают, меняют документы и уходят дальше."),
  en=("Safehouse", "Couriers rest, swap papers and move on."))
b("forest_camp", "army", 1, {"army_starting_experience_add": 5, U: 1}, {}, CRIM,
  ru=("Лесной лагерь", "Учебный лагерь в глуши, как у предков."),
  en=("Forest Camp", "A training camp in the wilds, just like the ancestors had."))
b("radio_station", "army", 1, {U: 2, SPY: 1},
  ru=("Подпольная радиостанция", "Позывные Сопротивления звучат и на чужих планетах."),
  en=("Underground Radio", "The Resistance's call signs ring out on foreign worlds too."))
b("partisan_hospital", "army", 1, {U: 1}, {"pop_happiness": 0.02},
  ru=("Подпольный госпиталь", "Лечит всех, не спрашивая документов."),
  en=("Underground Hospital", "Treats everyone, no papers asked."))
b("courier_network", "army", 1, {E: 1, I: 0.25},
  ru=("Курьерская сеть", "Пакеты, деньги и приказы — из рук в руки."),
  en=("Courier Network", "Parcels, money and orders, hand to hand."))
b("sabotage_school", "army", 2, {"army_damage_mult": 0.02, SPY: 2}, {}, CRIM,
  ru=("Школа диверсантов", "Здесь учат взрывать мосты и уходить незамеченными."),
  en=("Saboteur School", "Teaches how to blow bridges and slip away unseen."))
b("veterans_club", "army", 2, {U: 2, "army_starting_experience_add": 10},
  ru=("Клуб ветеранов", "Старики рассказывают молодым, как воевали."),
  en=("Veterans' Club", "Old fighters teach the young how it was done."))
b("memorial", "army", 2, {U: 3}, {"pop_happiness": 0.02},
  ru=("Мемориал Сопротивления", "Вечный огонь в честь павших партизан."),
  en=("Resistance Memorial", "An eternal flame for the fallen partisans."))
b("mountain_base", "army", 3, {NAVAL: 3, "army_damage_mult": 0.02},
  ru=("Горная база", "Укрытие в скалах для целого отряда."),
  en=("Mountain Base", "A cliffside shelter for a whole detachment."))
b("partisan_hq", "army", 3, {SPY: 3, U: 3, "army_damage_mult": 0.02}, {"planet_stability_add": -3}, CRIM,
  ru=("Партизанский штаб", "Отсюда координируются все ячейки сектора."),
  en=("Partisan Headquarters", "Coordinates every cell in the sector."))

# ===== B. Шпионаж =====
b("dead_drop", "government", 1, {SPY: 1, E: 1},
  ru=("Тайник-закладка", "Расшатанный кирпич в стене, за ним — микроплёнка."),
  en=("Dead Drop", "A loose brick in the wall, microfilm behind it."))
b("listening_post", "government", 1, {SPY: 2},
  ru=("Пост прослушки", "Антенны на крыше «метеостанции»."),
  en=("Listening Post", "Antennas on the roof of a «weather station»."))
b("honey_trap", "government", 1, {SPY: 2, I: 0.2},
  ru=("Салон «Медовая ловушка»", "Чиновники здесь отдыхают и много говорят."),
  en=("Honey Trap Salon", "Officials relax here and talk too much."))
b("forgery_shop", "government", 1, {SPY: 1, E: 1},
  ru=("Мастерская подделок", "Паспорта, пропуска, накладные — любые."),
  en=("Forgery Workshop", "Passports, permits, manifests, anything."))
b("cipher_bureau", "government", 2, {SPY: 1, "spy_network_daily_value_mult": 0.01},
  ru=("Шифровальное бюро", "Одноразовые блокноты и квантовые ключи."),
  en=("Cipher Bureau", "One-time pads and quantum keys."))
b("informant_network", "government", 2, {SPY: 3},
  ru=("Сеть осведомителей", "Таксисты, официанты, уборщики — все слушают."),
  en=("Informant Network", "Cab drivers, waiters, janitors, all listening."))
b("embassy_cover", "government", 2, {SPY: 2, I: 0.3},
  ru=("Прикрытие при посольстве", "Третий секретарь торгпредства — наш человек."),
  en=("Embassy Cover", "The third trade secretary is one of ours."))
b("data_haven", "government", 2, {SPY: 2, E: 1},
  ru=("Хранилище данных", "Серверы, которые не существуют официально."),
  en=("Data Haven", "Servers that do not officially exist."))
b("sleeper_agents", "government", 2, {SPY: 3}, {"planet_stability_add": -2},
  ru=("Спящие агенты", "Годами живут обычной жизнью и ждут сигнала."),
  en=("Sleeper Agents", "Live ordinary lives for years, waiting for the signal."))
b("counterintel_office", "government", 3, {SPY: 2, "spy_network_daily_value_mult": 0.02},
  ru=("Отдел контрразведки", "Ловит чужих шпионов, пока они ловят наших."),
  en=("Counterintelligence Office", "Catches their spies while they hunt ours."))
b("black_archive", "government", 3, {SPY: 4, U: 2},
  ru=("Чёрный архив", "Досье на каждого, кто что-то значит."),
  en=("Black Archive", "A dossier on everyone who matters."))
b("shadow_consulate", "government", 3, {SPY: 3, I: 0.5},
  ru=("Теневое консульство", "Неофициальная дипломатия Синдиката."),
  en=("Shadow Consulate", "The Syndicate's unofficial diplomacy."))

# ===== C. Экономика и деньги =====
b("front_company", "trade", 1, {E: 3},
  ru=("Фирма-прикрытие", "Легальный бизнес с нелегальными оборотами."),
  en=("Front Company", "A legal business with illegal turnover."))
b("money_laundry", "trade", 1, {E: 2}, {"planet_crime_add": 5}, CRIM,
  ru=("Прачечная", "Отмывает не только бельё."),
  en=("Laundromat", "Washes more than clothes."))
b("pawnshop", "trade", 1, {E: 2, CG: 1},
  ru=("Ломбард", "Принимает всё, вопросов не задаёт."),
  en=("Pawnshop", "Takes anything, asks nothing."))
b("currency_exchange", "trade", 1, {E: 2},
  ru=("Обменник", "Лучший курс в квартале, если знаешь пароль."),
  en=("Currency Exchange", "Best rate on the block, if you know the password."))
b("underground_bank", "trade", 2, {E: 4},
  ru=("Подпольный банк", "Хавала по-галактически."),
  en=("Underground Bank", "Hawala, galactic style."))
b("casino", "trade", 2, {E: 3, U: 1}, {"planet_amenities_add": 2}, [("jobs/entertainers_add", 100)],
  ru=("Казино", "Дом всегда выигрывает. Дом — это мы."),
  en=("Casino", "The house always wins. We are the house."))
b("insurance_racket", "trade", 2, {E: 4}, {"planet_stability_add": -2, "planet_crime_add": 5}, CRIM,
  ru=("Страховая «Крыша»", "Застрахуйтесь от пожара. Пока не поздно."),
  en=("«Protection» Insurance", "Insure against fire. Before it's too late."))
b("loan_sharks", "trade", 2, {E: 3}, {"planet_stability_add": -1},
  ru=("Ростовщики", "Деньги сразу, проценты потом."),
  en=("Loan Sharks", "Cash now, interest later."))
b("smugglers_market", "trade", 2, {E: 2, CG: 2}, {}, CRIM,
  ru=("Рынок контрабандистов", "Всё, что запрещено, по сходной цене."),
  en=("Smugglers' Market", "Everything forbidden, at fair prices."))
b("offshore", "trade", 3, {E: 6},
  ru=("Офшорная контора", "Тысяча компаний по одному адресу."),
  en=("Offshore Office", "A thousand companies at a single address."))
b("trade_guild", "trade", 3, {E: 4}, {"planet_jobs_trade_produces_mult": 0.05}, [("jobs/trader_add", 100)],
  ru=("Гильдия торговцев", "Местные купцы торгуют под защитой Синдиката."),
  en=("Merchants' Guild", "Local traders work under Syndicate protection."))
b("syndicate_exchange", "trade", 3, {E: 5, I: 0.3},
  ru=("Биржа Синдиката", "Котировки, о которых не пишут в новостях."),
  en=("Syndicate Exchange", "Quotes that never make the news."))

# ===== D. Ресурсы =====
b("mining_claim", "resource", 1, {M: 3}, {}, [("jobs/miners_add", 100)],
  ru=("Горный участок", "Скромная шахта, оформленная на подставное лицо."),
  en=("Mining Claim", "A modest mine registered to a straw man."))
b("ore_smugglers", "resource", 1, {M: 2}, {"planet_crime_add": 3},
  ru=("Контрабанда руды", "Часть добычи уходит мимо весов."),
  en=("Ore Smugglers", "Part of the yield bypasses the scales."))
b("scrap_yard", "resource", 1, {A: 1, M: 1},
  ru=("Свалка металлолома", "Из старых кораблей — новые сплавы."),
  en=("Scrap Yard", "Old ships become new alloys."))
b("hydroponic_den", "resource", 1, {F: 3}, {}, [("jobs/farmers_add", 100)],
  ru=("Гидропонная ферма", "Подвал, полный зелени и ламп."),
  en=("Hydroponic Den", "A basement full of greens and grow lamps."))
b("goods_workshop", "resource", 1, {CG: 2},
  ru=("Цех ширпотреба", "Подделки известных брендов, но работают."),
  en=("Knock-off Workshop", "Fake brands, but they work."))
b("crystal_cartel", "resource", 2, {RC: 0.5},
  ru=("Кристальный картель", "Контролирует продажу редких кристаллов."),
  en=("Crystal Cartel", "Controls the trade in rare crystals."))
b("gas_siphon", "resource", 2, {EG: 0.5},
  ru=("Газовый сифон", "Врезка в чужой газопровод."),
  en=("Gas Siphon", "A tap into someone else's gas line."))
b("mote_refinery", "resource", 2, {VM: 0.5},
  ru=("Перегонка мотов", "Кустарная установка по очистке летучих частиц."),
  en=("Mote Still", "A makeshift volatile mote refinery."))
b("alloy_forge", "resource", 2, {A: 2}, {}, [("jobs/foundry_add", 100)],
  ru=("Подпольная кузня", "Сплавы без маркировки и сертификатов."),
  en=("Underground Forge", "Alloys without markings or certificates."))
b("resource_depot", "resource", 2, {"country_resource_max_add": 500, M: 1},
  ru=("Склад Синдиката", "Запасы на чёрный день."),
  en=("Syndicate Depot", "Reserves for a rainy day."))
b("strip_mine", "resource", 3, {M: 5}, {"planet_stability_add": -2},
  ru=("Карьер", "Добыча без оглядки на экологию."),
  en=("Strip Mine", "Mining with no regard for ecology."))
b("rare_trading_post", "resource", 3, {RC: 0.5, EG: 0.5, VM: 0.5},
  ru=("Фактория редких ресурсов", "Обмен редкими ресурсами по всей сети."),
  en=("Rare Goods Trading Post", "Trades rare resources across the network."))

# ===== E. Наука =====
b("stolen_patents", "research", 1, {PHY: 0.01},
  ru=("Бюро краденых патентов", "Чужие изобретения — наши разработки."),
  en=("Stolen Patent Bureau", "Their inventions, our research."))
b("back_alley_lab", "research", 1, {ENG: 0.01},
  ru=("Лаборатория в подворотне", "Гениальные инженеры без лицензии."),
  en=("Back-Alley Lab", "Brilliant unlicensed engineers."))
b("sociology_circle", "research", 1, {SOC: 0.01},
  ru=("Подпольный кружок", "Запрещённые книги и долгие споры."),
  en=("Underground Study Circle", "Banned books and long debates."))
b("xeno_dealers", "research", 2, {SOC: 0.01, PHY: 0.01},
  ru=("Торговцы ксеноартефактами", "Древности из раскопок, о которых никто не знает."),
  en=("Xeno-Artifact Dealers", "Relics from digs nobody knows about."))
b("tech_smugglers", "research", 2, {ENG: 0.015},
  ru=("Контрабанда технологий", "Запчасти, которые не продаются иностранцам."),
  en=("Tech Smugglers", "Parts not for sale to foreigners."))
b("brain_drain", "research", 2, {PHY: 0.01, SOC: 0.01, ENG: 0.01}, {"planet_jobs_physics_research_produces_mult": -0.02},
  ru=("Утечка мозгов", "Синдикат переманивает местных учёных."),
  en=("Brain Drain", "The Syndicate lures away local scientists."))
b("prototype_shop", "research", 2, {ENG: 0.01, A: 1},
  ru=("Мастерская прототипов", "Опытные образцы, собранные вручную."),
  en=("Prototype Shop", "Hand-built prototypes."))
b("data_brokers", "research", 3, {PHY: 0.02, SPY: 1},
  ru=("Брокеры данных", "Покупают и продают чужие исследования."),
  en=("Data Brokers", "Buy and sell other people's research."))
b("secret_institute", "research", 3, {PHY: 0.015, SOC: 0.015, ENG: 0.015}, {}, [("jobs/researchers_add", 100)],
  ru=("Тайный институт", "Лучшие умы работают на сеть."),
  en=("Secret Institute", "The finest minds work for the network."))
b("dissident_academy", "research", 3, {SOC: 0.02, U: 2},
  ru=("Академия диссидентов", "Здесь учат думать иначе."),
  en=("Dissident Academy", "Teaches people to think differently."))

# ===== F. Пропаганда и единство =====
b("underground_press", "unity", 1, {U: 2, SPY: 1}, {"planet_stability_add": -4, "pop_government_ethic_attraction": -0.25}, CRIM,
  ru=("Подпольная типография", "Листовки, пиратское радио и голографические граффити."),
  en=("Underground Press", "Leaflets, pirate radio and holographic graffiti."))
b("pirate_radio", "unity", 1, {U: 2},
  ru=("Пиратское радио", "Музыка, новости и пароли между песнями."),
  en=("Pirate Radio", "Music, news and passwords between songs."))
b("graffiti_crew", "unity", 1, {U: 1}, {"planet_stability_add": -1},
  ru=("Бригада граффити", "Красная звезда на каждой стене."),
  en=("Graffiti Crew", "A red star on every wall."))
b("leaflet_drop", "unity", 1, {U: 1, I: 0.1},
  ru=("Листовки", "Тысячи листков с неба над площадью."),
  en=("Leaflet Drop", "Thousands of leaflets raining on the square."))
b("resistance_choir", "unity", 1, {U: 1}, {"pop_happiness": 0.01},
  ru=("Хор Сопротивления", "Старые партизанские песни на новый лад."),
  en=("Resistance Choir", "Old partisan songs, new arrangements."))
b("holo_cinema", "unity", 2, {U: 2}, {"planet_amenities_add": 2},
  ru=("Подпольный голокинотеатр", "Фильмы о героях, которых не покажут по ТВ."),
  en=("Underground Holo-Cinema", "Films about heroes you won't see on TV."))
b("martyr_shrine", "unity", 2, {U: 3},
  ru=("Святилище мучеников", "Имена павших выбиты на стене."),
  en=("Martyrs' Shrine", "The names of the fallen carved in stone."))
b("agitprop", "unity", 2, {U: 2, I: 0.2}, {"pop_government_ethic_attraction": -0.15},
  ru=("Агитпункт", "Брошюры, лекции и бесплатный чай."),
  en=("Agitprop Point", "Pamphlets, lectures and free tea."))
b("ideology_school", "unity", 3, {U: 4, I: 0.3},
  ru=("Школа идеологии", "Готовит пропагандистов для всей сети."),
  en=("School of Ideology", "Trains propagandists for the whole network."))
b("legend_museum", "unity", 3, {U: 5},
  ru=("Музей Легенды", "История партизан — от лесов до звёзд."),
  en=("Museum of the Legend", "The partisans' story, from forests to stars."))

# ===== G. Флот =====
b("smuggler_dock", "army", 1, {NAVAL: 2},
  ru=("Док контрабандистов", "Неприметный причал для быстрых кораблей."),
  en=("Smugglers' Dock", "An inconspicuous berth for fast ships."))
b("ship_breakers", "army", 1, {A: 1, M: 1},
  ru=("Разборка кораблей", "Списанные корабли идут на запчасти."),
  en=("Ship Breakers", "Decommissioned ships stripped for parts."))
b("crew_recruiters", "army", 2, {NAVAL: 3},
  ru=("Вербовщики экипажей", "Ищут пилотов в портовых барах."),
  en=("Crew Recruiters", "Hunting for pilots in dockside bars."))
b("hidden_shipyard", "army", 2, {A: 1, "starbase_shipyard_build_speed_mult": 0.01},
  ru=("Скрытая верфь", "Стапель в пещере астероида."),
  en=("Hidden Shipyard", "A slipway inside an asteroid cave."))
b("fuel_depot", "army", 2, {E: 2, NAVAL: 1},
  ru=("Топливный склад", "Заправка для своих, без записи в журнал."),
  en=("Fuel Depot", "Refuelling for friends, no log entries."))
b("privateer_berth", "army", 2, {NAVAL: 3, E: 1},
  ru=("Причал каперов", "Здесь каперы чинятся и делят добычу."),
  en=("Privateer Berth", "Privateers repair and split the loot here."))
b("navigator_guild", "army", 3, {"ship_speed_mult": 0.01, E: 1},
  ru=("Гильдия лоцманов", "Знает короткие пути через любые туманности."),
  en=("Navigators' Guild", "Knows shortcuts through any nebula."))
b("fleet_yards", "army", 3, {NAVAL: 5, A: 2},
  ru=("Теневая верфь", "Строит корабли без флагов и номеров."),
  en=("Shadow Fleet Yards", "Builds ships without flags or hull numbers."))

# ===== H. Помощь союзникам (только на планетах союзников/вассалов) =====
b("aid_clinic", "amenity", 1, {U: 1}, {"pop_happiness": 0.03}, [("job_healthcare_add", 100)], "ally",
  ru=("Клиника Синдиката", "Бесплатная медицина для союзников."),
  en=("Syndicate Clinic", "Free medicine for our allies."))
b("aid_food_bank", "amenity", 1, {I: 0.1}, {"planet_jobs_food_produces_mult": 0.05}, [("jobs/farmers_add", 100)], "ally",
  ru=("Продовольственный фонд", "Зерно и концентраты для союзных миров."),
  en=("Food Bank", "Grain and rations for allied worlds."))
b("aid_militia_trainers", "amenity", 1, {U: 1}, {"army_defense_damage_mult": 0.15, "army_defense_health_mult": 0.15}, None, "ally",
  ru=("Инструкторы ополчения", "Учат союзников обороняться по-партизански."),
  en=("Militia Trainers", "Teach allies to defend themselves partisan-style."))
b("aid_engineers", "amenity", 1, {U: 1}, {"planet_building_build_speed_mult": 0.20}, None, "ally",
  ru=("Инженерный корпус", "Помогает союзникам строить быстрее."),
  en=("Engineering Corps", "Helps allies build faster."))
b("aid_culture_house", "amenity", 1, {U: 1}, {"planet_amenities_add": 2}, [("jobs/entertainers_add", 100)], "ally",
  ru=("Дом культуры", "Концерты, кружки и танцы для союзников."),
  en=("House of Culture", "Concerts, clubs and dances for allies."))
b("aid_power_grid", "amenity", 2, {E: 1}, {"planet_jobs_energy_produces_mult": 0.10}, None, "ally",
  ru=("Энергосеть поддержки", "Синдикат налаживает союзникам энергоснабжение."),
  en=("Support Power Grid", "The Syndicate fixes its allies' power supply."))
b("aid_mining_advisers", "amenity", 2, {M: 1}, {"planet_jobs_minerals_produces_mult": 0.05}, [("jobs/miners_add", 100)], "ally",
  ru=("Горные советники", "Геологи Синдиката находят новые жилы."),
  en=("Mining Advisers", "Syndicate geologists find new veins."))
b("aid_foundry", "amenity", 2, {A: 1}, {}, [("jobs/foundry_add", 100)], "ally",
  ru=("Союзная литейная", "Сплавы для армий союзника."),
  en=("Allied Foundry", "Alloys for our ally's armies."))
b("aid_research_exchange", "amenity", 2, {U: 1}, {}, [("jobs/researchers_add", 100)], "ally",
  ru=("Научный обмен", "Совместные исследования с союзниками."),
  en=("Research Exchange", "Joint research with allies."))
b("aid_security", "amenity", 2, {I: 0.2}, {"planet_crime_add": -15, "planet_stability_add": 3}, None, "ally",
  ru=("Служба безопасности", "Синдикат наводит порядок у друзей."),
  en=("Security Service", "The Syndicate keeps order for its friends."))
b("aid_refugee_center", "amenity", 2, {U: 1}, {"pop_happiness": 0.02, "planet_stability_add": 2}, None, "ally",
  ru=("Центр беженцев", "Помощь тем, кто бежал от войны."),
  en=("Refugee Center", "Aid for those fleeing war."))
b("aid_trade_bridge", "amenity", 2, {E: 2}, {"planet_jobs_trade_produces_mult": 0.10}, None, "ally",
  ru=("Торговый мост", "Открывает союзникам рынки Синдиката."),
  en=("Trade Bridge", "Opens Syndicate markets to allies."))
b("aid_logistics", "amenity", 3, {E: 2}, {"planet_jobs_produces_mult": 0.05}, None, "ally",
  ru=("Логистический узел", "Снабжение союзной экономики по всем фронтам."),
  en=("Logistics Hub", "Supplies the allied economy on every front."))
b("aid_fortifications", "amenity", 3, {U: 2}, {"army_defense_damage_mult": 0.30, "army_defense_health_mult": 0.30, "planet_orbital_bombardment_damage": -0.25}, None, "ally",
  ru=("Укрепрайон", "Бункеры и ходы сообщения для обороны союзника."),
  en=("Fortified Zone", "Bunkers and trenches for the ally's defense."))
b("aid_war_chest", "amenity", 3, {A: 1}, {"planet_jobs_alloys_produces_mult": 0.10}, None, "ally",
  ru=("Военный фонд", "Синдикат финансирует оборонную промышленность союзника."),
  en=("War Chest", "The Syndicate funds the ally's defense industry."))
b("aid_unity_council", "amenity", 3, {I: 0.3}, {"planet_jobs_unity_produces_mult": 0.10}, None, "ally",
  ru=("Совет единства", "Общие праздники и общие герои."),
  en=("Unity Council", "Shared holidays and shared heroes."))

# ===== I. Подрыв (только на планетах соперников/врагов) =====
b("sub_strike_committee", "government", 1, {U: 1}, {"planet_jobs_produces_mult": -0.05, "planet_stability_add": -3}, None, "enemy",
  ru=("Стачком", "Организует забастовки на чужих заводах."),
  en=("Strike Committee", "Organises strikes in their factories."))
b("sub_rumor_mill", "government", 1, {SPY: 2}, {"planet_stability_add": -4, "pop_happiness": -0.05}, None, "enemy",
  ru=("Фабрика слухов", "Шепчет о коррупции и скорой войне."),
  en=("Rumor Mill", "Whispers of corruption and coming war."))
b("sub_saboteurs", "government", 2, {A: 1}, {"planet_jobs_alloys_produces_mult": -0.15}, None, "enemy",
  ru=("Диверсанты на заводах", "Песок в подшипниках, брак в сплавах."),
  en=("Factory Saboteurs", "Sand in the bearings, flaws in the alloys."))
b("sub_blackout", "government", 2, {E: 2}, {"planet_jobs_energy_produces_mult": -0.15}, None, "enemy",
  ru=("Энергоблокада", "Подстанции выходят из строя одна за другой."),
  en=("Blackout Campaign", "Substations fail one after another."))
b("sub_crime_wave", "government", 2, {E: 2}, {"planet_crime_add": 20}, CRIM, "enemy",
  ru=("Волна преступности", "Синдикат отпускает своих бойцов на волю."),
  en=("Crime Wave", "The Syndicate lets its enforcers off the leash."))
b("sub_food_riots", "government", 2, {F: 2}, {"planet_jobs_food_produces_mult": -0.20, "planet_stability_add": -3}, None, "enemy",
  ru=("Голодные бунты", "Скупка зерна и пустые полки."),
  en=("Bread Riots", "Hoarded grain and empty shelves."))
b("sub_brain_poaching", "government", 3, {PHY: 0.01, SOC: 0.01, ENG: 0.01},
  {"planet_jobs_physics_research_produces_mult": -0.10, "planet_jobs_society_research_produces_mult": -0.10,
   "planet_jobs_engineering_research_produces_mult": -0.10}, None, "enemy",
  ru=("Переманивание учёных", "Лучшие умы врага работают на нас."),
  en=("Brain Poaching", "The enemy's finest minds work for us."))
b("sub_mutiny_cells", "government", 3, {SPY: 3}, {"army_defense_damage_mult": -0.25, "planet_stability_add": -5}, None, "enemy",
  ru=("Ячейки мятежа", "Гарнизон врага ненадёжен."),
  en=("Mutiny Cells", "The enemy garrison is unreliable."))

assert len(B) == 100, len(B)
assert len({x["key"] for x in B}) == 100

TIER = {1: dict(time="@b1_time", min=300, inf=10, up=2, pre=None),
        2: dict(time="@b2_time", min=500, inf=20, up=3, pre="tech_ps_guerrilla_doctrine"),
        3: dict(time="@b3_time", min=800, inf=30, up=5, pre="tech_ps_ghost_networks")}


def fmt(v):
    return f"{v:g}"


def building(x):
    k = f"building_ps_{x['key']}"
    t = TIER[x["tier"]]
    o = []
    o.append(f"{k} = {{\n\tbase_buildtime = {t['time']}\n\tplanet_limit = 1\n\n\towner_type = corporate\n\tcategory = {x['cat']}\n")
    o.append("\tpotential = {\n\t\thas_branch_office = yes\n\t\tbranch_office_owner = { ps_is_partisan_empire = yes }\n\t}\n")
    if x["req"]:
        trig = "ps_branch_host_is_friend" if x["req"] == "ally" else "ps_branch_host_is_enemy"
        o.append(f"\n\tallow = {{\n\t\tcustom_tooltip = {{\n\t\t\tfail_text = {trig}_fail\n\t\t\t{trig} = yes\n\t\t}}\n\t}}\n")
    if t["pre"]:
        o.append(f'\n\tprerequisites = {{\n\t\t"{t["pre"]}"\n\t}}\n')
    scaled = {m: v for m, v in x["owner"].items() if m not in STATIC}
    static = {m: v for m, v in x["owner"].items() if m in STATIC}
    if scaled:
        o.append("\n\t# Владельцу филиала (растёт с ценностью филиала)\n\ttriggered_country_modifier = {\n\t\tpotential = { always = yes }\n")
        o += [f"\t\t{m} = {fmt(v)}\n" for m, v in scaled.items()]
        o.append("\t\tmult = value:branch_office_value_for_buildings\n\t}\n")
    if static:
        o.append("\n\t# Владельцу филиала (фиксированно)\n\ttriggered_country_modifier = {\n\t\tpotential = { always = yes }\n")
        o += [f"\t\t{m} = {fmt(v)}\n" for m, v in static.items()]
        o.append("\t}\n")
    if x["host"]:
        crime = x["host"].get("planet_crime_add")
        rest = {m: v for m, v in x["host"].items() if not (m == "planet_crime_add" and v > 0)}
        if rest:
            pot = "always = yes"
            if x["req"] == "ally":
                pot = "ps_branch_host_is_friend = yes"
            elif x["req"] == "enemy":
                pot = "ps_branch_host_is_enemy = yes"
            o.append(f"\n\t# Планете-хозяину\n\ttriggered_planet_modifier = {{\n\t\tpotential = {{ {pot} }}\n")
            o += [f"\t\t{m} = {fmt(v)}\n" for m, v in rest.items()]
            o.append("\t}\n")
        if crime and crime > 0:
            o.append(f"\n\ttriggered_planet_modifier = {{\n\t\tplanet_crime_add = {fmt(crime)}\n"
                     f"\t\tmult = branch_office_owner.value:scripted_modifier_mult|MODIFIER|branch_office_holding_crime_mult|\n\t}}\n")
    for script, amount in x["jobs"]:
        if script.startswith("job_"):
            o.append(f"\n\ttriggered_planet_modifier = {{\n\t\tpotential = {{ always = yes }}\n\t\t{script} = {amount}\n\t}}\n")
        else:
            o.append(f"\n\tinline_script = {{\n\t\tscript = {script}\n\t\tAMOUNT = {amount}\n\t}}\n")
    o.append(f"\n\tresources = {{\n\t\tcategory = planet_branch_office_buildings\n\t\tcost = {{\n\t\t\tminerals = {t['min']}\n"
             f"\t\t\tinfluence = {t['inf']}\n\t\t}}\n\t\tupkeep = {{\n\t\t\tenergy = {t['up']}\n\t\t}}\n\t}}\n")
    o.append("\n\tai_weight = {\n\t\tfactor = 10\n\t}\n}\n")
    return "".join(o)


THEMES_RU = {"army": "армия/флот", "government": "шпионаж/подрыв", "trade": "деньги", "resource": "ресурсы",
             "research": "наука", "unity": "пропаганда", "amenity": "помощь союзникам"}


def main():
    hdr = ("# АВТОГЕНЕРАЦИЯ: tools/gen_branch_buildings.py — правьте генератор, а не этот файл\n"
           "# Синдикат Сопротивления — 100 зданий филиалов\n\n")
    (ROOT / "common/buildings/ps_branch_offices.txt").write_text(hdr + "\n".join(building(x) for x in B), encoding="utf-8")

    gfx = ["spriteTypes = {"]
    for x in B:
        k = f"building_ps_{x['key']}"
        gfx.append(f'\tspriteType = {{\n\t\tname = "GFX_{k}"\n\t\ttexturefile = "gfx/interface/icons/buildings/{k}.dds"\n\t}}')
    gfx.append("}\n")
    (ROOT / "interface/ps_buildings.gfx").write_text("\n".join(gfx), encoding="utf-8")

    for lang in ("russian", "english"):
        ru = lang == "russian"
        L = [f"l_{lang}:"]
        for x in B:
            k = f"building_ps_{x['key']}"
            name, desc = x["ru"] if ru else x["en"]
            if x["req"] == "ally":
                desc += "\\n\\n§Y" + ("Только на планетах союзников, вассалов, членов федерации и дружественных империй." if ru else
                                     "Allied, subject, federation or friendly worlds only.") + "§!"
            elif x["req"] == "enemy":
                desc += "\\n\\n§R" + ("Только на планетах соперников, врагов и недружественных империй." if ru else
                                     "Rival, enemy or unfriendly worlds only.") + "§!"
            L += [f' {k}:0 "{name}"', f' {k}_desc:0 "{desc}"']
        if ru:
            L += [' ps_branch_host_is_friend_fail:0 "Планета должна принадлежать §Yсоюзнику§!: вассалу, члену федерации, партнёру по оборонному пакту или дружественной империи."',
                  ' ps_branch_host_is_enemy_fail:0 "Планета должна принадлежать §Rсоппернику§!, врагу или недружественной империи."'.replace("соппернику", "сопернику")]
        else:
            L += [' ps_branch_host_is_friend_fail:0 "The planet must belong to an §Yally§!: a subject, federation member, defensive pact partner or friendly empire."',
                  ' ps_branch_host_is_enemy_fail:0 "The planet must belong to a §Rrival§!, enemy or unfriendly empire."']
        (ROOT / f"localisation/{lang}/ps_buildings_l_{lang}.yml").write_bytes(b"\xef\xbb\xbf" + ("\n".join(L) + "\n").encode())

    try:
        from build_assets import icon, save_dds
        from PIL import ImageDraw
    except ImportError:
        print("Pillow не найден — иконки не созданы")
        return
    kind = {"army": "star", "government": "eye", "trade": "crown", "resource": "tree", "research": "net",
            "unity": "press", "amenity": "tree"}
    colors = {1: (120, 200, 120, 255), 2: (220, 180, 60, 255), 3: (220, 60, 60, 255)}
    for x in B:
        img = icon(kind[x["cat"]], 64)
        d = ImageDraw.Draw(img)
        for j in range(x["tier"]):
            d.ellipse([8 + j * 10, 50, 15 + j * 10, 57], fill=colors[x["tier"]])
        if x["req"] == "ally":
            d.rectangle([48, 6, 58, 16], fill=(60, 160, 220, 255))
        elif x["req"] == "enemy":
            d.rectangle([48, 6, 58, 16], fill=(200, 30, 30, 255))
        save_dds(img, f"gfx/interface/icons/buildings/building_ps_{x['key']}.dds")
    from collections import Counter
    print("ok:", len(B), "buildings;", dict(Counter(THEMES_RU[x["cat"]] for x in B)))


if __name__ == "__main__":
    main()
