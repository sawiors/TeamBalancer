from __future__ import annotations

LEAGUE_OF_LEGENDS_RANKS = [
    "아이언",
    "브론즈",
    "실버",
    "골드",
    "플래티넘",
    "에메랄드",
    "다이아몬드",
    "마스터",
    "그랜드마스터",
    "챌린저",
]

LEAGUE_OF_LEGENDS_TIER_OPTIONS = [
    "언랭크",
    "아이언4",
    "아이언3",
    "아이언2",
    "아이언1",
    "브론즈4",
    "브론즈3",
    "브론즈2",
    "브론즈1",
    "실버4",
    "실버3",
    "실버2",
    "실버1",
    "골드4",
    "골드3",
    "골드2",
    "골드1",
    "플래티넘4",
    "플래티넘3",
    "플래티넘2",
    "플래티넘1",
    "에메랄드4",
    "에메랄드3",
    "에메랄드2",
    "에메랄드1",
    "다이아몬드4",
    "다이아몬드3",
    "다이아몬드2",
    "다이아몬드1",
    "마스터",
    "그랜드마스터",
    "챌린저",
]

LEAGUE_OF_LEGENDS_POSITIONS = ["탑", "정글", "미드", "원딜", "서폿"]


def league_of_legends_tier_to_score(tier_text: str) -> int:
    if tier_text == "언랭크":
        return -1
    if tier_text in {"마스터", "그랜드마스터", "챌린저"}:
        return 4 * (LEAGUE_OF_LEGENDS_RANKS.index(tier_text) + 1)
    rank_name = tier_text[:-1]
    tier_num = int(tier_text[-1])
    rank_index = LEAGUE_OF_LEGENDS_RANKS.index(rank_name) + 1
    return 4 * rank_index - tier_num


def league_of_legends_score_to_tier_text(score: int) -> str:
    if score <= 0:
        return "아이언4"
    if score >= 40:
        return "챌린저"
    ordered_scores = [league_of_legends_tier_to_score(t) for t in LEAGUE_OF_LEGENDS_TIER_OPTIONS]
    best_tier, best_dist = LEAGUE_OF_LEGENDS_TIER_OPTIONS[0], None
    for tier, ts in zip(LEAGUE_OF_LEGENDS_TIER_OPTIONS, ordered_scores):
        d = abs(ts - score)
        if best_dist is None or d < best_dist:
            best_dist, best_tier = d, tier
    return best_tier


def league_of_legends_diff_to_gap_text(diff: int) -> str:
    if diff == 0:
        return "동일"
    if diff <= 40:
        return f"{league_of_legends_score_to_tier_text(diff)} 만큼의 차이"
    return f"챌린저 + {diff - 40} 단계 만큼의 차이"


def league_of_legends_team_advantage_text(sum_a: int, sum_b: int) -> str:
    diff = sum_a - sum_b
    if diff == 0:
        return "A팀과 B팀은 동등합니다."

    advantaged_team = "A팀" if diff > 0 else "B팀"
    gap_text = league_of_legends_score_to_tier_text(abs(diff))
    return f"{advantaged_team}이 {gap_text}만큼 우세합니다."
