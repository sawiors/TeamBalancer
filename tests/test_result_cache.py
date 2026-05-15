from __future__ import annotations

import unittest

from core.result_cache import build_result_cache_key, get_cached_result


class ResultCacheTests(unittest.TestCase):
    def test_build_result_cache_key_for_valorant(self) -> None:
        cache_key = build_result_cache_key(
            current_game="valorant",
            valorant_mode="팀 모집",
            lol_mode="팀 구성",
        )

        self.assertEqual(cache_key, "valorant:팀 모집")

    def test_build_result_cache_key_for_lol(self) -> None:
        cache_key = build_result_cache_key(
            current_game="lol",
            valorant_mode="팀 구성",
            lol_mode="팀 모집",
        )

        self.assertEqual(cache_key, "lol:팀 모집")

    def test_build_result_cache_key_for_unknown_game(self) -> None:
        cache_key = build_result_cache_key(
            current_game="unknown",
            valorant_mode="팀 구성",
            lol_mode="팀 모집",
        )

        self.assertEqual(cache_key, "unknown")

    def test_get_cached_result_returns_payload_when_present(self) -> None:
        cache = {
            "valorant:팀 구성": {
                "title_text": "최적 팀 구성",
                "solutions": [{"sum_a": 10, "sum_b": 10}],
                "extra_message": "",
            }
        }

        cached = get_cached_result(cache, "valorant:팀 구성")

        self.assertIsNotNone(cached)
        self.assertEqual(cached["title_text"], "최적 팀 구성")
        self.assertEqual(cached["solutions"][0]["sum_a"], 10)

    def test_get_cached_result_returns_none_when_missing(self) -> None:
        cached = get_cached_result({}, "lol:팀 모집")

        self.assertIsNone(cached)


if __name__ == "__main__":
    unittest.main()
