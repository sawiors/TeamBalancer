from __future__ import annotations

import unittest

from core.models import Player
from games.lol import LEAGUE_OF_LEGENDS_POSITIONS
from games.team_services import calculate_recruit_solutions, calculate_standard_solution


def make_player(
    pid: int,
    name: str,
    score: int,
    position: str,
    *,
    tier: str = "테스트",
    confirmed: bool = True,
    pair_index: int = -1,
) -> Player:
    return Player(
        pid=pid,
        name=name,
        tier=tier,
        score=score,
        position=position,
        confirmed=confirmed,
        pair_index=pair_index,
    )


class TeamServicesTests(unittest.TestCase):
    def test_calculate_standard_solution_for_valorant_returns_ok(self) -> None:
        players = [
            make_player(0, "A", 10, "타격대"),
            make_player(1, "B", 9, "척후대"),
            make_player(2, "C", 8, "감시자"),
            make_player(3, "D", 7, "전략가"),
            make_player(4, "E", 6, "타격대"),
            make_player(5, "F", 10, "척후대"),
            make_player(6, "G", 9, "감시자"),
            make_player(7, "H", 8, "전략가"),
            make_player(8, "I", 7, "타격대"),
            make_player(9, "J", 6, "척후대"),
        ]

        result = calculate_standard_solution(
            game="valorant",
            players=players,
            valorant_no_triple=False,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["solution"]["team_a"]), 5)
        self.assertEqual(len(result["solution"]["team_b"]), 5)

    def test_calculate_standard_solution_for_lol_returns_ok(self) -> None:
        players = [
            make_player(0, "Top1", 10, "탑", pair_index=0),
            make_player(1, "Top2", 8, "탑", pair_index=0),
            make_player(2, "Jg1", 9, "정글", pair_index=1),
            make_player(3, "Jg2", 7, "정글", pair_index=1),
            make_player(4, "Mid1", 10, "미드", pair_index=2),
            make_player(5, "Mid2", 8, "미드", pair_index=2),
            make_player(6, "Ad1", 9, "원딜", pair_index=3),
            make_player(7, "Ad2", 7, "원딜", pair_index=3),
            make_player(8, "Sup1", 10, "서폿", pair_index=4),
            make_player(9, "Sup2", 8, "서폿", pair_index=4),
        ]

        result = calculate_standard_solution(
            game="lol",
            players=players,
            valorant_no_triple=False,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["solution"]["team_a"]), 5)
        self.assertEqual(len(result["solution"]["team_b"]), 5)

    def test_calculate_recruit_solutions_returns_invalid_for_insufficient_players(self) -> None:
        players = [
            make_player(index, f"P{index}", 5 + index, "탑", confirmed=False)
            for index in range(9)
        ]

        result = calculate_recruit_solutions(
            game="valorant",
            players=players,
            lol_positions=LEAGUE_OF_LEGENDS_POSITIONS,
            valorant_no_triple=False,
            max_solutions=5,
        )

        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["solutions"], [])

    def test_calculate_recruit_solutions_for_lol_respects_max_solutions(self) -> None:
        players = [
            make_player(0, "Top1", 10, "탑", confirmed=True),
            make_player(1, "Top2", 8, "탑", confirmed=False),
            make_player(2, "Jg1", 9, "정글", confirmed=True),
            make_player(3, "Jg2", 7, "정글", confirmed=False),
            make_player(4, "Mid1", 10, "미드", confirmed=True),
            make_player(5, "Mid2", 8, "미드", confirmed=False),
            make_player(6, "Ad1", 9, "원딜", confirmed=True),
            make_player(7, "Ad2", 7, "원딜", confirmed=False),
            make_player(8, "Sup1", 10, "서폿", confirmed=True),
            make_player(9, "Sup2", 8, "서폿", confirmed=False),
        ]

        result = calculate_recruit_solutions(
            game="lol",
            players=players,
            lol_positions=LEAGUE_OF_LEGENDS_POSITIONS,
            valorant_no_triple=False,
            max_solutions=3,
        )

        self.assertEqual(result["status"], "ok")
        self.assertGreaterEqual(len(result["solutions"]), 1)
        self.assertLessEqual(len(result["solutions"]), 3)


if __name__ == "__main__":
    unittest.main()
