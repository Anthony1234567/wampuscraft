# demo.py

from wompuscraft_wrapper import WompusCraftExpertSystem

if __name__ == "__main__":
    es = WompusCraftExpertSystem("wompuscraft.pl")

    # Overall suggestion: “What should I do next?”
    result = es.recommend_next_action_overall_with_hints("steve")
    print("Next recommendation:")
    print(result)
    # {
    #   'objective': 'survive_first_night',
    #   'item': 'wooden_pickaxe',
    #   'needed_raw': [{'item': 'wood_log', 'qty': ...}, ...],
    #   'hints': ['chop_nearby_trees', ...]
    # }

    # Or for a specific objective:
    stone_tools = es.recommend_for_objective("steve", "get_stone_tools")
    print("Stone tools plan:")
    print(stone_tools)