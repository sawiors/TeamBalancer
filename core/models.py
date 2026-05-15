from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    pid: int
    name: str
    tier: str
    score: int
    position: str
    confirmed: bool = False
    pair_index: int = -1
