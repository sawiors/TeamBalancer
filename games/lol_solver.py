from __future__ import annotations

from itertools import combinations

from core.models import Player


def _variance(team: list[Player]) -> float:
    if not team:
        return 0.0
    mean = sum(p.score for p in team) / len(team)
    return sum((p.score - mean) ** 2 for p in team) / len(team)


def solve_lol_fixed(players: list[Player]) -> dict | None:
    pairs: list[list[Player]] = [[] for _ in range(5)]
    for p in players:
        pairs[p.pair_index].append(p)
    if any(len(pair) != 2 for pair in pairs):
        return None

    total = sum(p.score for p in players)
    target = total / 2
    best = None

    for mask in range(1 << 5):
        team_a, team_b = [], []
        for pi, pair_players in enumerate(pairs):
            sel = (mask >> pi) & 1
            team_a.append(pair_players[sel])
            team_b.append(pair_players[1 - sel])

        sum_a = sum(p.score for p in team_a)
        diff = abs(sum_a * 2 - total)
        sort_key = (
            diff,
            abs(sum_a - target),
            abs(_variance(team_a) - _variance(team_b)),
            tuple(sorted(p.name for p in team_a)),
        )
        candidate = {
            "team_a": team_a,
            "team_b": team_b,
            "sum_a": sum_a,
            "sum_b": total - sum_a,
            "diff": diff,
            "sort_key": sort_key,
        }
        if best is None or sort_key < best["sort_key"]:
            best = candidate

    return best


def solve_lol_selected_ten(players: list[Player], positions: list[str]) -> dict | None:
    by_pos: dict[str, list[Player]] = {pos: [] for pos in positions}
    for p in players:
        if p.position not in by_pos:
            return None
        by_pos[p.position].append(p)

    if any(len(by_pos[pos]) != 2 for pos in positions):
        return None

    total = sum(p.score for p in players)
    target = total / 2
    best = None

    for mask in range(1 << len(positions)):
        team_a: list[Player] = []
        team_b: list[Player] = []
        for idx, pos in enumerate(positions):
            pair = by_pos[pos]
            sel = (mask >> idx) & 1
            team_a.append(pair[sel])
            team_b.append(pair[1 - sel])

        sum_a = sum(p.score for p in team_a)
        diff = abs(sum_a * 2 - total)
        sort_key = (
            diff,
            abs(sum_a - target),
            abs(_variance(team_a) - _variance(team_b)),
            tuple(sorted(p.name for p in team_a)),
        )
        candidate = {
            "team_a": team_a,
            "team_b": team_b,
            "sum_a": sum_a,
            "sum_b": total - sum_a,
            "diff": diff,
            "sort_key": sort_key,
        }
        if best is None or sort_key < best["sort_key"]:
            best = candidate

    return best


def solve_lol_recruit(players: list[Player], positions: list[str], return_all: bool) -> dict:
    if len(players) < 10:
        return {"status": "invalid", "message": "현재 입력된 인원으로는 5:5 팀 구성이 불가능합니다."}

    locked = [p for p in players if p.confirmed]
    unlocked = [p for p in players if not p.confirmed]

    locked_by_pos: dict[str, int] = {pos: 0 for pos in positions}
    total_by_pos: dict[str, int] = {pos: 0 for pos in positions}

    for p in players:
        if p.position not in total_by_pos:
            return {"status": "invalid", "message": "유효하지 않은 포지션이 포함되어 있습니다."}
        total_by_pos[p.position] += 1
    for p in locked:
        locked_by_pos[p.position] += 1

    for pos in positions:
        if locked_by_pos[pos] >= 3:
            return {
                "status": "invalid",
                "message": f"{pos} 포지션 확정 인원이 3명 이상이라 팀 구성이 불가능합니다.",
            }
        if total_by_pos[pos] < 2:
            return {
                "status": "invalid",
                "message": f"{pos} 포지션 인원이 부족하여 팀 구성이 불가능합니다.",
            }

    need_by_pos = {pos: 2 - locked_by_pos[pos] for pos in positions}
    unlock_by_pos: dict[str, list[Player]] = {pos: [] for pos in positions}
    for p in unlocked:
        unlock_by_pos[p.position].append(p)

    for pos, need in need_by_pos.items():
        if need < 0:
            return {
                "status": "invalid",
                "message": f"{pos} 포지션 확정 인원이 너무 많아 팀 구성이 불가능합니다.",
            }
        if len(unlock_by_pos[pos]) < need:
            return {
                "status": "invalid",
                "message": f"{pos} 포지션 인원이 부족하여 팀 구성이 불가능합니다.",
            }

    min_diff = None
    best = None
    all_min: list[dict] = []

    def dfs_pick(pos_idx: int, picked: list[Player]) -> None:
        nonlocal min_diff, best, all_min

        if pos_idx == len(positions):
            selected = locked + picked
            if len(selected) != 10:
                return
            sol = solve_lol_selected_ten(selected, positions)
            if sol is None:
                return

            diff = sol["diff"]
            if min_diff is None or diff < min_diff:
                min_diff = diff
                best = sol
                all_min = [sol]
            elif diff == min_diff:
                all_min.append(sol)
                if sol["sort_key"] < best["sort_key"]:
                    best = sol
            return

        pos = positions[pos_idx]
        need = need_by_pos[pos]
        if need == 0:
            dfs_pick(pos_idx + 1, picked)
            return

        for combo in combinations(unlock_by_pos[pos], need):
            dfs_pick(pos_idx + 1, picked + list(combo))

    dfs_pick(0, [])

    if best is None:
        return {"status": "invalid", "message": "현재 입력된 인원으로는 5:5 팀 구성이 불가능합니다."}

    all_min.sort(key=lambda s: s["sort_key"])

    if return_all:
        return {"status": "ok", "solutions": all_min}
    return {"status": "ok", "best": best}
