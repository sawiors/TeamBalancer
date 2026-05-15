from __future__ import annotations

from typing import Any

import customtkinter as ctk

from core.constants import POSITION_PLACEHOLDER
from core.tooltip import SimpleToolTip
from core.ui_helpers import create_lightbulb_icon
from games.lol import LEAGUE_OF_LEGENDS_POSITIONS, LEAGUE_OF_LEGENDS_TIER_OPTIONS


def show_lol_modes(app: Any) -> None:
    app.clear_content()
    app.geometry("960x760")
    app.standard_inputs = []
    app.recruit_inputs = []
    app.recruit_position_labels = {}

    cf = app.content_frame
    cf.grid_columnconfigure(0, weight=1)
    cf.grid_rowconfigure(0, weight=0)
    cf.grid_rowconfigure(1, weight=0)
    cf.grid_rowconfigure(2, weight=1)
    cf.grid_rowconfigure(3, weight=0)

    ctk.CTkLabel(
        cf, text="리그오브레전드 5 vs 5 팀 구성", font=ctk.CTkFont(size=26, weight="bold")
    ).grid(row=0, column=0, padx=24, pady=(16, 8), sticky="w")

    mode_wrap = ctk.CTkFrame(cf, fg_color="transparent", height=48)
    mode_wrap.grid(row=1, column=0, padx=20, pady=(8, 6), sticky="ew")
    mode_wrap.grid_columnconfigure(0, weight=1)
    mode_wrap.grid_propagate(False)

    seg = ctk.CTkSegmentedButton(
        mode_wrap,
        values=["팀 구성", "팀 모집"],
        height=48,
        font=ctk.CTkFont(size=17, weight="bold"),
        command=app._on_lol_mode_select,
    )
    seg.set("팀 구성")
    seg.grid(row=0, column=0, sticky="ew")
    app._lol_seg_btn = seg

    unselected_color = app._resolve_ctk_color(seg.cget("unselected_color"))

    team_config_help = create_lightbulb_icon(mode_wrap, unselected_color)
    team_config_help.place(relx=0.475, rely=0.5, anchor="e")
    app._lol_team_config_help_icon = team_config_help
    app._tooltips.append(
        SimpleToolTip(
            team_config_help,
            "팀 구성: 입력한 10명을 기준으로\n각 팀에 탑/정글/미드/원딜/서폿이 1명씩 배치되도록 균형 분할합니다.",
        )
    )

    team_recruit_help = create_lightbulb_icon(mode_wrap, unselected_color)
    team_recruit_help.place(relx=0.975, rely=0.5, anchor="e")
    app._lol_team_recruit_help_icon = team_recruit_help
    app._tooltips.append(
        SimpleToolTip(
            team_recruit_help,
            "팀 모집: 완성 입력만 후보로 사용해 최적 10명을 선발합니다.\n"
            "누락된 사람은 자동 제외되며, 확정 인원은 반드시 포함됩니다.",
        )
    )
    app._update_lol_mode_help_icons()

    holder = ctk.CTkFrame(cf, fg_color="transparent")
    holder.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")
    holder.grid_columnconfigure(0, weight=1)
    holder.grid_rowconfigure(0, weight=1)

    app._lol_standard_frame = ctk.CTkFrame(holder, fg_color="transparent")
    app._lol_standard_frame.grid(row=0, column=0, sticky="nsew")
    app._lol_standard_frame.grid_columnconfigure(0, weight=1)
    app._build_lol_standard_panel(app._lol_standard_frame)

    app._lol_recruit_frame = ctk.CTkFrame(holder, fg_color="transparent")
    app._lol_recruit_frame.grid(row=0, column=0, sticky="nsew")
    app._lol_recruit_frame.grid_columnconfigure(0, weight=1)
    app._lol_recruit_frame.grid_rowconfigure(1, weight=1)
    app._build_lol_recruit_panel(app._lol_recruit_frame)

    bottom = ctk.CTkFrame(cf, fg_color="transparent")
    bottom.grid(row=3, column=0, padx=20, pady=(8, 16), sticky="ew")
    bottom.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(
        bottom,
        text="◀",
        width=48,
        height=48,
        font=ctk.CTkFont(size=20),
        fg_color="transparent",
        border_width=2,
        text_color=("gray10", "gray90"),
        hover_color=("gray85", "gray30"),
        command=app.show_home_screen,
    ).grid(row=0, column=0, padx=(4, 12), sticky="w")

    app._lol_calc_btn = ctk.CTkButton(bottom, text="계산", width=140, height=42)
    app._lol_calc_btn.grid(row=0, column=2, padx=(8, 4), sticky="e")

    app._on_lol_mode_select("팀 구성")


def on_lol_mode_select(app: Any, value: str) -> None:
    if not app._lol_standard_frame or not app._lol_recruit_frame:
        return

    app.geometry("960x760")
    app._lol_current_mode = value
    is_standard = value == "팀 구성"

    if is_standard:
        app._lol_standard_frame.grid()
        app._lol_recruit_frame.grid_remove()
        if app._lol_calc_btn:
            app._lol_calc_btn.configure(command=app.calculate_standard_teams)
    else:
        app._lol_standard_frame.grid_remove()
        app._lol_recruit_frame.grid()
        if app._lol_calc_btn:
            app._lol_calc_btn.configure(command=app.calculate_recruit_best)

    app._update_lol_mode_help_icons()

    if not app._restore_cached_result(app._current_result_cache_key()):
        app._hide_result_panel()


