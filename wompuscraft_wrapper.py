# wompuscraft_wrapper.py

from typing import Any, Dict, List
from pyswip import Prolog


class WompusCraftExpertSystem:
    """
    Thin Python wrapper around the wompuscraft.pl Prolog knowledge base.
    """

    def __init__(self, prolog_file: str = "wompuscraft.pl") -> None:
        self.prolog = Prolog()
        self.prolog.consult(prolog_file)

    def _convert_needed_raw(self, needed_raw_term: Any) -> List[Dict[str, Any]]:
        """
        Convert a Prolog list like [3-wood_log, 2-stick] into
        [{'item': 'wood_log', 'qty': 3}, ...]
        """
        result: List[Dict[str, Any]] = []
        for pair in needed_raw_term:
            # pair is a Prolog structure representing Qty-Item
            qty = int(pair.value[0])    # left side
            item = str(pair.value[1])   # right side
            result.append({"item": item, "qty": qty})
        return result

    def _convert_hints(self, hints_term: Any) -> List[str]:
        """
        Convert Prolog hint list (e.g. [mine_near_surface, chop_nearby_trees])
        to a list of strings.
        """
        return [str(h) for h in hints_term]

    def recommend_next_action_overall(self, player: str) -> Dict[str, Any]:
        """
        Ask Prolog: given this player and the default objective order,
        what is the next objective, what item should they craft, and
        what raw resources are required?
        """
        query = (
            f"recommend_next_action_overall({player}, Objective, Item, NeededRaw)"
        )
        solutions = list(self.prolog.query(query, maxresult=1))

        if not solutions:
            return {
                "objective": None,
                "item": None,
                "needed_raw": [],
            }

        sol = solutions[0]
        objective = str(sol["Objective"])
        item = str(sol["Item"])
        needed_raw = self._convert_needed_raw(sol["NeededRaw"])

        return {
            "objective": objective,
            "item": item,
            "needed_raw": needed_raw,
        }

    def recommend_next_action_overall_with_hints(self, player: str) -> Dict[str, Any]:
        """
        Same as above, but also returns hints about where to get each
        required raw material.
        """
        query = (
            f"recommend_next_action_overall_with_hint("
            f"{player}, Objective, Item, NeededRaw, Hints)"
        )
        solutions = list(self.prolog.query(query, maxresult=1))

        if not solutions:
            return {
                "objective": None,
                "item": None,
                "needed_raw": [],
                "hints": [],
            }

        sol = solutions[0]
        objective = str(sol["Objective"])
        item = str(sol["Item"])
        needed_raw = self._convert_needed_raw(sol["NeededRaw"])
        hints = self._convert_hints(sol["Hints"])

        return {
            "objective": objective,
            "item": item,
            "needed_raw": needed_raw,
            "hints": hints,
        }

    def recommend_for_objective(self, player: str, objective: str) -> Dict[str, Any]:
        """
        Ask for the next item specifically for a single objective
        (ignoring global ordering).
        """
        query = (
            f"recommend_next_action({player}, {objective}, Item, NeededRaw)"
        )
        solutions = list(self.prolog.query(query, maxresult=1))

        if not solutions:
            return {
                "objective": objective,
                "item": None,
                "needed_raw": [],
            }

        sol = solutions[0]
        item = str(sol["Item"])
        needed_raw = self._convert_needed_raw(sol["NeededRaw"])

        return {
            "objective": objective,
            "item": item,
            "needed_raw": needed_raw,
        }