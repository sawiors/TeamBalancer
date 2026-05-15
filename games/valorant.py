from __future__ import annotations

VALORANT_RANKS = [
    "아이언",
    "브론즈",
    "실버",
    "골드",
    "플래티넘",
    "다이아몬드",
    "초월자",
    "불멸",
    "레디언트",
]

VALORANT_TIER_OPTIONS = [
    "언랭크",
    "아이언1",
    "아이언2",
    "아이언3",
    "브론즈1",
    "브론즈2",
    "브론즈3",
    "실버1",
    "실버2",
    "실버3",
    "골드1",
    "골드2",
    "골드3",
    "플래티넘1",
    "플래티넘2",
    "플래티넘3",
    "다이아몬드1",
    "다이아몬드2",
    "다이아몬드3",
    "초월자1",
    "초월자2",
    "초월자3",
    "불멸1",
    "불멸2",
    "불멸3",
    "레디언트",
]

VALORANT_POSITIONS = ["타격대", "척후대", "감시자", "전략가"]


def valorant_tier_to_score(tier_text: str) -> int:
    if tier_text == "언랭크":
        return -1
    if tier_text == "레디언트":
        return 3 * VALORANT_RANKS.index("레디언트")
    rank_name = tier_text[:-1]
    tier_num = int(tier_text[-1])
    rank_index = VALORANT_RANKS.index(rank_name)
    return 3 * rank_index + tier_num - 1


def valorant_score_to_tier_text(score: int) -> str:
    if score <= 0:
        return "아이언1"
    if score >= 24:
        return "레디언트"
    return VALORANT_TIER_OPTIONS[score]


def valorant_diff_to_gap_text(diff: int) -> str:
    if diff == 0:
        return "동일"
    if diff <= 24:
        return f"{valorant_score_to_tier_text(diff)} 만큼의 차이"
    return f"레디언트 + {diff - 24} 단계 만큼의 차이"


def valorant_team_advantage_text(sum_a: int, sum_b: int) -> str:
    diff = sum_a - sum_b
    if diff == 0:
        return "A팀과 B팀은 동등합니다."

    advantaged_team = "A팀" if diff > 0 else "B팀"
    gap_text = valorant_score_to_tier_text(abs(diff))
    return f"{advantaged_team}이 {gap_text}만큼 우세합니다."
