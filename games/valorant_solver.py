from __future__ import annotations

from itertools import combinations

from core.models import Player
from games.valorant import valorant_tier_to_score


def _has_triple_position(team: list[Player]) -> bool:
    counts: dict[str, int] = {}
    for p in team:
        counts[p.position] = counts.get(p.position, 0) + 1
        if counts[p.position] >= 3:
            return True
    return False


def _mix_penalty(team_a: list[Player], team_b: list[Player]) -> int:
    ca = sum(1 for p in team_a if p.confirmed)
    cb = sum(1 for p in team_b if p.confirmed)
    return abs(ca - cb) + int(ca in {0, 5}) + int(cb in {0, 5})


def _variance(team: list[Player]) -> float:
    if not team:
        return 0.0
    mean = sum(p.score for p in team) / len(team)
    return sum((p.score - mean) ** 2 for p in team) / len(team)


def _extreme_penalty(team_a: list[Player], team_b: list[Player]) -> int:
    high = valorant_tier_to_score("불멸1")
    low = valorant_tier_to_score("실버1")
    ha = sum(1 for p in team_a if p.score >= high)
    hb = sum(1 for p in team_b if p.score >= high)
    la = sum(1 for p in team_a if p.score <= low)
    lb = sum(1 for p in team_b if p.score <= low)
    return abs(ha - hb) + abs(la - lb)


def solve_selected_ten(players: list[Player], no_triple: bool) -> dict | None:
    total = sum(p.score for p in players)
    target = total / 2
    best = None

    for combo in combinations(range(10), 5):
        if 0 not in combo:
            continue
        team_a = [players[i] for i in combo]
        team_b = [players[i] for i in range(10) if i not in combo]

        if no_triple and (_has_triple_position(team_a) or _has_triple_position(team_b)):
            continue

        sum_a = sum(p.score for p in team_a)
        sum_b = total - sum_a
        diff = abs(sum_a - sum_b)

        sort_key = (
            diff,
            _mix_penalty(team_a, team_b),
            abs(_variance(team_a) - _variance(team_b)),
            _extreme_penalty(team_a, team_b),
            tuple(sorted(p.name for p in team_a)),
            abs(sum_a - target),
        )
        candidate = {
            "team_a": team_a,
            "team_b": team_b,
            "sum_a": sum_a,
            "sum_b": sum_b,
            "diff": diff,
            "sort_key": sort_key,
        }
        if best is None or sort_key < best["sort_key"]:
            best = candidate

    return best


def solve_recruit(players: list[Player], no_triple: bool, return_all: bool) -> dict:
    if len(players) < 10:
        return {"status": "invalid", "message": "현재 입력된 인원으로는 5:5 팀 구성이 불가능합니다."}

    locked = [p for p in players if p.confirmed]
    unlocked = [p for p in players if not p.confirmed]

    if len(locked) > 10:
        return {"status": "invalid", "message": "확정 인원이 10명을 초과하여 5:5 팀 구성이 불가능합니다."}

    need = 10 - len(locked)
    if len(unlocked) < need:
        return {"status": "invalid", "message": "현재 입력된 인원으로는 5:5 팀 구성이 불가능합니다."}

    min_diff = None
    best = None
    all_min: list[dict] = []

    for picked in combinations(unlocked, need):
        selected = locked + list(picked)
        sol = solve_selected_ten(selected, no_triple=no_triple)
        if sol is None:
            continue
        diff = sol["diff"]
        if min_diff is None or diff < min_diff:
            min_diff = diff
            best = sol
            all_min = [sol]
        elif diff == min_diff:
            all_min.append(sol)
            if sol["sort_key"] < best["sort_key"]:
                best = sol

    if best is None:
        return {"status": "invalid", "message": "현재 입력된 인원으로는 5:5 팀 구성이 불가능합니다."}

    all_min.sort(key=lambda s: s["sort_key"])

    if return_all:
        return {"status": "ok", "solutions": all_min}
    return {"status": "ok", "best": best}
