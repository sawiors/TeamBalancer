from __future__ import annotations

import unittest

from core.input_adapter import extract_recruit_rows, extract_standard_rows
from games.team_services import collect_recruit_completed_players, collect_standard_players


class FakeWidget:
    def __init__(self, value: str) -> None:
        self._value = value

    def get(self) -> str:
        return self._value


class FakeApp:
    def __init__(self) -> None:
        self.standard_inputs = []
        self.recruit_inputs = []


class InputPipelineTests(unittest.TestCase):
    def test_extract_standard_rows_uses_default_position_when_combo_missing(self) -> None:
        app = FakeApp()
        app.standard_inputs = [
            {
                "name_entry": FakeWidget(" Alpha "),
                "tier_combo": FakeWidget("골드2"),
                "position_combo": None,
                "default_position": "탑",
                "pair_index": 3,
            }
        ]

        rows = extract_standard_rows(app, tier_to_score=lambda tier: 10 if tier == "골드2" else 0)

        self.assertEqual(
            rows,
            [
                {
                    "name": "Alpha",
                    "tier": "골드2",
                    "score": 10,
                    "position": "탑",
                    "pair_index": 3,
                }
            ],
        )

    def test_extract_recruit_rows_keeps_confirmed_flag(self) -> None:
        app = FakeApp()
        app.recruit_inputs = [
            {
                "name_entry": FakeWidget(" Beta "),
                "position_combo": FakeWidget("미드"),
                "tier_combo": FakeWidget("플래티넘1"),
                "confirmed": True,
            }
        ]

        rows = extract_recruit_rows(app, tier_to_score=lambda tier: 13 if tier == "플래티넘1" else 0)

        self.assertEqual(
            rows,
            [
                {
                    "name": "Beta",
                    "position": "미드",
                    "tier": "플래티넘1",
                    "score": 13,
                    "confirmed": True,
                }
            ],
        )

    def test_collect_standard_players_returns_error_for_placeholder(self) -> None:
        players, error_message = collect_standard_players(
            [
                {
                    "name": "Gamma",
                    "tier": "실버1",
                    "score": 6,
                    "position": "포지션 선택",
                    "pair_index": 0,
                }
            ],
            position_placeholder="포지션 선택",
        )

        self.assertEqual(players, [])
        self.assertEqual(error_message, "10명을 모두 입력하세요.")

    def test_collect_recruit_completed_players_skips_incomplete_rows(self) -> None:
        players = collect_recruit_completed_players(
            [
                {
                    "name": "Delta",
                    "tier": "골드1",
                    "score": 9,
                    "position": "원딜",
                    "confirmed": False,
                },
                {
                    "name": "",
                    "tier": "골드2",
                    "score": 10,
                    "position": "서폿",
                    "confirmed": True,
                },
            ],
            position_placeholder="포지션 선택",
        )

        self.assertEqual(len(players), 1)
        self.assertEqual(players[0].name, "Delta")
        self.assertEqual(players[0].position, "원딜")
        self.assertFalse(players[0].confirmed)


if __name__ == "__main__":
    unittest.main()
