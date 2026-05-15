from __future__ import annotations

import unittest

from core.models import Player
from core.result_renderer import format_multi_results_text
from games.lol import league_of_legends_team_advantage_text
from games.valorant import valorant_team_advantage_text


def make_player(name: str, tier: str, position: str) -> Player:
    return Player(pid=0, name=name, tier=tier, score=0, position=position)


class ResultRendererTextTests(unittest.TestCase):
    def test_format_multi_results_text_includes_players_and_scores(self) -> None:
        solution = {
            "team_a": [
                make_player("Alpha", "골드2", "정글"),
                make_player("Bravo", "골드1", "탑"),
                make_player("Charlie", "실버1", "미드"),
                make_player("Delta", "플래티넘1", "서폿"),
                make_player("Echo", "실버2", "원딜"),
            ],
            "team_b": [
                make_player("Foxtrot", "골드2", "정글"),
                make_player("Golf", "골드1", "탑"),
                make_player("Hotel", "실버1", "미드"),
                make_player("India", "플래티넘1", "서폿"),
                make_player("Juliet", "실버2", "원딜"),
            ],
            "sum_a": 50,
            "sum_b": 49,
        }

        text = format_multi_results_text(
            title_text="최적 팀 모집 결과",
            solutions=[solution],
            extra_message="",
            format_player_text=lambda player: f"{player.name} ({player.tier})",
            sort_players=lambda players: sorted(
                players,
                key=lambda player: (
                    {"탑": 0, "정글": 1, "미드": 2, "원딜": 3, "서폿": 4}.get(player.position, 99),
                    player.name,
                ),
            ),
            format_balance_text=lambda _solution: "A팀이 아이언2만큼 우세합니다.",
        )

        self.assertIn("최적 팀 모집 결과", text)
        self.assertIn("#1 | A팀 점수 50 / B팀 점수 49", text)
        self.assertIn("A팀이 아이언2만큼 우세합니다.", text)
        self.assertIn("- 탑: Bravo (골드1)", text)
        self.assertIn("- 서폿: India (플래티넘1)", text)
        self.assertLess(text.index("- 탑: Bravo (골드1)"), text.index("- 정글: Alpha (골드2)"))
        self.assertLess(text.index("- 정글: Alpha (골드2)"), text.index("- 미드: Charlie (실버1)"))
        self.assertLess(text.index("- 미드: Charlie (실버1)"), text.index("- 원딜: Echo (실버2)"))
        self.assertLess(text.index("- 원딜: Echo (실버2)"), text.index("- 서폿: Delta (플래티넘1)"))

    def test_team_advantage_text_reflects_winning_team(self) -> None:
        self.assertEqual(league_of_legends_team_advantage_text(50, 50), "A팀과 B팀은 동등합니다.")
        self.assertIn("A팀이", league_of_legends_team_advantage_text(52, 50))
        self.assertIn("B팀이", valorant_team_advantage_text(48, 50))

    def test_format_multi_results_text_handles_empty_results(self) -> None:
        text = format_multi_results_text(
            title_text="최적 팀 모집 결과",
            solutions=[],
            extra_message="계산 가능한 결과가 없습니다.",
            format_player_text=lambda player: player.name,
            sort_players=lambda players: players,
            format_balance_text=lambda _solution: "A팀과 B팀은 동등합니다.",
        )

        self.assertIn("계산 가능한 결과가 없습니다.", text)
        self.assertIn("표시할 결과가 없습니다.", text)


if __name__ == "__main__":
    unittest.main()
