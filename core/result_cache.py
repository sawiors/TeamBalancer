from __future__ import annotations

from typing import Any, TypedDict


class CachedResult(TypedDict):
    title_text: str
    solutions: list[dict[str, Any]]
    extra_message: str


ResultCache = dict[str, CachedResult]


def build_result_cache_key(*, current_game: str, valorant_mode: str, lol_mode: str) -> str:
    if current_game == "valorant":
        return f"valorant:{valorant_mode}"
    if current_game == "lol":
        return f"lol:{lol_mode}"
    return "unknown"


def get_cached_result(result_cache: ResultCache, cache_key: str) -> CachedResult | None:
    return result_cache.get(cache_key)
