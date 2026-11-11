#my_piquant_megastructure = {
#	entity = "bawling_pink_rainbow_graphics"
#	construction_entity = "bawling_pink_rainbow_graphics_construction"
#	construction_scale = 1.02       # default: 1.0. Changes the size of construction_entity.
#	portrait = "GFX_my_piquant_megastructure_background"
#	order_icon = "GFX_fleet_order_button_build_starbase_station"	# If specified, fleets that can potentially build the megastructure will have a separate order button with this icon.
#																	# The icon should also have a version with the "_selected" suffix.
#																	# Only shown for ships that can build megastructures via construction_capabilities, not scripted actions.
#																	# Not currently supported for megastructures with must_select_ship_design = yes.
#	hide_name = yes / no			# default: no. Replaces the megastructure name on the system view nameplate with "NAMEPLATE_EMPTY_STRING"
#	upgrade_desc = default|hide		# default: 'default'. Use 'hide' to hide to hide this stage from the upgrade list.
#	upgrade_from = {
#		my_flamboyant_megastructure
#	}
#	prerequisites = { "tech" }		# required technologies
#	potential = {}					# trigger, scope: country, from: fleet for new megastructures and megastructure for upgrades
#	possible = {}					# trigger, scope: galactic object, from: country, fromfrom: fleet for new megastructures and megastructure for upgrades
#	context_menu_potential = {}		# trigger, scope: galactic object, from: country, fromfrom: fleet
#									# If true, fleets that can potentially build the megastructure will show a separate option for it in the system right-click context menu. If this is not specified, the option is never shown.
#									# Not currently supported for megastructures with build_type = around_planet or must_select_ship_design = yes.
#	dismantle_potential = {}		# trigger, scope: megastructure instance, from: country. Used to check if the button should even appear
#	dismantle_possible = {}			# trigger, scope: megastructure instance, from: country. Used to check if the button should be greyed out
#	should_ai_dismantle = {}		# trigger, scope: megastructure instance, from: country. Used to check if an AI wants to dismantle this megastructure. Returns false by default.
#	build_time = 5					# days
#	dismantle_time = 5				# days; how many days it takes to dismantle
#	can_be_dismantled_by_non_owner = yes/no	# default: no. Allows dismantling of megastructures owned by other empires (dismantle effects' country scopes will be set to the dismantling country, not necessarily the megastructure owner)
#	can_prevent_crisis_terraformation = yes/no	# default: no. Prevents crisis terraformation of the star this megastructure is orbiting.
#	victory_score = 1000			# Victory score for the player who owns that megastructure
#	dismantle_cost = {
#		minerals = 8
#		energy = 13
#		influence = 21
#	}
#	resources = {
#		category = megastructures
#		cost = {}					# trigger, scope: country. Paid when building or upgrading to this stage.
#		produces = {}				# trigger, scope: country. Monthly output once the stage is finished.
#		upkeep = {}					# trigger, scope: country. Monthly cost once the stage is finished.
#	}								# Repeat cost, produces or upkeep to add a block that only applies when its trigger passes.
#	country_modifier = {}
#	system_modifier = {}				# applies to everything in the solar system, like a starbase system modifier
#	custom_tooltip = LOC_KEY			# replaces the whole modifier block wherever this megastructure lists its effects,
#										# so a type can write its own "Effects:" line instead of the Empire, System and
#										# Megastructure sections. Suppresses triggered_country_modifier text too, and
#										# takes priority over custom_tooltip_with_modifiers.
#	custom_tooltip_with_modifiers = LOC_KEY	# as above, but prepended to the modifier block rather than replacing it.
#										# Prefer this over custom_tooltip when the megastructure has, or may gain, modifiers
#										# worth showing, since custom_tooltip hides them. A megastructure that previously
#										# carried its description as a custom_tooltip inside a modifier block can move that
#										# key up to here, but the loc then needs its own header, $EFFECTS$ or similar, because
#										# the section headings no longer apply to it.
#										# Both keys resolve on a megastructure scope.
#	triggered_country_modifier = {
#		potential = {}
#	}
#
#	placement_rules = {
#		planet_possible = {}		# trigger, scope: planet
#	}
#
#	on_build_start = {}				# effects, scope: galactic object, from: country,
									# fromfrom: megastructure instance (when upgrading existing megastructure)
#	on_build_cancel = {}			# effects, scope: galactic object, from: country
#	on_build_complete = {}			# effects, scope: galactic object, from: country,
									# fromfrom: megastructure instance, fromfromfrom: constructing fleet
									# prev: starbase (if the megastructure spawns a starbase)
#
#	on_dismantle_start = {}			# effects, scope: galactic object, from: country, fromfrom: megastructure instance
#	on_dismantle_cancel = {}		# effects, scope: galactic object, from: country, fromfrom: megastructure instance
#	on_dismantle_complete = {}		# effects, scope: galactic object, from: country
#
#	starbase = level_type			# AI will use this starbase level type to evaluate economical value
									# this starbase type will also be built automatically when the megastructure is finished
