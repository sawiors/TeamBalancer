from __future__ import annotations

from typing import TypedDict


class StandardRow(TypedDict):
    name: str
    tier: str
    score: int
    position: str
    pair_index: int


class RecruitRow(TypedDict):
    name: str
    tier: str
    score: int
    position: str
    confirmed: bool
