# Патчи совместимости

## vanilla_ui_waystation_patch
Нужен **только если вы играете БЕЗ UI Overhaul Dynamic (UIOD)** или другого мода интерфейса.

Синдикат даёт стоянкам партизан до 50 слотов модулей (модуль «Отсеки Синдиката»), а ванильное окно стоянки показывает модули по 3 в ряд без прокрутки. Патч переопределяет `interface/waystation_view.gui`: блок модулей получает прокрутку и 4 модуля в ряд.

**С UIOD патч НЕ ставьте:** в UIOD окно стоянки уже прокручивается (5 модулей в ряд), а патч заменил бы окно UIOD ванильным.

Ставится после основного мода. Архив: `releases/partisan_syndicate_vanilla_ui_patch.zip`.

## xhk_worldark_patch — интеграция с XHK World Ark
Нужен, если вы играете с модом **[4.5] XHK World Ark**. Ставится **после** «Синдиката» и XHK World Ark.

- Происхождение XHK **«Мировой ковчег»** у **мегакорпорации с «Криминальным наследием»** становится **партизанским ковчегом**: работают все механики «Ковчега Сопротивления» (пролог с доктриной ковчега, стоянки Сопротивления, высадка ячеек, вассалы-специалисты, 100 модулей стоянок, операции, бессмертные лидеры).
- Мировой ковчег сразу получает **специализации всех трёх ванильных ковчегов** — гражданского, научного и военного — на **максимальном 3-м уровне** (переменные XHK `xhk_worldark_<тип>_upgrade_level = 3`). Проверка повторяется ежегодно.

Архив: `releases/partisan_syndicate_xhk_worldark_patch.zip`.

## nomad_mega_patch — кочевники строят мегаструктуры Gigastructures и Halo
Это готовый патч: скрипты запускать не нужно. Ставится **последним**, после «Синдиката», **Gigastructural Engineering & More (4.5)** и **Halo: Forerunner Ships & Portraits**. Нужны оба этих мода.
- Сам «Синдикат» уже позволяет кочевникам строить **ванильные** мегаструктуры (встроенная статическая часть «Nomad Can Build Megastructures — Mod Compatible Edition»).
- Этот патч содержит копии 67 файлов мегаструктур (66 из Gigastructures, 1 из Halo) и 5 файлов технологий Gigastructures. В них проверка «система внутри границ» заменена ванильной `system_ownership_or_waystation_check` (владение системой **или** стоянка кочевника), а `is_nomadic = no` снят.
- Файлы созданы скриптом `tools/gen_nomad_mega_patch.py` (порт `NomadPatch.ps1` из Compatible Edition) для **Gigastructures 4.5** и **Halo 2.8**. После обновления этих модов патч нужно пересоздать: пришлите новые версии модов или запустите
  `python3 tools/gen_nomad_mega_patch.py <папка Gigastructures> <папка Halo>`.
  Устаревший патч может вернуть старые версии мегаструктур.
- Патч содержит код Gigastructures и Halo. Он предназначен для личной игры, публиковать его в мастерской без разрешения авторов этих модов нельзя.

Архив: `releases/partisan_syndicate_nomad_mega_patch.zip`.

## frameworld_goodies_patch — XHK Frameworld Extra Goodies в пакете «Синдиката»
Это мод **[4.5] XHK Frameworld Extra Goodies** (Workshop 3071450599), встроенный в наш пакет с разрешения автора, файлы не изменены. Он расширяет происхождение **Frameworld** из Gigastructures: новые районы и зоны, мегаструктуры на секциях, анклавы, перемещение секций (framewarp), Frameworld-Бёрч, дополнительные залежи и многое другое.
- Требует **Gigastructural Engineering & More (4.5)**. Отдельным модулем он сделан потому, что без Gigastructures игра выдаст сотни ошибок, а «Синдикат» должен работать и без Gigastructures.
- Ставится **вместо** оригинала, после Gigastructures. Оригинал из плейсета уберите.
- С XHK World Ark совместим: их общие файлы одинаковые.
- Переопределяет ванильные `building_cryovault`, `building_offworld_expedition_hub`, `decision_market_nomination`, правило `has_full_sensor_range`, триггер `is_wet` и два инлайн-скрипта Gigastructures (`giga_birch_manager_swap_*`), как и оригинал.
- Русская локализация в оригинале на английском, её можно перевести отдельно.

Архив: `releases/partisan_syndicate_frameworld_goodies_patch.zip`.
