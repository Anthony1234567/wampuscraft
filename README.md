# wampuscraft

Minecraft Opinionated Speedrun Plugin

### Setup

- Install SWI-Prolog first: `brew install swi-prolog`
- Install Python deps: `pip install -r requirements.txt`
- Run the demo: `python demo.py`

Once you have all of the necessary prereqs, validate the knowledge base

```sh
$ swipl
```

Once the prolog cli is open, paste the following

```prolog
?- [wompuscraft].

% What’s the next objective and what am I missing?
?- next_objective(steve, Obj, Missing).
Obj = survive_first_night,
Missing = [wooden_pickaxe, stone_pickaxe, furnace, bed, shield, torch].

% For that objective, what should I build and what raw do I need?
?- recommend_next_action_overall(steve, Obj, Item, Needs).
Obj   = survive_first_night,
Item  = wooden_pickaxe,
Needs = RawList.   % expanded list of qty-raw materials

% With hints
?- recommend_next_action_overall_with_hint(steve, Obj, Item, Needs, Hints).
```
