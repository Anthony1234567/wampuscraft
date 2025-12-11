/**************************************
 * WompusCraft Expert System (POC)
 * Knowledge base + multi-objective reasoning
 **************************************/

%%%%%%%%%%%%%
%% RAW ITEMS
%%%%%%%%%%%%%

% Items that are considered raw / directly mineable or lootable.
raw(wood_log).
raw(cobblestone).
raw(iron_ore).
raw(coal).
raw(flint).
raw(water_source).
raw(lava_source).
raw(wool).
raw(gravel).

%%%%%%%%%%%%%%%%
%% CRAFTING RULES
%%%%%%%%%%%%%%%%

% recipe(ResultItem, [qty(Sub1)-SubItem1, qty(Sub2)-SubItem2, ...])

recipe(planks, [1-wood_log]).         % 1 log -> 4 planks (abstracted)
recipe(stick, [2-planks]).

recipe(crafting_table, [4-planks]).

recipe(wooden_pickaxe, [
    3-planks,
    2-stick
]).

recipe(stone_pickaxe, [
    3-cobblestone,
    2-stick
]).

recipe(furnace, [
    8-cobblestone
]).

recipe(iron_ingot, [
    1-iron_ore,
    1-coal
]).

recipe(iron_pickaxe, [
    3-iron_ingot,
    2-stick
]).

recipe(bucket, [
    3-iron_ingot
]).

recipe(flint_and_steel, [
    1-flint,
    1-iron_ingot
]).

recipe(iron_sword, [
    2-iron_ingot,
    1-stick
]).

recipe(shield, [
    1-iron_ingot,
    6-planks
]).

recipe(bed, [
    3-wool,
    3-planks
]).

recipe(torch, [
    1-coal,
    1-stick
]).

%%%%%%%%%%%%%%%%%%%%%%%%
%% MINING CAPABILITIES
%%%%%%%%%%%%%%%%%%%%%%%%

% What block types each pickaxe can mine.
can_mine_with(wooden_pickaxe, cobblestone).
can_mine_with(stone_pickaxe, cobblestone).
can_mine_with(stone_pickaxe, iron_ore).
can_mine_with(iron_pickaxe, cobblestone).
can_mine_with(iron_pickaxe, iron_ore).

%%%%%%%%%%%%%%%%%
%% PLAYER STATE
%%%%%%%%%%%%%%%%%

% has(Player, Item, Count).
% Example starting inventory; update via assert/retract in a real system.

has(steve, wood_log, 4).
has(steve, cobblestone, 0).
has(steve, iron_ore, 0).
has(steve, coal, 0).
has(steve, stick, 0).
has(steve, planks, 0).
has(steve, crafting_table, 0).
has(steve, wooden_pickaxe, 0).
has(steve, stone_pickaxe, 0).
has(steve, furnace, 0).
has(steve, iron_ingot, 0).
has(steve, iron_pickaxe, 0).
has(steve, bucket, 0).
has(steve, flint_and_steel, 0).
has(steve, iron_sword, 0).
has(steve, shield, 0).
has(steve, bed, 0).
has(steve, torch, 0).
has(steve, wool, 0).
has(steve, flint, 0).
has(steve, gravel, 0).
has(steve, water_source, 0).
has(steve, lava_source, 0).

% Simple positional predicates for POC.
at_biome(steve, plains).
at_y_level(steve, 70).    % roughly surface
at_dimension(steve, overworld).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% OBJECTIVES AND REQUIREMENTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% objective(Name, RequiredItems).

% First night survival: tools, light, bed, basic defense.
objective(survive_first_night, [
    wooden_pickaxe,
    stone_pickaxe,
    furnace,
    bed,
    shield,
    torch
]).

% Basic stone tool progression (subset of survival path).
objective(get_stone_tools, [
    stone_pickaxe,
    furnace
]).

% Get basic iron gear.
objective(get_iron_gear, [
    furnace,
    iron_pickaxe,
    iron_sword,
    shield,
    bucket
]).

% Get Nether-ready toolkit.
objective(reach_nether, [
    iron_pickaxe,
    furnace,
    bucket,
    flint_and_steel
]).

