#!/usr/bin/env python3
"""Генератор владений («ячеек») Синдиката на планетах вассалов — 100 шт.

Создаёт:
  common/buildings/ps_cell_holdings.txt
  interface/ps_holdings.gfx + DDS-иконки (заглушки)
  localisation/{russian,english}/ps_holdings_l_*.yml

Формат сверен с vanilla 4.x common/buildings/15_overlord_holdings.txt:
  owner_type = subject_holding, resources.category = planet_holdings
  planet_modifier            -> планета вассала
  country_modifier           -> сюзерен (владелец здания)
  job_overlord_*_add         -> должности сюзерена на планете вассала (+ *_drone_add для гештальтов)
  скоупы: owner = вассал, owner.overlord = сюзерен, planet.owner = вассал

Запуск из корня репозитория:  python3 tools/gen_holdings.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

E, M, F, A, U, I = (f"country_base_{r}_produces_add" for r in ("energy", "minerals", "food", "alloys", "unity", "influence"))
CG, RC, EG, VM = (f"country_base_{r}_produces_add" for r in ("consumer_goods", "rare_crystals", "exotic_gases", "volatile_motes"))
PHY, SOC, ENG = ("country_physics_research_produces_mult", "country_society_research_produces_mult",
                 "country_engineering_research_produces_mult")
LOY = "monthly_loyalty"

# Должности сюзерена (обычная, гештальт) — из vanilla 15_overlord_holdings.txt
JOB = {
    "academic": ("job_overlord_academic_add", "job_overlord_academic_drone_add"),
    "propagandist": ("job_overlord_propagandist_add", "job_overlord_propagandist_drone_add"),
    "trader": ("job_overlord_trader_add", "job_overlord_trader_drone_add"),
    "recruiter": ("job_overlord_recruiter_add", "job_overlord_recruiter_drone_add"),
    "beholder": ("job_overlord_beholder_add", "job_overlord_beholder_drone_add"),
    "aid": ("job_aid_worker_add", "job_aid_worker_drone_add"),
}

H = []


def h(key, cat, tier, ru, en, overlord=None, planet=None, job=None, jobs=100, spec=None, unique=False, upkeep=None):
    H.append(dict(key=key, cat=cat, tier=tier, ru=ru, en=en, overlord=overlord or {}, planet=planet or {},
                  job=job, jobs=jobs, spec=spec, unique=unique, upkeep=upkeep))


# ===== A. Гарнизон и оборона вассала (12) =====
h("cell_garrison", "army", 1, ("Гарнизон ячейки", "Партизанский гарнизон держит порядок и верность."), ("Cell Garrison", "A partisan garrison keeps order and loyalty."),
  planet={"planet_crime_add": -10, LOY: 0.5, "army_defense_damage_mult": 0.10})
h("militia_school", "army", 1, ("Школа ополчения", "Местные учатся обороняться по-партизански."), ("Militia School", "Locals learn partisan self-defence."),
  planet={"army_defense_damage_mult": 0.20, "army_defense_health_mult": 0.20})
h("arms_depot", "army", 1, ("Склад оружия", "Оружие сюзерена на случай вторжения."), ("Arms Depot", "The overlord's weapons in case of invasion."),
  overlord={"army_damage_mult": 0.01}, planet={"army_defense_health_mult": 0.15})
h("recruitment_post", "army", 1, ("Вербовочный пункт", "Вербует добровольцев во флот сюзерена."), ("Recruitment Post", "Recruits volunteers for the overlord's fleet."),
  overlord={"country_naval_cap_add": 3}, job="recruiter")
h("watchtower", "army", 1, ("Сторожевая вышка", "Наблюдатели следят за небом и улицами."), ("Watchtower", "Watchers keep an eye on the sky and the streets."),
  planet={"planet_crime_add": -5, "planet_stability_add": 2}, job="beholder")
h("bunker_network", "army", 2, ("Сеть бункеров", "Подземные укрытия на случай оккупации."), ("Bunker Network", "Underground shelters in case of occupation."),
  planet={"army_defense_damage_mult": 0.25, "army_defense_health_mult": 0.25, "planet_orbital_bombardment_damage": -0.20})
h("naval_depot", "army", 2, ("Флотский склад", "Снабжение для флота сюзерена."), ("Naval Depot", "Supplies for the overlord's fleet."),
  overlord={"country_naval_cap_add": 5})
h("officer_school", "army", 2, ("Офицерская школа", "Готовит командиров для армии сюзерена."), ("Officer School", "Trains commanders for the overlord's army."),
  overlord={"army_starting_experience_add": 10})
h("fortress_cell", "army", 2, ("Крепость-ячейка", "Опорный пункт сети."), ("Fortress Cell", "A strongpoint of the network."),
  planet={"army_defense_damage_mult": 0.30, LOY: 0.5}, upkeep={"energy": 4})
h("rapid_response", "army", 3, ("Отряд быстрого реагирования", "Подавляет беспорядки за часы."), ("Rapid Response Unit", "Crushes unrest within hours."),
  planet={"planet_stability_add": 5, "planet_crime_add": -15, LOY: 0.5})
h("strategic_reserve", "army", 3, ("Стратегический резерв", "Армии, готовые к переброске на фронт сюзерена."), ("Strategic Reserve", "Armies ready to deploy to the overlord's front."),
  overlord={"country_naval_cap_add": 8, "army_damage_mult": 0.02}, upkeep={"energy": 5})
h("partisan_citadel", "army", 3, ("Цитадель Сопротивления", "Последний рубеж обороны вассала."), ("Resistance Citadel", "The subject's last line of defence."),
  planet={"army_defense_damage_mult": 0.50, "army_defense_health_mult": 0.50, "planet_orbital_bombardment_damage": -0.35}, upkeep={"energy": 5})

# ===== B. Разведка (12) =====
h("listening_post", "government", 1, ("Пост прослушки", "Слушает эфир соседей вассала."), ("Listening Post", "Monitors the subject's neighbours."),
  overlord={"spy_network_levels_add": 2})
h("safehouse", "government", 1, ("Конспиративная квартира", "Явка для агентов сюзерена."), ("Safehouse", "A hideout for the overlord's agents."),
  overlord={"spy_network_levels_add": 1, U: 1})
h("courier_hub", "government", 1, ("Курьерский узел", "Агенты и донесения идут через вассала."), ("Courier Hub", "Agents and reports pass through the subject."),
  overlord={"spy_network_daily_value_mult": 0.01})
h("watch_office", "government", 1, ("Бюро наблюдения", "Следит за настроениями вассала."), ("Watch Office", "Monitors the subject's mood."),
  planet={LOY: 0.25}, job="beholder")
h("cipher_station", "government", 2, ("Шифровальная станция", "Квантовые ключи для всей сети."), ("Cipher Station", "Quantum keys for the whole network."),
  overlord={"intel_encryption_add": 1}, unique=True)
h("decryption_center", "government", 2, ("Центр дешифровки", "Взламывает коды соседей."), ("Decryption Center", "Cracks the neighbours' codes."),
  overlord={"intel_decryption_add": 1}, unique=True)
h("agent_academy", "government", 2, ("Академия агентов", "Готовит разведчиков для сюзерена."), ("Agent Academy", "Trains spies for the overlord."),
  overlord={"spy_network_levels_add": 3})
h("informant_web", "government", 2, ("Сеть осведомителей", "Каждый лавочник что-то знает."), ("Informant Web", "Every shopkeeper knows something."),
  overlord={"spy_network_daily_value_mult": 0.02}, planet={"planet_crime_add": -5})
h("envoy_residence", "government", 2, ("Резиденция посланника", "Неофициальная дипломатия сюзерена."), ("Envoy Residence", "The overlord's unofficial diplomacy."),
  overlord={"envoys_add": 1}, unique=True)
h("black_archive", "government", 3, ("Чёрный архив", "Досье на всех соседей вассала."), ("Black Archive", "Dossiers on all of the subject's neighbours."),
  overlord={"spy_network_levels_add": 4, U: 1})
h("counterintel_bureau", "government", 3, ("Бюро контрразведки", "Ловит чужих шпионов в сети."), ("Counterintelligence Bureau", "Catches foreign spies in the network."),
  overlord={"intel_encryption_add": 1}, planet={"planet_crime_add": -10}, unique=True)
h("shadow_directorate", "government", 3, ("Теневая дирекция", "Координирует разведку всех ячеек."), ("Shadow Directorate", "Coordinates intelligence across all cells."),
  overlord={"spy_network_daily_value_mult": 0.03, "spy_network_levels_add": 2}, upkeep={"energy": 4})

# ===== C. Дань и деньги (12) =====
h("tribute_office", "trade", 1, ("Контора дани", "Собирает долю для сюзерена."), ("Tribute Office", "Collects the overlord's share."),
  overlord={E: 3}, planet={LOY: -0.25})
h("trading_house", "trade", 1, ("Торговый дом", "Купцы сюзерена работают у вассала."), ("Trading House", "The overlord's merchants work at the subject."),
  overlord={E: 2}, job="trader")
h("exchange_office", "trade", 1, ("Обменная контора", "Валюта сюзерена в обороте вассала."), ("Exchange Office", "The overlord's currency in the subject's economy."),
  overlord={E: 2, U: 1})
h("bank_branch", "trade", 1, ("Отделение банка", "Кредиты вассалу под проценты."), ("Bank Branch", "Loans to the subject at interest."),
  overlord={E: 3})
h("customs_house", "trade", 2, ("Таможня", "Пошлины с торговли вассала."), ("Customs House", "Duties on the subject's trade."),
  overlord={E: 4}, planet={LOY: -0.25})
h("insurance_agency", "trade", 2, ("Страховое агентство", "Страхует всё, что можно застраховать."), ("Insurance Agency", "Insures everything insurable."),
  overlord={E: 3, I: 0.2})
h("investment_fund", "trade", 2, ("Инвестиционный фонд", "Вкладывает в экономику вассала и получает дивиденды."), ("Investment Fund", "Invests in the subject's economy and collects dividends."),
  overlord={E: 3}, planet={"planet_jobs_produces_mult": 0.03})
h("market_hall", "trade", 2, ("Рыночный зал", "Большой рынок под контролем Синдиката."), ("Market Hall", "A big market controlled by the Syndicate."),
  overlord={E: 3}, job="trader", jobs=200)
h("casino_resort", "trade", 2, ("Курорт-казино", "Развлечения для богатых и налоги для сюзерена."), ("Casino Resort", "Entertainment for the rich and taxes for the overlord."),
  overlord={E: 4}, planet={"planet_amenities_add": 500})
h("syndicate_bank", "trade", 3, ("Банк Синдиката", "Главный финансовый узел ячейки."), ("Syndicate Bank", "The cell's main financial hub."),
  overlord={E: 6, I: 0.3}, upkeep={"energy": 3})
h("offshore_zone", "trade", 3, ("Офшорная зона", "Тысяча фирм-однодневок."), ("Offshore Zone", "A thousand shell companies."),
  overlord={E: 8}, planet={LOY: -0.5})
h("trade_consortium", "trade", 3, ("Торговый консорциум", "Монополия на торговлю вассала."), ("Trade Consortium", "A monopoly on the subject's trade."),
  overlord={E: 5, CG: 2}, job="trader", jobs=200)

# ===== D. Ресурсы (12) =====
h("mining_concession", "resource", 1, ("Горная концессия", "Шахты сюзерена на земле вассала."), ("Mining Concession", "The overlord's mines on the subject's land."),
  overlord={M: 4}, planet={LOY: -0.25})
h("farm_lease", "resource", 1, ("Арендованные фермы", "Урожай идёт сюзерену."), ("Leased Farms", "The harvest goes to the overlord."),
  overlord={F: 4}, planet={LOY: -0.25})
h("power_plant", "resource", 1, ("Электростанция", "Энергия для сюзерена."), ("Power Plant", "Energy for the overlord."),
  overlord={E: 3})
h("alloy_works", "resource", 2, ("Сплавный завод", "Сплавы для флота сюзерена."), ("Alloy Works", "Alloys for the overlord's fleet."),
  overlord={A: 2}, planet={LOY: -0.25})
h("goods_factory", "resource", 1, ("Фабрика товаров", "Товары для рынка сюзерена."), ("Goods Factory", "Goods for the overlord's market."),
  overlord={CG: 2})
h("crystal_mine", "resource", 2, ("Кристальная шахта", "Редкие кристаллы для сюзерена."), ("Crystal Mine", "Rare crystals for the overlord."),
  overlord={RC: 0.5})
h("gas_extractor", "resource", 2, ("Газовый экстрактор", "Экзотические газы для сюзерена."), ("Gas Extractor", "Exotic gases for the overlord."),
  overlord={EG: 0.5})
h("mote_refinery", "resource", 2, ("Перегонка мотов", "Летучие частицы для сюзерена."), ("Mote Refinery", "Volatile motes for the overlord."),
  overlord={VM: 0.5})
h("resource_depot", "resource", 2, ("Ресурсный склад", "Запасы сюзерена хранятся у вассала."), ("Resource Depot", "The overlord's reserves are stored at the subject."),
  overlord={"country_resource_max_add": 1000})
h("rare_guidance", "resource", 3, ("Центр редких ресурсов", "Учит вассала добывать редкое и делится добычей."), ("Rare Resource Center", "Teaches the subject to extract rare goods and shares the yield."),
  overlord={RC: 0.5, EG: 0.5, VM: 0.5}, planet={"planet_jobs_produces_mult": 0.05}, upkeep={"energy": 4})
h("industrial_combine", "resource", 3, ("Промышленный комбинат", "Тяжёлая промышленность для сюзерена."), ("Industrial Combine", "Heavy industry for the overlord."),
  overlord={A: 4, M: 2}, planet={LOY: -0.5}, upkeep={"energy": 4})
h("strategic_stockpile", "resource", 3, ("Стратегические запасы", "Огромные хранилища сюзерена."), ("Strategic Stockpile", "The overlord's huge warehouses."),
  overlord={"country_resource_max_add": 3000, M: 1})

# ===== E. Наука (10) =====
h("research_outpost", "research", 1, ("Научный аванпост", "Учёные сюзерена работают у вассала."), ("Research Outpost", "The overlord's scientists work at the subject."),
  job="academic")
h("patent_office", "research", 1, ("Патентное бюро", "Изобретения вассала регистрируются на сюзерена."), ("Patent Office", "The subject's inventions are registered to the overlord."),
  overlord={ENG: 0.01})
h("xeno_institute", "research", 1, ("Ксеноинститут", "Изучает культуру и природу вассала."), ("Xeno Institute", "Studies the subject's culture and nature."),
  overlord={SOC: 0.01})
h("physics_lab", "research", 1, ("Физическая лаборатория", "Опыты, которые дома запрещены."), ("Physics Lab", "Experiments that are banned at home."),
  overlord={PHY: 0.01})
h("joint_university", "research", 2, ("Совместный университет", "Учит студентов вассала и сюзерена вместе."), ("Joint University", "Teaches students of both subject and overlord."),
  planet={LOY: 0.5}, job="academic", jobs=200)
h("tech_transfer", "research", 2, ("Центр передачи технологий", "Делится знаниями с вассалом."), ("Tech Transfer Center", "Shares knowledge with the subject."),
  planet={"planet_jobs_produces_mult": 0.03, LOY: 0.5})
h("data_center", "research", 2, ("Центр обработки данных", "Вычислительные мощности сюзерена."), ("Data Center", "The overlord's computing power."),
  overlord={PHY: 0.01, ENG: 0.01})
h("archaeology_bureau", "research", 2, ("Археологическое бюро", "Раскопки на земле вассала."), ("Archaeology Bureau", "Excavations on the subject's land."),
  overlord={SOC: 0.015})
h("secret_institute", "research", 3, ("Тайный институт", "Лучшие умы работают на сеть."), ("Secret Institute", "The best minds work for the network."),
  overlord={PHY: 0.015, SOC: 0.015, ENG: 0.015}, job="academic", upkeep={"energy": 4})
h("think_tank", "research", 3, ("Мозговой центр", "Стратеги Синдиката планируют будущее."), ("Think Tank", "Syndicate strategists plan the future."),
  overlord={"all_technology_research_speed": 0.02}, unique=True, upkeep={"energy": 5})

# ===== F. Лояльность и пропаганда (10) =====
h("propaganda_office", "unity", 1, ("Агитпункт ячейки", "Рассказывает вассалу о дружбе с Синдикатом."), ("Cell Propaganda Office", "Tells the subject about friendship with the Syndicate."),
  planet={LOY: 0.5}, job="propagandist")
h("memorial_hall", "unity", 1, ("Зал памяти", "Общая история Сопротивления."), ("Memorial Hall", "A shared history of the Resistance."),
  overlord={U: 2}, planet={LOY: 0.5})
h("radio_relay", "unity", 1, ("Ретранслятор радио", "Голос Синдиката в эфире вассала."), ("Radio Relay", "The Syndicate's voice on the subject's air."),
  overlord={U: 1}, planet={LOY: 0.25, "planet_stability_add": 1})
h("youth_league", "unity", 1, ("Молодёжная лига", "Воспитывает верную молодёжь."), ("Youth League", "Raises a loyal youth."),
  planet={LOY: 0.75})
h("cultural_center", "unity", 2, ("Культурный центр", "Концерты, фильмы и праздники Синдиката."), ("Cultural Center", "Syndicate concerts, films and holidays."),
  overlord={U: 2}, planet={"planet_amenities_add": 500, LOY: 0.5})
h("oath_hall", "unity", 2, ("Зал присяги", "Здесь клянутся в верности сети."), ("Oath Hall", "Where oaths of loyalty to the network are sworn."),
  planet={LOY: 1})
h("veterans_union", "unity", 2, ("Союз ветеранов", "Ветераны общих войн хранят дружбу."), ("Veterans' Union", "Veterans of shared wars keep the friendship."),
  overlord={U: 2}, planet={LOY: 0.5, "planet_stability_add": 2})
h("press_agency", "unity", 2, ("Информагентство", "Новости в нужном свете."), ("Press Agency", "News in the right light."),
  overlord={U: 3}, job="propagandist")
h("unity_council", "unity", 3, ("Совет единства", "Общие решения сюзерена и вассала."), ("Unity Council", "Joint decisions of overlord and subject."),
  overlord={U: 4, I: 0.3}, planet={LOY: 1}, upkeep={"energy": 4})
h("hall_of_heroes", "unity", 3, ("Пантеон героев", "Имена героев Сопротивления обоих народов."), ("Hall of Heroes", "The names of Resistance heroes of both peoples."),
  overlord={U: 5}, planet={LOY: 1, "planet_stability_add": 3}, upkeep={"energy": 4})

# ===== G. Помощь вассалу (16) =====
h("aid_mission", "amenity", 1, ("Миссия помощи", "Врачи и волонтёры Синдиката."), ("Aid Mission", "Syndicate doctors and volunteers."),
  planet={LOY: 0.5}, job="aid")
h("construction_brigade", "amenity", 1, ("Строительная бригада", "Помогает вассалу строиться."), ("Construction Brigade", "Helps the subject build."),
  planet={"planet_building_build_speed_mult": 0.20, LOY: 0.25})
h("clinic", "amenity", 1, ("Поликлиника", "Бесплатная медицина для вассала."), ("Clinic", "Free healthcare for the subject."),
  planet={"pop_happiness": 0.03, LOY: 0.5})
h("food_aid", "amenity", 1, ("Продовольственная помощь", "Зерно и концентраты."), ("Food Aid", "Grain and rations."),
  planet={"planet_jobs_food_produces_mult": 0.10, LOY: 0.25})
h("power_grid", "amenity", 1, ("Энергосеть", "Надёжное энергоснабжение для вассала."), ("Power Grid", "Reliable power for the subject."),
  planet={"planet_jobs_energy_produces_mult": 0.10})
h("mining_advisers", "amenity", 2, ("Горные советники", "Геологи находят новые жилы."), ("Mining Advisers", "Geologists find new veins."),
  planet={"planet_jobs_minerals_produces_mult": 0.10, LOY: 0.25})
h("industrial_aid", "amenity", 2, ("Промышленная помощь", "Станки и инженеры для вассала."), ("Industrial Aid", "Machine tools and engineers for the subject."),
  planet={"planet_jobs_alloys_produces_mult": 0.10, "planet_jobs_consumer_goods_produces_mult": 0.10})
h("research_aid", "amenity", 2, ("Научная помощь", "Учим учёных вассала."), ("Research Aid", "Training the subject's scientists."),
  planet={"planet_jobs_physics_research_produces_mult": 0.10, "planet_jobs_society_research_produces_mult": 0.10,
          "planet_jobs_engineering_research_produces_mult": 0.10})
h("housing_program", "amenity", 2, ("Жилищная программа", "Новые кварталы для вассала."), ("Housing Program", "New districts for the subject."),
  planet={"planet_housing_add": 500, LOY: 0.5})
h("security_service", "amenity", 2, ("Служба безопасности", "Синдикат наводит порядок у вассала."), ("Security Service", "The Syndicate keeps order at the subject."),
  planet={"planet_crime_add": -15, "planet_stability_add": 3})
h("culture_house", "amenity", 2, ("Дом культуры", "Досуг для жителей вассала."), ("House of Culture", "Leisure for the subject's people."),
  planet={"planet_amenities_add": 1000, LOY: 0.25})
h("refugee_center", "amenity", 2, ("Центр беженцев", "Помогает тем, кто бежал от войны."), ("Refugee Center", "Helps those fleeing war."),
  planet={"planet_resettlement_unemployed_mult": 0.25, "pop_happiness": 0.02})
h("logistics_hub", "amenity", 3, ("Логистический узел", "Снабжение всей экономики вассала."), ("Logistics Hub", "Supplies the subject's whole economy."),
  planet={"planet_jobs_produces_mult": 0.05, LOY: 0.5}, upkeep={"energy": 4})
h("reconstruction_fund", "amenity", 3, ("Фонд восстановления", "Отстраивает разрушенное войной."), ("Reconstruction Fund", "Rebuilds what war destroyed."),
  planet={"planet_building_build_speed_mult": 0.35, "planet_stability_add": 3, LOY: 0.5}, upkeep={"energy": 4})
h("medical_center", "amenity", 3, ("Медицинский центр", "Лучшая медицина сети."), ("Medical Center", "The network's best medicine."),
  planet={"pop_happiness": 0.05, LOY: 1}, job="aid", upkeep={"energy": 4})
h("prosperity_program", "amenity", 3, ("Программа процветания", "Синдикат вкладывается в будущее вассала."), ("Prosperity Program", "The Syndicate invests in the subject's future."),
  planet={"planet_jobs_produces_mult": 0.08, "pop_happiness": 0.03, LOY: 1}, upkeep={"energy": 6})

# ===== H. Под специализацию Синдиката (12) — только у вассала нужного типа =====
SPEC = [
    ("ps_strike", "Ударный легион", "Strike Legion",
     ("fleet_yard", "Верфь легиона", "Legion Yard", {"country_naval_cap_add": 10}, {}),
     ("gunnery_school", "Школа канониров", "Gunnery School", {"ship_fire_rate_mult": 0.03}, {})),
    ("ps_assault", "Штурмовой корпус", "Assault Corps",
     ("assault_barracks", "Штурмовые казармы", "Assault Barracks", {"army_damage_mult": 0.05}, {"army_defense_damage_mult": 0.25}),
     ("drop_pod_factory", "Завод десантных капсул", "Drop Pod Factory", {"army_starting_experience_add": 25}, {})),
    ("ps_raiders", "Каперская флотилия", "Privateer Flotilla",
     ("privateer_harbor", "Каперская гавань", "Privateer Harbor", {"ship_speed_mult": 0.02, E: 2}, {}),
     ("prize_court", "Призовой суд", "Prize Court", {E: 4}, {LOY: 0.25})),
    ("ps_residency", "Шпионская резидентура", "Spy Residency",
     ("residency_hq", "Штаб резидентуры", "Residency HQ", {"spy_network_levels_add": 5}, {}),
     ("embassy_quarter", "Посольский квартал", "Embassy Quarter", {"spy_network_daily_value_mult": 0.03}, {})),
    ("ps_exchange", "Теневая биржа", "Shadow Exchange",
     ("clearing_house", "Расчётная палата", "Clearing House", {E: 8}, {}),
     ("hedge_fund", "Хедж-фонд", "Hedge Fund", {E: 5, I: 0.3}, {})),
    ("ps_trust", "Ресурсный трест", "Resource Trust",
     ("trust_mines", "Шахты треста", "Trust Mines", {M: 6, A: 1}, {}),
     ("trust_refinery", "Завод треста", "Trust Refinery", {RC: 0.5, EG: 0.5, VM: 0.5}, {})),
]
for spec, sru, sen, *items in SPEC:
    for (k, ru, en, ov, pl) in items:
        h(k, "government", 2, (ru, f"Только у вассала-специалиста «{sru}»."), (en, f"Only at a «{sen}» specialist subject."),
          overlord=ov, planet=pl, spec=spec)

# ===== I. Партизанская подготовка (4) =====
h("guerrilla_camp", "army", 1, ("Партизанский лагерь", "Учит воевать без армии."), ("Guerrilla Camp", "Teaches fighting without an army."),
  overlord={"army_starting_experience_add": 5}, planet={"army_defense_damage_mult": 0.15})
h("sabotage_school", "army", 2, ("Школа диверсантов", "Готовит подрывников для сети."), ("Saboteur School", "Trains demolition experts for the network."),
  overlord={"spy_network_levels_add": 2, "army_damage_mult": 0.01})
h("partisan_hq", "army", 3, ("Партизанский штаб ячейки", "Координирует оборону и диверсии."), ("Cell Partisan HQ", "Coordinates defence and sabotage."),
  overlord={"spy_network_levels_add": 2, U: 2}, planet={"army_defense_damage_mult": 0.25, LOY: 0.5}, upkeep={"energy": 4})
h("liberation_school", "army", 3, ("Школа освобождения", "Готовит инструкторов для восстаний за рубежом."), ("Liberation School", "Trains instructors for uprisings abroad."),
  overlord={"spy_network_daily_value_mult": 0.03}, unique=True)

assert len(H) == 100, len(H)
assert len({x["key"] for x in H}) == 100

TECH = {1: None, 2: "tech_ps_guerrilla_doctrine", 3: "tech_ps_ghost_networks"}
COST = {1: 300, 2: 500, 3: 800}
UPKEEP = {1: 2, 2: 3, 3: 4}
TIME = {1: "@b1_time", 2: "@b2_time", 3: "@b2_time"}


def g(v):
    return f"{v:g}"


def holding(x):
    k = f"holding_ps_{x['key']}"
    o = [f"{k} = {{\n\tbase_buildtime = {TIME[x['tier']]}\n\towner_type = subject_holding\n"]
    o.append("\tempire_limit = 1\n" if x["unique"] else "\tplanet_limit = 1\n")
    o.append(f"\n\tcategory = {x['cat']}\n")
    o.append("\n\tpotential = {\n\t\thas_overlord_dlc = yes\n\t\texists = owner\n\t\towner = {\n\t\t\tis_wilderness_empire = no\n"
             "\t\t\toverlord = { ps_is_shadow_overlord = yes }\n\t\t}\n\t}\n")
    allow = []
    if TECH[x["tier"]]:
        allow.append(f"\t\tcustom_tooltip = {{\n\t\t\tfail_text = ps_holding_requires_{TECH[x['tier']]}\n"
                     f"\t\t\towner.overlord = {{ has_technology = {TECH[x['tier']]} }}\n\t\t}}\n")
    if x["spec"]:
        allow.append(f"\t\tcustom_tooltip = {{\n\t\t\tfail_text = ps_holding_requires_{x['spec']}\n\t\t\texists = planet.owner\n"
                     f"\t\t\tplanet.owner = {{ any_agreement = {{ agreement_preset = preset_{x['spec']} }} }}\n\t\t}}\n")
    if allow:
        o.append("\n\tallow = {\n" + "".join(allow) + "\t}\n")
    if x["spec"]:
        o.append(f"\n\tdestroy_trigger = {{\n\t\texists = planet.owner\n\t\tplanet.owner = {{\n\t\t\tNOT = {{ any_agreement = {{ agreement_preset = preset_{x['spec']} }} }}\n\t\t}}\n\t}}\n")
    up = x["upkeep"] or {"energy": UPKEEP[x["tier"]]}
    o.append(f"\n\tresources = {{\n\t\tcategory = planet_holdings\n\t\tcost = {{\n\t\t\tminerals = {COST[x['tier']]}\n\t\t}}\n\t\tupkeep = {{\n"
             + "".join(f"\t\t\t{r} = {g(v)}\n" for r, v in up.items()) + "\t\t}\n\t}\n")
    if x["planet"]:
        o.append("\n\tplanet_modifier = {\n" + "".join(f"\t\t{m} = {g(v)}\n" for m, v in x["planet"].items()) + "\t}\n")
    if x["overlord"]:
        o.append("\n\tcountry_modifier = {\n" + "".join(f"\t\t{m} = {g(v)}\n" for m, v in x["overlord"].items()) + "\t}\n")
    if x["job"]:
        reg, drone = JOB[x["job"]]
        for jobkey, gest in ((reg, "no"), (drone, "yes")):
            o.append(f"\n\ttriggered_planet_modifier = {{\n\t\tpotential = {{\n\t\t\texists = planet.owner\n\t\t\tplanet.owner = {{ is_gestalt = {gest} }}\n"
                     f"\t\t}}\n\t\t{jobkey} = {x['jobs']}\n\t}}\n")
    o.append("}\n")
    return "".join(o)


CAT_RU = {"army": "оборона", "government": "разведка/спец.", "trade": "деньги", "resource": "ресурсы", "research": "наука",
          "unity": "лояльность", "amenity": "помощь вассалу"}


def main():
    hdr = ("# АВТОГЕНЕРАЦИЯ: tools/gen_holdings.py — правьте генератор, а не этот файл\n"
           "# Синдикат Сопротивления — 100 владений («ячеек») на планетах вассалов\n\n")
    (ROOT / "common/buildings/ps_cell_holdings.txt").write_text(hdr + "\n".join(holding(x) for x in H), encoding="utf-8")
    gfx = ["spriteTypes = {"] + [
        f'\tspriteType = {{\n\t\tname = "GFX_holding_ps_{x["key"]}"\n\t\ttexturefile = "gfx/interface/icons/buildings/holding_ps_{x["key"]}.dds"\n\t}}'
        for x in H] + ["}\n"]
    (ROOT / "interface/ps_holdings.gfx").write_text("\n".join(gfx), encoding="utf-8")

    specs = {s[0]: (s[1], s[2]) for s in SPEC}
    for lang in ("russian", "english"):
        ru = lang == "russian"
        L = [f"l_{lang}:"]
        for x in H:
            name, desc = x["ru"] if ru else x["en"]
            L += [f' holding_ps_{x["key"]}:0 "{name}"', f' holding_ps_{x["key"]}_desc:0 "{desc}"']
        for t in ("tech_ps_guerrilla_doctrine", "tech_ps_ghost_networks"):
            L.append(f' ps_holding_requires_{t}:0 "' + ("Сюзерену нужна технология" if ru else "The overlord needs the technology") + f' §Y${t}$§!."')
        for s, (sru, sen) in specs.items():
            L.append(f' ps_holding_requires_{s}:0 "' + (f"Вассал должен быть специалистом «{sru}»." if ru else f"The subject must be a «{sen}» specialist.") + '"')
        (ROOT / f"localisation/{lang}/ps_holdings_l_{lang}.yml").write_bytes(b"\xef\xbb\xbf" + ("\n".join(L) + "\n").encode())

    try:
        from build_assets import icon, save_dds
        from PIL import ImageDraw
    except ImportError:
        print("Pillow не найден — иконки не созданы")
        return
    kind = {"army": "star", "government": "eye", "trade": "crown", "resource": "tree", "research": "net", "unity": "press", "amenity": "tree"}
    col = {1: (120, 200, 120, 255), 2: (220, 180, 60, 255), 3: (220, 60, 60, 255)}
    for x in H:
        img = icon(kind[x["cat"]], 64)
        d = ImageDraw.Draw(img)
        for j in range(x["tier"]):
            d.ellipse([8 + j * 10, 50, 15 + j * 10, 57], fill=col[x["tier"]])
        if x["spec"]:
            d.rectangle([48, 6, 58, 16], fill=(150, 90, 200, 255))
        save_dds(img, f"gfx/interface/icons/buildings/holding_ps_{x['key']}.dds")
    from collections import Counter
    print("ok:", len(H), "holdings;", dict(Counter(CAT_RU[x["cat"]] for x in H)))


if __name__ == "__main__":
    main()