def build_lol_standard_panel(app: Any, parent: ctk.CTkFrame) -> None:
    form = ctk.CTkFrame(parent)
    form.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
    form.grid_columnconfigure(0, weight=1)
    form.grid_columnconfigure(1, weight=1)

    for row_index, position in enumerate(LEAGUE_OF_LEGENDS_POSITIONS):
        left_idx = row_index * 2
        right_idx = row_index * 2 + 1

        left = app._create_standard_player_block(
            form,
            idx=left_idx,
            label_text=position,
            include_position_combo=False,
            default_position=position,
        )
        right = app._create_standard_player_block(
            form,
            idx=right_idx,
            label_text=position,
            include_position_combo=False,
            default_position=position,
        )
        left.grid(row=row_index, column=0, padx=(14, 8), pady=8, sticky="ew")
        right.grid(row=row_index, column=1, padx=(8, 14), pady=8, sticky="ew")


def build_lol_recruit_panel(app: Any, parent: ctk.CTkFrame) -> None:
    app.recruit_inputs = []
    app.recruit_position_labels = {}

    status = ctk.CTkFrame(parent)
    status.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
    status.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    for idx, position in enumerate(LEAGUE_OF_LEGENDS_POSITIONS):
        lbl = ctk.CTkLabel(
            status,
            text=f"{position} 0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#d9534f",
        )
        lbl.grid(row=0, column=idx, padx=10, pady=8, sticky="w")
        app.recruit_position_labels[position] = lbl

    app.recruit_scroll = ctk.CTkScrollableFrame(parent)
    app.recruit_scroll.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
    app.recruit_scroll.grid_columnconfigure(0, weight=1)
    app.recruit_scroll.grid_columnconfigure(1, weight=1)

    for _ in range(10):
        app._add_lol_recruit_player_row(scroll_to_new=False)

    add_bar = ctk.CTkFrame(parent, fg_color="transparent")
    add_bar.grid(row=2, column=0, padx=0, pady=(6, 0), sticky="ew")
    add_bar.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(
        add_bar,
        text="+ 인원 추가",
        width=130,
        height=36,
        command=lambda: _add_lol_recruit_two_rows(app),
    ).grid(row=0, column=0, padx=(4, 10), sticky="w")

    ctk.CTkLabel(
        add_bar,
        text="누락된 입력 칸은 자동으로 제외됩니다.",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray60"),
    ).grid(row=0, column=1, padx=4, sticky="w")


def _add_lol_recruit_two_rows(app: Any) -> None:
    first_idx = len(app.recruit_inputs)
    # 한 행에 2명이므로 첫 번째 칸이 왼쪽 열(col=0)이 될 때까지 채우고 1행 추가
    add_lol_recruit_player_row(app, scroll_to_new=False)
    add_lol_recruit_player_row(app, scroll_to_new=False)
    app.after(20, app._scroll_recruit_to_bottom)
    app.after(30, app.recruit_inputs[first_idx]["name_entry"].focus_set)


def add_lol_recruit_player_row(app: Any, scroll_to_new: bool = True) -> None:
    if app.recruit_scroll is None:
        return

    idx = len(app.recruit_inputs)
    row, col = idx // 2, idx % 2

    block = ctk.CTkFrame(app.recruit_scroll)
    block.grid(
        row=row,
        column=col,
        padx=(10, 8) if col == 0 else (8, 10),
        pady=8,
        sticky="ew",
    )
    block.grid_columnconfigure(1, weight=1)
    block.grid_columnconfigure(2, weight=1)
    block.grid_columnconfigure(3, weight=1)

    lock_btn = ctk.CTkButton(
        block,
        text="🔓",
        width=34,
        fg_color="#b22222",
        hover_color="#8b1a1a",
        command=lambda i=idx: app._toggle_recruit_lock(i),
    )
    lock_btn.grid(row=0, column=0, padx=(8, 6), pady=8)
    app._tooltips.append(
        SimpleToolTip(
            lock_btn,
            "잠긴 자물쇠는 확정 인원이며 반드시 포함됩니다.\n"
            "열린 자물쇠는 후보 인원으로 제외될 수 있습니다.",
        )
    )

    name_entry = ctk.CTkEntry(block, placeholder_text="닉네임")
    name_entry.grid(row=0, column=1, padx=(0, 6), pady=8, sticky="ew")

    position_combo = ctk.CTkComboBox(
        block,
        values=[POSITION_PLACEHOLDER] + LEAGUE_OF_LEGENDS_POSITIONS,
        state="readonly",
        command=lambda _v: app._on_recruit_input_changed(),
    )
    position_combo.set(POSITION_PLACEHOLDER)
    position_combo.grid(row=0, column=2, padx=(0, 6), pady=8, sticky="ew")

    tier_combo = ctk.CTkComboBox(
        block,
        values=LEAGUE_OF_LEGENDS_TIER_OPTIONS,
        state="readonly",
        command=lambda _v: app._on_recruit_input_changed(),
    )
    tier_combo.set(LEAGUE_OF_LEGENDS_TIER_OPTIONS[0])
    tier_combo.grid(row=0, column=3, padx=(0, 8), pady=8, sticky="ew")

    name_entry.bind("<KeyRelease>", lambda _e: app._on_recruit_input_changed())

    app.recruit_inputs.append(
        {
            "lock_btn": lock_btn,
            "name_entry": name_entry,
            "position_combo": position_combo,
            "tier_combo": tier_combo,
            "confirmed": False,
        }
    )

    app._on_recruit_input_changed()

    if scroll_to_new:
        app.after(20, app._scroll_recruit_to_bottom)
        app.after(30, name_entry.focus_set)
