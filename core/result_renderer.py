from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk

from core.models import Player


def render_team_pair_table(
    parent: ctk.CTkFrame,
    solution: dict,
    small: bool,
    format_player_text: Callable[[Player], str],
    get_player_color: Callable[[Player], str | tuple[str, str] | None],
    sort_players: Callable[[list[Player]], list[Player]],
) -> None:
    team_a: list[Player] = solution["team_a"]
    team_b: list[Player] = solution["team_b"]

    table = ctk.CTkFrame(parent)
    table.grid(row=0, column=0, sticky="ew")
    table.grid_columnconfigure(0, weight=1)
    table.grid_columnconfigure(1, weight=1)

    fs = 12 if small else 13
    head_font = ctk.CTkFont(size=fs + 1, weight="bold")
    row_font = ctk.CTkFont(size=fs)

    ctk.CTkLabel(table, text="A팀", font=head_font).grid(row=0, column=0, padx=8, pady=(6, 4), sticky="w")
    ctk.CTkLabel(table, text="B팀", font=head_font).grid(row=0, column=1, padx=8, pady=(6, 4), sticky="w")

    a_sorted = sort_players(team_a)
    b_sorted = sort_players(team_b)

    for i in range(5):
        a_label_kwargs = {
            "text": format_player_text(a_sorted[i]),
            "font": row_font,
            "wraplength": 320,
            "justify": "left",
        }
        a_color = get_player_color(a_sorted[i])
        if a_color is not None:
            a_label_kwargs["text_color"] = a_color
        ctk.CTkLabel(table, **a_label_kwargs).grid(row=i + 1, column=0, padx=8, pady=2, sticky="w")

        b_label_kwargs = {
            "text": format_player_text(b_sorted[i]),
            "font": row_font,
            "wraplength": 320,
            "justify": "left",
        }
        b_color = get_player_color(b_sorted[i])
        if b_color is not None:
            b_label_kwargs["text_color"] = b_color
        ctk.CTkLabel(table, **b_label_kwargs).grid(row=i + 1, column=1, padx=8, pady=2, sticky="w")


def cache_multi_result(
    result_cache: dict[str, dict[str, Any]],
    cache_key: str,
    title_text: str,
    solutions: list[dict],
    extra_message: str,
) -> None:
    result_cache[cache_key] = {
        "title_text": title_text,
        "solutions": list(solutions),
        "extra_message": extra_message,
    }


def format_multi_results_text(
    title_text: str,
    solutions: list[dict],
    extra_message: str,
    format_player_text: Callable[[Player], str],
    sort_players: Callable[[list[Player]], list[Player]],
    format_balance_text: Callable[[dict], str] | None = None,
) -> str:
    lines = [title_text]

    if extra_message:
        lines.extend(["", extra_message])

    if not solutions:
        lines.extend(["", "표시할 결과가 없습니다."])
        return "\n".join(lines)

    for rank, solution in enumerate(solutions, start=1):
        team_a = sort_players(solution["team_a"])
        team_b = sort_players(solution["team_b"])

        lines.extend(
            [
                "",
                f"#{rank} | A팀 점수 {solution['sum_a']} / B팀 점수 {solution['sum_b']}",
            ]
        )
        if format_balance_text is not None:
            lines.append(format_balance_text(solution))
        lines.append("A팀:")
        for player in team_a:
            lines.append(f"- {player.position}: {format_player_text(player)}")

        lines.append("B팀:")
        for player in team_b:
            lines.append(f"- {player.position}: {format_player_text(player)}")

    return "\n".join(lines)


def render_multi_results_panel(
    result_frame: ctk.CTkFrame,
    title_text: str,
    solutions: list[dict],
    extra_message: str,
    render_solution_table: Callable[[ctk.CTkFrame, dict], None],
    on_copy: Callable[[], None] | None = None,
    copy_feedback_var: Any | None = None,
    format_balance_text: Callable[[dict], str] | None = None,
) -> None:
    result_frame.grid_columnconfigure(0, weight=1)
    content_row = 1
    result_frame.grid_rowconfigure(content_row, weight=1)

    header = ctk.CTkFrame(result_frame, fg_color="transparent")
    header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(header, text=title_text, font=ctk.CTkFont(size=23, weight="bold")).grid(
        row=0, column=0, sticky="w"
    )

    if on_copy is not None:
        ctk.CTkLabel(
            header,
            textvariable=copy_feedback_var,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1f7a3a",
        ).grid(row=0, column=1, padx=(0, 8), sticky="e")

        ctk.CTkButton(
            header,
            text="결과 복사",
            width=96,
            height=32,
            command=on_copy,
        ).grid(row=0, column=2, padx=(12, 0), sticky="e")

    if extra_message:
        ctk.CTkLabel(
            result_frame,
            text=extra_message,
            font=ctk.CTkFont(size=13),
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")
        content_row = 2
        result_frame.grid_rowconfigure(2, weight=1)

    holder = ctk.CTkScrollableFrame(result_frame)
    holder.grid(row=content_row, column=0, padx=12, pady=(0, 12), sticky="nsew")
    holder.grid_columnconfigure(0, weight=1)

    if not solutions:
        ctk.CTkLabel(holder, text="표시할 결과가 없습니다.", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=8, pady=10, sticky="w"
        )
        return

    for rank, solution in enumerate(solutions, start=1):
        card = ctk.CTkFrame(holder)
        card.grid(row=rank - 1, column=0, padx=4, pady=6, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"#{rank}  |  A팀 점수 {solution['sum_a']} / B팀 점수 {solution['sum_b']}",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")

        details_row = 1
        if format_balance_text is not None:
            ctk.CTkLabel(
                card,
                text=format_balance_text(solution),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="gray35",
            ).grid(row=1, column=0, padx=10, pady=(0, 4), sticky="w")
            details_row = 2

        body = ctk.CTkFrame(card)
        body.grid(row=details_row, column=0, padx=10, pady=(0, 10), sticky="ew")
        body.grid_columnconfigure(0, weight=1)
        render_solution_table(body, solution)


def format_team_advantage_text(
    sum_a: int,
    sum_b: int,
    score_to_tier_text: Callable[[int], str],
) -> str:
    diff = sum_a - sum_b
    if diff == 0:
        return "A팀과 B팀은 동등합니다."

    advantaged_team = "A팀" if diff > 0 else "B팀"
    gap_text = score_to_tier_text(abs(diff))
    return f"{advantaged_team}이 {gap_text}만큼 우세합니다."
