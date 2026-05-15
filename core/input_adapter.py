from __future__ import annotations

from typing import Any, Callable

from core.input_types import RecruitRow, StandardRow


def extract_standard_rows(app: Any, *, tier_to_score: Callable[[str], int]) -> list[StandardRow]:
    rows: list[StandardRow] = []

    for player_input in app.standard_inputs:
        tier = player_input["tier_combo"].get().strip()
        position_combo = player_input["position_combo"]
        if position_combo is None:
            position = player_input["default_position"]
        else:
            position = position_combo.get().strip()

        rows.append(
            {
                "name": player_input["name_entry"].get().strip(),
                "tier": tier,
                "score": tier_to_score(tier) if tier else 0,
                "position": position,
                "pair_index": player_input["pair_index"],
            }
        )

    return rows


def extract_recruit_rows(app: Any, *, tier_to_score: Callable[[str], int]) -> list[RecruitRow]:
    rows: list[RecruitRow] = []

    for player_input in app.recruit_inputs:
        tier = player_input["tier_combo"].get().strip()
        rows.append(
            {
                "name": player_input["name_entry"].get().strip(),
                "position": player_input["position_combo"].get().strip(),
                "tier": tier,
                "score": tier_to_score(tier) if tier else 0,
                "confirmed": bool(player_input["confirmed"]),
            }
        )

    return rows
