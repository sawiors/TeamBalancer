from __future__ import annotations

from core.input_types import RecruitRow, StandardRow
from core.models import Player
from games.lol_solver import solve_lol_fixed, solve_lol_recruit
from games.valorant_solver import solve_recruit, solve_selected_ten


def collect_standard_players(
    rows: list[StandardRow],
    *,
    position_placeholder: str,
) -> tuple[list[Player], str | None]:
    players: list[Player] = []

    for idx, row in enumerate(rows):
        name = str(row.get("name", "")).strip()
        tier = str(row.get("tier", "")).strip()
        position = str(row.get("position", "")).strip()
        score = int(row.get("score", 0))
        pair_index = int(row.get("pair_index", idx // 2))

        if not name or not tier or not position or position == position_placeholder:
            return [], "10명을 모두 입력하세요."

        players.append(
            Player(
                pid=idx,
                name=name,
                tier=tier,
                score=score,
                position=position,
                confirmed=True,
                pair_index=pair_index,
            )
        )

    return players, None


def collect_recruit_completed_players(
    rows: list[RecruitRow],
    *,
    position_placeholder: str,
) -> list[Player]:
    players: list[Player] = []

    for idx, row in enumerate(rows):
        name = str(row.get("name", "")).strip()
        position = str(row.get("position", "")).strip()
        tier = str(row.get("tier", "")).strip()
        score = int(row.get("score", 0))
        confirmed = bool(row.get("confirmed", False))

        if not name or not position or position == position_placeholder or not tier:
            continue

        players.append(
            Player(
                pid=idx,
                name=name,
                tier=tier,
                score=score,
                position=position,
                confirmed=confirmed,
            )
        )

    return players


def calculate_standard_solution(
    *,
    game: str,
    players: list[Player],
    valorant_no_triple: bool,
) -> dict:
    if game == "lol":
        solution = solve_lol_fixed(players)
        if solution is None:
            return {"status": "invalid", "message": "조건을 만족하는 팀 구성을 찾지 못했습니다."}
        return {"status": "ok", "solution": solution}

    best = solve_selected_ten(players, no_triple=valorant_no_triple)
    if best is None:
        return {"status": "invalid", "message": "조건을 만족하는 팀 구성을 찾지 못했습니다."}
    return {"status": "ok", "solution": best}


def calculate_recruit_solutions(
    *,
    game: str,
    players: list[Player],
    lol_positions: list[str],
    valorant_no_triple: bool,
    max_solutions: int,
) -> dict:
    if game == "lol":
        result = solve_lol_recruit(players, positions=lol_positions, return_all=True)
    else:
        result = solve_recruit(players, no_triple=valorant_no_triple, return_all=True)

    if result["status"] != "ok":
        return {"status": "invalid", "message": result["message"], "solutions": []}

    return {
        "status": "ok",
        "solutions": list(result["solutions"][:max_solutions]),
        "message": "",
    }
