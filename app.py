from __future__ import annotations

from typing import Any
import tkinter as tk
import tkinter.messagebox as messagebox

import customtkinter as ctk

from core.constants import (
    HOME_CONTENT_WIDTH,
    POSITION_PLACEHOLDER,
    RESULT_CONTENT_MIN_WIDTH,
    RESULT_PANEL_MIN_WIDTH,
    RESULT_WINDOW_GEOMETRY,
)
from core.input_adapter import extract_recruit_rows, extract_standard_rows
from core.result_cache import build_result_cache_key, get_cached_result
from core.models import Player
from core.recruit_helpers import (
    on_recruit_input_changed as on_recruit_input_changed_helper,
    update_recruit_position_status as update_recruit_position_status_helper,
)
from core.result_renderer import (
    cache_multi_result,
    format_multi_results_text,
    render_multi_results_panel,
    render_team_pair_table,
)
from core.tooltip import SimpleToolTip
from core.ui_helpers import create_standard_player_block, sync_segment_help_icons
from games.lol import (
    LEAGUE_OF_LEGENDS_POSITIONS,
    LEAGUE_OF_LEGENDS_TIER_OPTIONS,
    league_of_legends_diff_to_gap_text,
    league_of_legends_tier_to_score,
    league_of_legends_team_advantage_text,
)
from games.team_services import (
    calculate_recruit_solutions,
    calculate_standard_solution,
    collect_recruit_completed_players,
    collect_standard_players,
)
from games.lol_ui import (
    add_lol_recruit_player_row as add_lol_recruit_player_row_ui,
    build_lol_recruit_panel as build_lol_recruit_panel_ui,
    build_lol_standard_panel as build_lol_standard_panel_ui,
    on_lol_mode_select as on_lol_mode_select_ui,
    show_lol_modes as show_lol_modes_ui,
)
from games.valorant import (
    VALORANT_POSITIONS,
    VALORANT_TIER_OPTIONS,
    valorant_diff_to_gap_text,
    valorant_tier_to_score,
    valorant_team_advantage_text,
)
from games.valorant_ui import (
    add_valorant_recruit_player_row as add_valorant_recruit_player_row_ui,
    build_valorant_recruit_panel as build_valorant_recruit_panel_ui,
    build_valorant_standard_panel as build_valorant_standard_panel_ui,
    on_val_mode_select as on_val_mode_select_ui,
    show_valorant_modes as show_valorant_modes_ui,
)


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TeamBalancingApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("팀 밸런서")
        self.geometry("960x760")
        self.minsize(880, 700)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.configure(width=HOME_CONTENT_WIDTH)
        self.content_frame.grid_propagate(False)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.configure(width=RESULT_PANEL_MIN_WIDTH)
        self.result_frame.grid_propagate(False)
        self.result_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.result_frame.grid_remove()

        self.current_game = "valorant"

        # 팀 구성 (표준 10인) 공용
        self.standard_inputs: list[dict] = []
        self.standard_valorant_limit_var = ctk.BooleanVar(value=True)

        # 팀 모집 공용
        self.recruit_inputs: list[dict] = []
        self.recruit_limit_var = ctk.BooleanVar(value=True)
        self.recruit_position_labels: dict[str, ctk.CTkLabel] = {}
        self.recruit_scroll: ctk.CTkScrollableFrame | None = None

        # 발로란트 모드 전환 위젯 참조
        self._val_seg_btn: ctk.CTkSegmentedButton | None = None
        self._val_standard_frame: ctk.CTkFrame | None = None
        self._val_recruit_frame: ctk.CTkFrame | None = None
        self._val_current_mode = "팀 구성"
        self._val_std_checkbox: ctk.CTkCheckBox | None = None
        self._val_rec_checkbox: ctk.CTkCheckBox | None = None
        self._val_calc_btn: ctk.CTkButton | None = None
        self._val_team_config_help_icon: tk.Canvas | None = None
        self._val_team_recruit_help_icon: tk.Canvas | None = None

        # LoL 모드 전환 위젯 참조
        self._lol_seg_btn: ctk.CTkSegmentedButton | None = None
        self._lol_standard_frame: ctk.CTkFrame | None = None
        self._lol_recruit_frame: ctk.CTkFrame | None = None
        self._lol_current_mode = "팀 구성"
        self._lol_calc_btn: ctk.CTkButton | None = None
        self._lol_team_config_help_icon: tk.Canvas | None = None
        self._lol_team_recruit_help_icon: tk.Canvas | None = None

        self._result_cache: dict[str, dict[str, Any]] = {}
        self._copy_feedback_var = tk.StringVar(value="")
        self._copy_feedback_after_id: str | None = None

        self._tooltips: list[SimpleToolTip] = []

        self.show_home_screen()

    # ─── 공용 유틸리티 ────────────────────────────────────────

    def _hide_result_panel(self) -> None:
        self.result_frame.grid_remove()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(0, minsize=0)
        self.grid_columnconfigure(1, minsize=0)
        self.content_frame.configure(width=HOME_CONTENT_WIDTH)
        self.result_frame.configure(width=RESULT_PANEL_MIN_WIDTH)

    def clear_content(self) -> None:
        for w in self.content_frame.winfo_children():
            w.destroy()
        self._tooltips.clear()
        self.clear_result()
        self._hide_result_panel()

    def clear_result(self) -> None:
        for w in self.result_frame.winfo_children():
            w.destroy()

    def _tier_to_score(self, tier_text: str) -> int:
        if self.current_game == "lol":
            return league_of_legends_tier_to_score(tier_text)
        return valorant_tier_to_score(tier_text)

    def _diff_to_gap_text(self, diff: int) -> str:
        if self.current_game == "lol":
            return league_of_legends_diff_to_gap_text(diff)
        return valorant_diff_to_gap_text(diff)

    def _resolve_ctk_color(self, color: str | tuple[str, str]) -> str:
        return self._apply_appearance_mode(color)

    def _update_val_mode_help_icons(self) -> None:
        sync_segment_help_icons(
            seg_btn=self._val_seg_btn,
            current_mode=self._val_current_mode,
            left_mode_name="팀 구성",
            right_mode_name="팀 모집",
            left_icon=self._val_team_config_help_icon,
            right_icon=self._val_team_recruit_help_icon,
            resolve_color=self._resolve_ctk_color,
        )

    def _update_lol_mode_help_icons(self) -> None:
        sync_segment_help_icons(
            seg_btn=self._lol_seg_btn,
            current_mode=self._lol_current_mode,
            left_mode_name="팀 구성",
            right_mode_name="팀 모집",
            left_icon=self._lol_team_config_help_icon,
            right_icon=self._lol_team_recruit_help_icon,
            resolve_color=self._resolve_ctk_color,
        )

    def _current_result_cache_key(self) -> str:
        return build_result_cache_key(
            current_game=self.current_game,
            valorant_mode=self._val_current_mode,
            lol_mode=self._lol_current_mode,
        )

    def _restore_cached_result(self, cache_key: str) -> bool:
        cached = get_cached_result(self._result_cache, cache_key)
        if cached is None:
            return False
        self._show_multi_results(
            cached["title_text"],
            cached["solutions"],
            cached["extra_message"],
            cache_result=False,
        )
        return True

    # ─── 홈 화면 ─────────────────────────────────────────────

    def show_home_screen(self) -> None:
        self.clear_content()
        self.geometry("980x620")

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        box = ctk.CTkFrame(self.content_frame)
        box.grid(row=0, column=0, padx=40, pady=40)

        ctk.CTkLabel(box, text="팀 밸런서", font=ctk.CTkFont(size=30, weight="bold")).pack(
            padx=40, pady=(30, 12)
        )

        ctk.CTkButton(
            box,
            text="발로란트",
            width=260,
            height=56,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.show_valorant_screen,
        ).pack(padx=40, pady=(10, 14))

        ctk.CTkButton(
            box,
            text="리그오브레전드",
            width=260,
            height=56,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.show_lol_screen,
        ).pack(padx=40, pady=(0, 30))

    # ─── 발로란트 화면 ────────────────────────────────────────

    def show_valorant_screen(self) -> None:
        self.current_game = "valorant"
        self._show_valorant_modes()

    def _show_valorant_modes(self) -> None:
        show_valorant_modes_ui(self)

    def _on_val_mode_select(self, value: str) -> None:
        on_val_mode_select_ui(self, value)

    def _build_valorant_standard_panel(self, parent: ctk.CTkFrame) -> None:
        build_valorant_standard_panel_ui(self, parent)

    def _build_valorant_recruit_panel(self, parent: ctk.CTkFrame) -> None:
        build_valorant_recruit_panel_ui(self, parent)

    # ─── 리그오브레전드 화면 ──────────────────────────────────

    def show_lol_screen(self) -> None:
        self.current_game = "lol"
        self._show_lol_modes()

    def _show_lol_modes(self) -> None:
        show_lol_modes_ui(self)

    def _on_lol_mode_select(self, value: str) -> None:
        on_lol_mode_select_ui(self, value)

    def _build_lol_standard_panel(self, parent: ctk.CTkFrame) -> None:
        build_lol_standard_panel_ui(self, parent)

    def _build_lol_recruit_panel(self, parent: ctk.CTkFrame) -> None:
        build_lol_recruit_panel_ui(self, parent)

    def _add_lol_recruit_player_row(self, scroll_to_new: bool = True) -> None:
        add_lol_recruit_player_row_ui(self, scroll_to_new=scroll_to_new)

    # ─── 공용 입력 블록 생성 ──────────────────────────────────

    def _create_standard_player_block(
        self,
        parent: ctk.CTkFrame,
        idx: int,
        label_text: str,
        include_position_combo: bool,
        default_position: str,
    ) -> ctk.CTkFrame:
        tier_values = (
            LEAGUE_OF_LEGENDS_TIER_OPTIONS if self.current_game == "lol" else VALORANT_TIER_OPTIONS
        )
        return create_standard_player_block(
            parent=parent,
            idx=idx,
            label_text=label_text,
            include_position_combo=include_position_combo,
            default_position=default_position,
            position_placeholder=POSITION_PLACEHOLDER,
            position_values=VALORANT_POSITIONS,
            tier_values=tier_values,
            standard_inputs=self.standard_inputs,
        )

    # ─── 모집 입력 행 추가 ────────────────────────────────────

    def _add_recruit_player_row(self, scroll_to_new: bool = True) -> None:
        add_valorant_recruit_player_row_ui(self, scroll_to_new=scroll_to_new)

    def _scroll_recruit_to_bottom(self) -> None:
        if self.recruit_scroll is None:
            return
        try:
            self.recruit_scroll._parent_canvas.yview_moveto(1.0)
        except AttributeError:
            pass

    def _toggle_recruit_lock(self, idx: int) -> None:
        p = self.recruit_inputs[idx]
        p["confirmed"] = not p["confirmed"]
        if p["confirmed"]:
            p["lock_btn"].configure(text="🔒", fg_color="#1f7a1f", hover_color="#145214")
        else:
            p["lock_btn"].configure(text="🔓", fg_color="#b22222", hover_color="#8b1a1a")
        self._on_recruit_input_changed()

    def _on_recruit_input_changed(self) -> None:
        on_recruit_input_changed_helper(
            self,
            lol_positions=LEAGUE_OF_LEGENDS_POSITIONS,
            valorant_positions=VALORANT_POSITIONS,
        )

    def _update_recruit_position_status(self) -> None:
        update_recruit_position_status_helper(
            self,
            lol_positions=LEAGUE_OF_LEGENDS_POSITIONS,
            valorant_positions=VALORANT_POSITIONS,
        )

    # ─── 완성된 모집 플레이어 수집 ────────────────────────────

    def _collect_recruit_completed_players(self) -> list[Player]:
        rows = extract_recruit_rows(self, tier_to_score=self._tier_to_score)
        return collect_recruit_completed_players(
            rows,
            position_placeholder=POSITION_PLACEHOLDER,
        )

    # ─── 계산 진입점 ──────────────────────────────────────────

    def calculate_standard_teams(self) -> None:
        rows = extract_standard_rows(self, tier_to_score=self._tier_to_score)

        players, error_message = collect_standard_players(
            rows,
            position_placeholder=POSITION_PLACEHOLDER,
        )
        if error_message is not None:
            messagebox.showerror("입력 오류", error_message)
            return

        result = calculate_standard_solution(
            game=self.current_game,
            players=players,
            valorant_no_triple=self.standard_valorant_limit_var.get(),
        )
        if result["status"] != "ok":
            messagebox.showerror("계산 실패", result["message"])
            return

        self._show_single_result("최적 팀 구성", result["solution"])

    def calculate_recruit_best(self) -> None:
        players = self._collect_recruit_completed_players()
        result = calculate_recruit_solutions(
            game=self.current_game,
            players=players,
            lol_positions=LEAGUE_OF_LEGENDS_POSITIONS,
            valorant_no_triple=self.recruit_limit_var.get(),
            max_solutions=5,
        )
        if result["status"] != "ok":
            messagebox.showinfo("안내", result["message"])
            self._show_multi_results("최적 팀 모집 결과", [], result["message"])
            return

        solutions: list[dict] = result["solutions"]
        self._show_multi_results("최적 팀 모집 결과", solutions, "")

    # ─── 결과 표시 ────────────────────────────────────────────

    def _show_single_result(self, title_text: str, solution: dict) -> None:
        self._show_multi_results(title_text, [solution], "")

    def _show_multi_results(
        self,
        title_text: str,
        solutions: list[dict],
        extra_message: str,
        cache_result: bool = True,
    ) -> None:
        self.clear_result()
        self._copy_feedback_var.set("")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(0, minsize=RESULT_CONTENT_MIN_WIDTH)
        self.grid_columnconfigure(1, minsize=RESULT_PANEL_MIN_WIDTH)
        self.content_frame.configure(width=RESULT_CONTENT_MIN_WIDTH)
        self.result_frame.configure(width=RESULT_PANEL_MIN_WIDTH)
        self.geometry(RESULT_WINDOW_GEOMETRY)
        self.result_frame.grid()

        if cache_result:
            cache_multi_result(
                result_cache=self._result_cache,
                cache_key=self._current_result_cache_key(),
                title_text=title_text,
                solutions=solutions,
                extra_message=extra_message,
            )

        render_multi_results_panel(
            result_frame=self.result_frame,
            title_text=title_text,
            solutions=solutions,
            extra_message=extra_message,
            render_solution_table=lambda parent, solution: self._render_team_pair_table(
                parent, solution, small=False
            ),
            on_copy=lambda: self._copy_results_to_clipboard(title_text, solutions, extra_message),
            copy_feedback_var=self._copy_feedback_var,
            format_balance_text=self._format_result_balance_text,
        )

    def _copy_results_to_clipboard(
        self,
        title_text: str,
        solutions: list[dict],
        extra_message: str,
    ) -> None:
        copied_text = format_multi_results_text(
            title_text=title_text,
            solutions=solutions,
            extra_message=extra_message,
            format_player_text=self._format_player_result_text,
            sort_players=self._sort_players_for_result,
            format_balance_text=self._format_result_balance_text,
        )
        self.clipboard_clear()
        self.clipboard_append(copied_text)
        self.update()
        self._copy_feedback_var.set("v")
        if self._copy_feedback_after_id is not None:
            self.after_cancel(self._copy_feedback_after_id)
        self._copy_feedback_after_id = self.after(1500, self._clear_copy_feedback)

    def _clear_copy_feedback(self) -> None:
        self._copy_feedback_var.set("")
        self._copy_feedback_after_id = None

    def _render_team_pair_table(self, parent: ctk.CTkFrame, solution: dict, small: bool) -> None:
        render_team_pair_table(
            parent=parent,
            solution=solution,
            small=small,
            format_player_text=self._format_player_result_text,
            get_player_color=self._get_player_result_color,
            sort_players=self._sort_players_for_result,
        )

    def _format_result_balance_text(self, solution: dict) -> str:
        if self.current_game == "lol":
            return league_of_legends_team_advantage_text(solution["sum_a"], solution["sum_b"])
        return valorant_team_advantage_text(solution["sum_a"], solution["sum_b"])

    def _sort_players_for_result(self, players: list[Player]) -> list[Player]:
        if self.current_game == "lol":
            order = LEAGUE_OF_LEGENDS_POSITIONS
        else:
            order = VALORANT_POSITIONS

        order_index = {position: index for index, position in enumerate(order)}
        fallback = len(order_index)
        return sorted(players, key=lambda player: (order_index.get(player.position, fallback), player.name))

    def _format_player_result_text(self, player: Player) -> str:
        return f"{player.name} ({player.tier})"

    def _get_player_result_color(self, player: Player) -> str | tuple[str, str] | None:
        is_recruit_mode = (
            (self.current_game == "valorant" and self._val_current_mode == "팀 모집")
            or (self.current_game == "lol" and self._lol_current_mode == "팀 모집")
        )
        if is_recruit_mode:
            if player.confirmed:
                return ("#1f7a3a", "#57d073")
            return ("#b42318", "#ff6b6b")
        return None
