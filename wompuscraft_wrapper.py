# wompuscraft_wrapper.py

from typing import Any, Dict, List, Union
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
            # Support both pyswip Structure (has .value) and already-string forms.
            qty_term: Union[str, int, Any]
            item_term: Any

            if hasattr(pair, "value"):
                qty_term, item_term = pair.value  # type: ignore[attr-defined]
            elif isinstance(pair, (list, tuple)) and len(pair) == 2:
                qty_term, item_term = pair
            elif isinstance(pair, str) and "-" in pair:
                qty_part, item_part = pair.split("-", 1)
                qty_term, item_term = qty_part, item_part
            else:
                # Fallback: try to treat as two-element sequence-like
                try:
                    qty_term, item_term = pair[0], pair[1]  # type: ignore[index]
                except Exception as exc:  # pragma: no cover - defensive path
                    # Last resort: try regex on the string form "3-wood_log"
                    import re

                    m = re.match(r"\s*(-?\d+)\s*-\s*([A-Za-z0-9_]+)", str(pair))
                    if m:
                        qty_term, item_term = m.group(1), m.group(2)
                    else:
                        raise ValueError(
                            f"Unrecognized NeededRaw term (cannot parse qty-item): {pair}"
                        ) from exc

            qty_str = str(qty_term).strip()
            item_str = str(item_term).strip() if item_term is not None else ""

            if qty_str == "" or item_str == "":
                # Try parsing both sides from the whole pair string
                import re

                m = re.match(r"\s*(-?\d+)\s*-\s*([A-Za-z0-9_]+)", str(pair))
                if m:
                    if qty_str == "":
                        qty_str = m.group(1)
                    if item_str == "":
                        item_str = m.group(2)

            # If still empty qty, assume 1 (defensive; Prolog should provide a number)
            if qty_str == "":
                qty_str = "1"

            qty = int(qty_str)
            item = item_str if item_str else str(item_term)
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