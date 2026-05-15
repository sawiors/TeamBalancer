from __future__ import annotations

from typing import Any


def on_recruit_input_changed(app: Any, *, lol_positions: list[str], valorant_positions: list[str]) -> None:
    update_recruit_position_status(
        app,
        lol_positions=lol_positions,
        valorant_positions=valorant_positions,
    )


def update_recruit_position_status(app: Any, *, lol_positions: list[str], valorant_positions: list[str]) -> None:
    positions = lol_positions if app.current_game == "lol" else valorant_positions
    counts = {pos: 0 for pos in positions}

    for player in app._collect_recruit_completed_players():
        counts[player.position] += 1

    for position, label in app.recruit_position_labels.items():
        count = counts[position]
        label.configure(text=f"{position} {count}", text_color="#1f7a1f" if count >= 2 else "#d9534f")