#	ai_weight = {					# scope = country, default = 100
#		modifier = {
#			weight = 0
#			NOT = {
#				has_ethic = ethic_militarist
#			}
#		}
#	}
#
#	construction_blocks_and_blocked_by = none # default multi_stage_type,	#use none				if construction can not block and can not be blocked by any constructions,
#																			#use self_type			if construction blocks and blocked by same type of constructions,
#																			#use multi_stage_type	if construction blocks and blocked by multi-stage constructions
#	custom_tooltip_requirements = LOC_KEY	# custom loc to show in the build requirements. The loc can optionally include a MEGASTRUCTURE variable for the name of the megastructure
#	build_system_tooltip = habitat_tooltip	# tooltip from common/system_tooltips that will be shown when selecting a location to build the megastructure
#
#	# Best systems tooltip - shows a ranked list of candidate systems in the megastructure selection UI tooltip.
#	# The number of systems shown is controlled by MEGASTRUCTURE_TOOLTIP_BEST_SYSTEMS_COUNT (default 10).
#	tooltip_best_systems_header = LOC_KEY	# loc key for the header shown above the list (e.g. "§ESystems with highest potential:§!")
#	tooltip_system_filter = {}				# trigger block, scope: galactic object, from: country. Systems that fail this trigger are excluded from the list entirely.
#											# Use this to filter out systems that are fundamentally ineligible (e.g. already have this megastructure).
#											# Prefer this over repeating the full possible = {} block, which includes infrastructure checks unsuitable for ranking.
#	tooltip_system_score = {				# MTTH-style block, scope: galactic object, from: country. Higher score = higher rank. Mutually exclusive with tooltip_show_star_resources.
#		base = 0
#		add = value:some_scripted_value
#	}
#	tooltip_system_score_low_threshold = 5	# optional: systems scoring at or below this value are shown in red
#	tooltip_system_score_high_threshold = 10# optional: systems scoring at or above this value are shown in green; between thresholds is yellow
#	tooltip_show_star_resources = yes		# alternative to tooltip_system_score: ranks systems by the star's total deposit value
#											# (weighted by culling conversion values) and displays resource icons showing the raw/base
#											# output (ignoring modifiers) instead of a numeric score.
#											# When there are more candidates than can be shown, the top
#											# MEGASTRUCTURE_TOOLTIP_BEST_SYSTEMS_PER_RESOURCE_COUNT (default 4) systems for each resource type
#											# are guaranteed a slot before the remaining slots are filled by score, so a resource type with many
#											# high-value stars can't crowd the others out of the list.
#
#	# Overclocking
#	overclock_types = {						# modes from common/megastructure_overclock_types. The Overclocking tab only appears
#		my_mode_a							# when at least one of them passes its potential. Whenever no mode is stored, on
#		my_mode_b							# creation and on reset, the mode with the highest flat ai_weight is selected, so state
#	}									# the default there rather than relying on the order of this list.
#	overclock_cooldown = 720				# optional, default 0. Days the megastructure is locked out of switching mode after a
#											# switch, shared by every mode rather than tracked per mode. Accepts a plain number,
#											# an @scripted_variable, or value:my_script_value / trigger: / modifier: / var: forms,
#											# evaluated in megastructure scope.
#											# The player path is blocked while it runs, and the mode button says how many days are
#											# left. set_overclock ignores it and still starts it, so a scripted mode change always
#											# lands; pass cooldown = no there to change mode without starting one.
#											# Script can test the state with has_overclock_cooldown = yes/no, megastructure scope.
#	overclock_loc_key = SMELTING			# optional. Renames the word "Overclocking" throughout the tab for this megastructure
#											# only, so an Arc Furnace can talk about Smelting instead. The key is substituted into
#											# each of the seven strings below.
#											#
#											# Every string is looked up individually, and any key that is not localized falls back
#											# to the shared one, so a megastructure can rename only the strings it cares about.
#											# Omitting overclock_loc_key entirely uses the shared string everywhere.
#											#
#											#   composed key (SMELTING)					shared fallback									where it appears
#											#   MEGASTRUCTURE_SMELTING_TAB				MEGASTRUCTURE_OVERCLOCKING_TAB					tab button
#											#   MEGASTRUCTURE_SMELTING_DESC				MEGASTRUCTURE_OVERCLOCKING_DESC					blurb along the bottom of the tab
#											#   MEGASTRUCTURE_NO_SMELTING				MEGASTRUCTURE_NO_OVERCLOCKING					header while no mode is active
#											#   MEGASTRUCTURE_SMELTING_ENABLED			MEGASTRUCTURE_OVERCLOCKING_ENABLED				on the mode that is already active
#											#   MEGASTRUCTURE_CLICK_TO_ENABLE_SMELTING	MEGASTRUCTURE_CLICK_TO_ENABLE_OVERCLOCK			mode button call to action
#											#   MEGASTRUCTURE_TOOLTIP_SMELTING_COST_HEADER	MEGASTRUCTURE_TOOLTIP_OVERCLOCK_COST_HEADER	mode button cost header
#											#   MEGASTRUCTURE_SMELTING_TOOLTIP_DESC		MEGASTRUCTURE_OVERCLOCK_TOOLTIP_DESC			mode button flavor styling
#
#	is_ruined_orbital_ring = yes			# default = no
#	scales_with_planet = yes				# default = no
#	use_planet_resource = yes			    # default = no; decides if the megastructure will mine the underlying resources if its on top of a planet/star
#	build_outside_gravity_well = no 		# deprecated, default = no, decides if the megastructure should be built outside the gravity well instead of around a planet
#	build_type = inside_gravity_well/outside_gravity_well/around_planet # default = around_planet, decided how and where the MS is built
#	must_select_ship_design = yes/no		# default = no, means the mega structure should offer a choice of design when becoming a starbase (only applies to megastructure that become starbases )
#   show_in_outliner = no                   # default = yes
#   outliner_trigger = {}                   # an extra trigger to allow scripted reasons to hide the megastructure. if defined both show_in_outliner and this trigger need to be true for the megastructure to show in the outliner. scope: megastructure
#   build_menu_potential = {}               # trigger, scope: fleet, from: country
#                                           # Use for megastructures that have their own dedicated context_menu_potential shortcut and order_icon, so the general picker is redundant.
#}
