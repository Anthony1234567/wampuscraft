# demo.py

from pprint import pprint

from wompuscraft_wrapper import WompusCraftExpertSystem

if __name__ == "__main__":
    es = WompusCraftExpertSystem("wompuscraft.pl")

    print("=== Default objective order ===")
    pprint(es.default_objectives())

    print("\n=== Next objective & missing items ===")
    next_obj = es.next_objective("steve")
    pprint(next_obj)

    print("\n=== Global recommendation with hints ===")
    rec = es.recommend_next_action_overall_with_hints("steve")
    pprint(rec)

    print("\n=== Single-objective drill-down (get_stone_tools) ===")
    stone_tools = es.recommend_for_objective("steve", "get_stone_tools")
    pprint(stone_tools)

    print("\n=== Missing items for reach_nether ===")
    missing_nether = es.missing_items("steve", "reach_nether")
    pprint(missing_nether)
