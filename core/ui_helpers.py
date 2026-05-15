from __future__ import annotations

from typing import Callable
import tkinter as tk

import customtkinter as ctk


def create_lightbulb_icon(parent: tk.Widget, bg_color: str) -> tk.Canvas:
    canvas = tk.Canvas(
        parent,
        width=18,
        height=18,
        bg=bg_color,
        highlightthickness=0,
        bd=0,
        relief="flat",
    )
    canvas.create_oval(4, 2, 14, 12, fill="#facc15", outline="#222222", width=1.5)
    canvas.create_rectangle(7, 11, 11, 14, fill="#facc15", outline="#222222", width=1.2)
    canvas.create_line(6, 15, 12, 15, fill="#222222", width=1.2)
    canvas.create_line(7, 17, 11, 17, fill="#222222", width=1.2)
    return canvas


def sync_segment_help_icons(
    seg_btn: ctk.CTkSegmentedButton | None,
    current_mode: str,
    left_mode_name: str,
    right_mode_name: str,
    left_icon: tk.Canvas | None,
    right_icon: tk.Canvas | None,
    resolve_color: Callable[[str | tuple[str, str]], str],
) -> None:
    if not seg_btn:
        return

    selected_color = resolve_color(seg_btn.cget("selected_color"))
    unselected_color = resolve_color(seg_btn.cget("unselected_color"))

    left_bg = selected_color if current_mode == left_mode_name else unselected_color
    right_bg = selected_color if current_mode == right_mode_name else unselected_color

    if left_icon is not None:
        left_icon.configure(bg=left_bg)
    if right_icon is not None:
        right_icon.configure(bg=right_bg)


def create_standard_player_block(
    parent: ctk.CTkFrame,
    idx: int,
    label_text: str,
    include_position_combo: bool,
    default_position: str,
    position_placeholder: str,
    position_values: list[str],
    tier_values: list[str],
    standard_inputs: list[dict],
) -> ctk.CTkFrame:
    block = ctk.CTkFrame(parent)
    block.grid_columnconfigure(0, weight=1)
    block.grid_columnconfigure(1, weight=1)
    block.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(block, text=label_text, font=ctk.CTkFont(size=14, weight="bold")).grid(
        row=0, column=0, columnspan=3, padx=10, pady=(8, 4), sticky="w"
    )

    name_entry = ctk.CTkEntry(block, placeholder_text="닉네임")
    name_entry.grid(row=1, column=0, padx=(10, 6), pady=(0, 10), sticky="ew")

    position_combo = None
    if include_position_combo:
        position_combo = ctk.CTkComboBox(
            block,
            values=[position_placeholder] + position_values,
            state="readonly",
            width=120,
        )
        position_combo.set(default_position)
        position_combo.grid(row=1, column=1, padx=(6, 6), pady=(0, 10), sticky="ew")

    tier_col = 2 if include_position_combo else 1
    tier_combo = ctk.CTkComboBox(block, values=tier_values, state="readonly")
    tier_combo.set(tier_values[0])
    tier_combo.grid(row=1, column=tier_col, padx=(6, 10), pady=(0, 10), sticky="ew")

    standard_inputs.append(
        {
            "name_entry": name_entry,
            "tier_combo": tier_combo,
            "position_combo": position_combo,
            "default_position": default_position,
            "pair_index": idx // 2,
        }
    )
    return block