% Default objective order toward “beat the game”.
default_objective_order([
    survive_first_night,
    get_stone_tools,
    get_iron_gear,
    reach_nether
]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% INVENTORY / COUNT HELPERS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% get_count(+Player, +Item, -Count)
get_count(Player, Item, Count) :-
    has(Player, Item, Count), !.
get_count(_, _, 0).

% has_at_least(+Player, +Item, +NeededQty)
has_at_least(Player, Item, NeededQty) :-
    get_count(Player, Item, Have),
    Have >= NeededQty.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MISSING ITEMS FOR OBJECTIVE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% missing_items(+Player, +ObjectiveName, -MissingList)
missing_items(Player, ObjectiveName, MissingList) :-
    objective(ObjectiveName, RequiredItems),
    include(is_missing(Player), RequiredItems, MissingList).

is_missing(Player, Item) :-
    get_count(Player, Item, C),
    C =< 0.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% RESOURCE BREAKDOWN
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% needed_raw_for_item(+Item, -RawNeedsList)
% Return list of qty(Item) pairs for RAW materials required to craft Item.

needed_raw_for_item(Item, Needs) :-
    recipe(Item, Components),
    !,
    needed_raw_for_components(Components, Needs).
needed_raw_for_item(Item, [1-Item]) :-
    % If there's no recipe, treat it as raw (or externally obtained).
    raw(Item).

needed_raw_for_components([], []).
needed_raw_for_components([Qty-SubItem | Rest], NeedsOut) :-
    needed_raw_for_item(SubItem, SubNeeds),
    scale_needs(Qty, SubNeeds, ScaledSubNeeds),
    needed_raw_for_components(Rest, RestNeeds),
    merge_needs(ScaledSubNeeds, RestNeeds, NeedsOut).

% Multiply all quantities by factor.
scale_needs(_, [], []).
scale_needs(Factor, [Qty-Item | Rest], [Scaled-Item | ScaledRest]) :-
    Scaled is Factor * Qty,
    scale_needs(Factor, Rest, ScaledRest).

% Merge two lists of qty-Item, summing quantities for same Item.
merge_needs([], L, L).
merge_needs([Qty-Item | Rest], L2, Out) :-
    add_need(Qty, Item, L2, L2New),
    merge_needs(Rest, L2New, Out).

add_need(Qty, Item, [], [Qty-Item]).
add_need(Qty, Item, [ExistingQty-Item | Rest], [NewQty-Item | Rest]) :-
    NewQty is ExistingQty + Qty.
add_need(Qty, Item, [OtherQty-OtherItem | Rest], [OtherQty-OtherItem | RestOut]) :-
    Item \= OtherItem,
    add_need(Qty, Item, Rest, RestOut).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PER-OBJECTIVE NEXT ACTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% choose_next_item(+Player, +ObjectiveName, -ItemToBuild)
% Very simple strategy: pick the first missing item for the objective.
choose_next_item(Player, ObjectiveName, ItemToBuild) :-
    missing_items(Player, ObjectiveName, [ItemToBuild | _]).

% recommend_next_action(+Player, +ObjectiveName, -ItemToBuild, -NeededRaw)
recommend_next_action(Player, ObjectiveName, ItemToBuild, NeededRaw) :-
    choose_next_item(Player, ObjectiveName, ItemToBuild),
    needed_raw_for_item(ItemToBuild, NeededRaw).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% POSITION / SEED-BASED HINTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% where_to_get(+Item, -Hint)
where_to_get(iron_ore, mine_at_y(16)).
where_to_get(cobblestone, mine_near_surface).
where_to_get(wood_log, chop_nearby_trees).
where_to_get(flint, mine_gravel_or_trade).
where_to_get(coal, mine_surface_coal_or_caves).
where_to_get(wool, shear_or_kill_sheep).
where_to_get(water_source, scoop_any_surface_water).
where_to_get(lava_source, check_seed_lava_pool).
where_to_get(gravel, dig_near_rivers_or_beaches).

% combine recommendation with location hint for a single objective
recommend_next_action_with_hint(Player, Objective, Item, NeededRaw, Hints) :-
    recommend_next_action(Player, Objective, Item, NeededRaw),
    findall(Hint,
            (member(_Qty-RawItem, NeededRaw),
             where_to_get(RawItem, Hint)),
            Hints).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MULTI-OBJECTIVE ORDERING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% next_objective_from_list(+Player, +Objectives, -Objective, -MissingItems)
% Scan objectives in order; pick first with any missing items.

next_objective_from_list(Player, [Obj | _], Obj, Missing) :-
    missing_items(Player, Obj, Missing),
    Missing \= [],
    !.
next_objective_from_list(Player, [_ | Rest], Obj, Missing) :-
    next_objective_from_list(Player, Rest, Obj, Missing).

% next_objective(+Player, -Objective, -MissingItems)
% Uses default_objective_order/1.

next_objective(Player, Objective, Missing) :-
    default_objective_order(Objs),
    next_objective_from_list(Player, Objs, Objective, Missing).

% Global “what should I do next?” for the whole game plan.
% recommend_next_action_overall(+Player, -Objective, -ItemToBuild, -NeededRaw)

recommend_next_action_overall(Player, Objective, ItemToBuild, NeededRaw) :-
    next_objective(Player, Objective, _Missing),
    recommend_next_action(Player, Objective, ItemToBuild, NeededRaw).

% Global version with hints
recommend_next_action_overall_with_hint(Player, Objective, ItemToBuild, NeededRaw, Hints) :-
    recommend_next_action_overall(Player, Objective, ItemToBuild, NeededRaw),
    findall(Hint,
            (member(_Qty-RawItem, NeededRaw),
             where_to_get(RawItem, Hint)),
            Hints).