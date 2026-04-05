"""
╔══════════════════════════════════════════════════════════════╗
║              🎰  ROYAL CASINO ROULETTE  🎰                  ║
║           European Roulette  ·  Mini Project                 ║
╚══════════════════════════════════════════════════════════════╝

A fully-featured casino roulette game built with Python & Tkinter.
Features:
  • Animated spinning roulette wheel (European, 0-36)
  • Full betting table (numbers, red/black, odd/even, dozens, columns, halves)
  • Chip selection ($5 / $25 / $100 / $500)
  • Balance tracking with win/loss history
  • Premium dark casino theme with gold accents

No external dependencies – runs on any Python 3.x installation.
"""

import tkinter as tk
from tkinter import font as tkfont
import math
import random
import time

# ─────────────────────────── CONSTANTS ────────────────────────────

# European roulette wheel order
WHEEL_ORDER = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36,
    11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
    22, 18, 29, 7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

# ─── Color palette ───
BG_DARK        = "#0D0D0D"
BG_FELT        = "#0B3D0B"
BG_FELT_DARK   = "#072807"
GOLD           = "#D4AF37"
GOLD_LIGHT     = "#F5D76E"
GOLD_DIM       = "#8B7536"
RED            = "#C0392B"
RED_HOVER      = "#E74C3C"
BLACK          = "#1A1A2E"
GREEN_NUM      = "#27AE60"
WHITE          = "#ECF0F1"
GRAY           = "#7F8C8D"
GRAY_DARK      = "#2C3E50"
CHIP_BORDER    = "#F1C40F"
WIN_COLOR      = "#2ECC71"
LOSE_COLOR     = "#E74C3C"
TABLE_LINE     = "#3A7D3A"
HEADER_BG      = "#111111"


# ─────────────────────────── ROULETTE GAME ────────────────────────

class RouletteGame:
    """Core game logic – manages balance, bets, and payout calculations."""

    PAYOUTS = {
        "straight": 35,   # single number
        "red": 1, "black": 1,
        "odd": 1, "even": 1,
        "1-18": 1, "19-36": 1,
        "1st12": 2, "2nd12": 2, "3rd12": 2,
        "col1": 2, "col2": 2, "col3": 2,
    }

    def __init__(self, starting_balance=1000):
        self.balance = starting_balance
        self.bets: list[dict] = []          # [{type, value, amount}, ...]
        self.history: list[int] = []
        self.last_win = 0

    # ── betting ──────────────────────────────────────────────
    def place_bet(self, bet_type: str, value, amount: int) -> bool:
        total_on_table = sum(b["amount"] for b in self.bets)
        if total_on_table + amount > self.balance:
            return False
        self.bets.append({"type": bet_type, "value": value, "amount": amount})
        return True

    def clear_bets(self):
        self.bets.clear()

    def total_bet(self) -> int:
        return sum(b["amount"] for b in self.bets)

    # ── spin & resolve ───────────────────────────────────────
    def spin(self) -> int:
        result = random.choice(WHEEL_ORDER)
        self.history.append(result)
        return result

    def resolve(self, result: int) -> int:
        """Returns total winnings (profit only, not including stake)."""
        total_winnings = 0
        for bet in self.bets:
            if self._is_winner(bet, result):
                payout = self.PAYOUTS.get(bet["type"], 0)
                total_winnings += bet["amount"] * payout + bet["amount"]
            # losing bet: amount is lost (already deducted before spin)
        # Deduct total bet, add winnings
        self.balance -= self.total_bet()
        self.balance += total_winnings
        self.last_win = total_winnings
        self.bets.clear()
        return total_winnings

    @staticmethod
    def _is_winner(bet: dict, result: int) -> bool:
        t, v = bet["type"], bet["value"]
        if t == "straight":
            return result == v
        if t == "red":
            return result in RED_NUMBERS
        if t == "black":
            return result in BLACK_NUMBERS
        if t == "odd":
            return result != 0 and result % 2 == 1
        if t == "even":
            return result != 0 and result % 2 == 0
        if t == "1-18":
            return 1 <= result <= 18
        if t == "19-36":
            return 19 <= result <= 36
        if t == "1st12":
            return 1 <= result <= 12
        if t == "2nd12":
            return 13 <= result <= 24
        if t == "3rd12":
            return 25 <= result <= 36
        if t == "col1":
            return result != 0 and result % 3 == 1
        if t == "col2":
            return result != 0 and result % 3 == 2
        if t == "col3":
            return result != 0 and result % 3 == 0
        return False

    @staticmethod
    def number_color(n: int) -> str:
        if n == 0:
            return "green"
        return "red" if n in RED_NUMBERS else "black"


# ──────────────────────────── GUI ─────────────────────────────────

class RouletteApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("🎰 Royal Casino Roulette")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        # Centre the window
        w, h = 1280, 820
        sx = self.winfo_screenwidth() // 2 - w // 2
        sy = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{sx}+{sy}")

        # ── Fonts ──
        self.font_title  = tkfont.Font(family="Georgia", size=22, weight="bold")
        self.font_sub    = tkfont.Font(family="Segoe UI", size=11)
        self.font_num    = tkfont.Font(family="Consolas", size=11, weight="bold")
        self.font_chip   = tkfont.Font(family="Consolas", size=10, weight="bold")
        self.font_btn    = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_big    = tkfont.Font(family="Georgia", size=28, weight="bold")
        self.font_hist   = tkfont.Font(family="Consolas", size=10)
        self.font_label  = tkfont.Font(family="Segoe UI", size=10)
        self.font_bal    = tkfont.Font(family="Georgia", size=16, weight="bold")

        self.game = RouletteGame()
        self.selected_chip = 25
        self.spinning = False
        self.wheel_angle = 0.0
        self.ball_angle = 0.0
        self.result_number = None
        self.bet_markers: list = []

        self._build_ui()
        self._draw_wheel()
        self._update_balance_display()

    # ────────────────── UI CONSTRUCTION ───────────────────────

    def _build_ui(self):
        # ── Header bar ──
        header = tk.Frame(self, bg=HEADER_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="♠ ♥ ROYAL CASINO ROULETTE ♦ ♣", font=self.font_title,
                 fg=GOLD, bg=HEADER_BG).pack(side="left", padx=20, pady=10)

        self.lbl_balance = tk.Label(header, text="", font=self.font_bal,
                                     fg=GOLD_LIGHT, bg=HEADER_BG)
        self.lbl_balance.pack(side="right", padx=20)

        # ── Main content ──
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: wheel
        left = tk.Frame(main, bg=BG_DARK)
        left.pack(side="left", fill="both", padx=5)

        self.canvas_wheel = tk.Canvas(left, width=400, height=400,
                                       bg=BG_FELT_DARK, highlightthickness=0)
        self.canvas_wheel.pack(pady=(10, 5))

        # Result display
        self.lbl_result = tk.Label(left, text="Place your bets!", font=self.font_big,
                                    fg=GOLD, bg=BG_DARK)
        self.lbl_result.pack(pady=(0, 5))

        # History strip
        hist_frame = tk.Frame(left, bg=BG_DARK)
        hist_frame.pack(pady=(0, 5))
        tk.Label(hist_frame, text="HISTORY", font=self.font_label,
                 fg=GRAY, bg=BG_DARK).pack(anchor="w")
        self.canvas_hist = tk.Canvas(hist_frame, width=390, height=36,
                                      bg=BG_DARK, highlightthickness=0)
        self.canvas_hist.pack()

        # Right: table + controls
        right = tk.Frame(main, bg=BG_DARK)
        right.pack(side="right", fill="both", expand=True, padx=5)

        # Betting table canvas
        self.canvas_table = tk.Canvas(right, width=820, height=460,
                                       bg=BG_FELT, highlightthickness=2,
                                       highlightbackground=GOLD_DIM)
        self.canvas_table.pack(pady=(10, 5))
        self._draw_table()
        self.canvas_table.bind("<Button-1>", self._on_table_click)

        # Controls bar  
        ctrl = tk.Frame(right, bg=BG_DARK)
        ctrl.pack(fill="x", pady=(5, 5))

        # Chip selector
        chip_frame = tk.LabelFrame(ctrl, text=" SELECT CHIP ", font=self.font_label,
                                    fg=GOLD, bg=BG_DARK, bd=1, relief="groove",
                                    labelanchor="n")
        chip_frame.pack(side="left", padx=(0, 15))

        self.chip_buttons = {}
        chip_values = [5, 25, 100, 500]
        chip_colors_map = {5: "#E74C3C", 25: "#27AE60", 100: "#2980B9", 500: "#8E44AD"}
        for val in chip_values:
            c = chip_colors_map[val]
            btn = tk.Canvas(chip_frame, width=52, height=52, bg=BG_DARK,
                            highlightthickness=0, cursor="hand2")
            btn.pack(side="left", padx=4, pady=4)
            self._draw_chip(btn, val, c, selected=(val == self.selected_chip))
            btn.bind("<Button-1>", lambda e, v=val: self._select_chip(v))
            self.chip_buttons[val] = (btn, c)

        # Action buttons
        btn_frame = tk.Frame(ctrl, bg=BG_DARK)
        btn_frame.pack(side="left", padx=10)

        self.btn_spin = tk.Button(btn_frame, text="🎲  SPIN", font=self.font_btn,
                                   fg=BG_DARK, bg=GOLD, activebackground=GOLD_LIGHT,
                                   activeforeground=BG_DARK, relief="flat",
                                   padx=25, pady=8, cursor="hand2",
                                   command=self._on_spin)
        self.btn_spin.pack(side="left", padx=5)

        self.btn_clear = tk.Button(btn_frame, text="✖ CLEAR", font=self.font_btn,
                                    fg=WHITE, bg="#555", activebackground="#777",
                                    relief="flat", padx=15, pady=8, cursor="hand2",
                                    command=self._on_clear)
        self.btn_clear.pack(side="left", padx=5)

        self.btn_reset = tk.Button(btn_frame, text="↻ NEW GAME", font=self.font_btn,
                                    fg=WHITE, bg=GRAY_DARK, activebackground="#3D566E",
                                    relief="flat", padx=15, pady=8, cursor="hand2",
                                    command=self._on_reset)
        self.btn_reset.pack(side="left", padx=5)

        # Bet info
        info_frame = tk.Frame(ctrl, bg=BG_DARK)
        info_frame.pack(side="right", padx=10)

        self.lbl_total_bet = tk.Label(info_frame, text="Total Bet: $0",
                                       font=self.font_sub, fg=WHITE, bg=BG_DARK)
        self.lbl_total_bet.pack(anchor="e")

        self.lbl_status = tk.Label(info_frame, text="", font=self.font_sub,
                                    fg=GOLD_LIGHT, bg=BG_DARK)
        self.lbl_status.pack(anchor="e")

    # ────────────────── CHIP DRAWING ─────────────────────────

    def _draw_chip(self, canvas: tk.Canvas, value: int, color: str, selected: bool = False):
        canvas.delete("all")
        cx, cy, r = 26, 26, 22
        # Outer glow when selected
        if selected:
            canvas.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                               fill="", outline=GOLD, width=3)
        # Main chip body
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color,
                           outline="#FFF", width=2)
        # Inner ring
        canvas.create_oval(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                           fill="", outline="#AAAAAA", width=1, dash=(3, 3))
        # Value text
        canvas.create_text(cx, cy, text=f"${value}", fill="white",
                           font=self.font_chip)

    def _select_chip(self, value: int):
        self.selected_chip = value
        chip_colors_map = {5: "#E74C3C", 25: "#27AE60", 100: "#2980B9", 500: "#8E44AD"}
        for v, (btn, c) in self.chip_buttons.items():
            self._draw_chip(btn, v, c, selected=(v == value))

    # ────────────────── ROULETTE WHEEL ───────────────────────

    def _draw_wheel(self):
        c = self.canvas_wheel
        c.delete("all")
        cx, cy = 200, 200
        outer_r = 180
        inner_r = 130
        num_slots = len(WHEEL_ORDER)
        arc = 360 / num_slots

        # Dark background circle
        c.create_oval(cx - outer_r - 5, cy - outer_r - 5,
                      cx + outer_r + 5, cy + outer_r + 5,
                      fill="#1a1a1a", outline=GOLD_DIM, width=3)

        for i, num in enumerate(WHEEL_ORDER):
            start = self.wheel_angle + i * arc
            color = GREEN_NUM if num == 0 else (RED if num in RED_NUMBERS else "#1A1A2E")

            # Draw sector
            c.create_arc(cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r,
                         start=start, extent=arc, fill=color, outline="#333", width=1)

            # Number label
            mid_angle = math.radians(start + arc / 2)
            tr = (outer_r + inner_r) / 2
            tx = cx + tr * math.cos(mid_angle)
            ty = cy - tr * math.sin(mid_angle)
            c.create_text(tx, ty, text=str(num), fill="white",
                         font=("Consolas", 8, "bold"))

        # Inner circle (hub)
        c.create_oval(cx - inner_r + 15, cy - inner_r + 15,
                      cx + inner_r - 15, cy + inner_r - 15,
                      fill="#222", outline=GOLD_DIM, width=2)
        c.create_oval(cx - 40, cy - 40, cx + 40, cy + 40,
                      fill="#111", outline=GOLD, width=2)
        c.create_text(cx, cy, text="⬥", fill=GOLD, font=("Segoe UI", 18))

        # Ball marker
        if self.result_number is not None:
            idx = WHEEL_ORDER.index(self.result_number)
            ball_angle_rad = math.radians(self.wheel_angle + idx * arc + arc / 2)
            br = outer_r - 12
            bx = cx + br * math.cos(ball_angle_rad)
            by = cy - br * math.sin(ball_angle_rad)
            c.create_oval(bx - 6, by - 6, bx + 6, by + 6,
                         fill="white", outline="#CCC", width=1)
        elif self.spinning:
            ball_angle_rad = math.radians(self.ball_angle)
            br = outer_r - 12
            bx = cx + br * math.cos(ball_angle_rad)
            by = cy - br * math.sin(ball_angle_rad)
            c.create_oval(bx - 6, by - 6, bx + 6, by + 6,
                         fill="white", outline="#CCC", width=1)

        # Pointer triangle at top
        c.create_polygon(cx - 10, cy - outer_r - 8,
                         cx + 10, cy - outer_r - 8,
                         cx, cy - outer_r + 8,
                         fill=GOLD, outline=GOLD_LIGHT)

    # ────────────────── BETTING TABLE ────────────────────────

    def _draw_table(self):
        c = self.canvas_table
        c.delete("all")

        # Table dimensions
        ox, oy = 15, 15          # origin offset
        cw, ch = 58, 44          # cell width / height
        rows, cols = 3, 12

        # ── Zero ──
        zw = 40
        c.create_rectangle(ox, oy, ox + zw, oy + ch * 3,
                           fill=GREEN_NUM, outline=TABLE_LINE, width=2)
        c.create_text(ox + zw // 2, oy + ch * 1.5, text="0",
                     fill="white", font=self.font_num)

        # ── Number grid (3 rows × 12 cols) ──
        # Row 0 (top) = 3, 6, 9, …, 36
        # Row 1 (mid) = 2, 5, 8, …, 35
        # Row 2 (bot) = 1, 4, 7, …, 34
        grid_x = ox + zw
        for col in range(cols):
            for row in range(rows):
                num = (col * 3) + (3 - row)
                x1 = grid_x + col * cw
                y1 = oy + row * ch
                x2 = x1 + cw
                y2 = y1 + ch
                fill = RED if num in RED_NUMBERS else BLACK
                c.create_rectangle(x1, y1, x2, y2, fill=fill,
                                   outline=TABLE_LINE, width=1)
                c.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(num),
                             fill="white", font=self.font_num)

        # ── Column bets (2:1) ──
        col_x = grid_x + cols * cw
        col_labels = ["col3", "col2", "col1"]
        for row in range(3):
            y1 = oy + row * ch
            y2 = y1 + ch
            c.create_rectangle(col_x, y1, col_x + 50, y2,
                               fill=BG_FELT_DARK, outline=TABLE_LINE, width=1)
            c.create_text(col_x + 25, (y1 + y2) // 2, text="2:1",
                         fill=GOLD, font=self.font_label)

        # ── Bottom outside bets ──
        bot_y = oy + rows * ch + 5
        bot_h = 38
        total_w = cols * cw
        # Row 1: dozens
        doz_labels = [("1st 12", "1st12"), ("2nd 12", "2nd12"), ("3rd 12", "3rd12")]
        doz_w = total_w // 3
        for i, (label, _) in enumerate(doz_labels):
            x1 = grid_x + i * doz_w
            c.create_rectangle(x1, bot_y, x1 + doz_w, bot_y + bot_h,
                               fill=BG_FELT_DARK, outline=TABLE_LINE, width=1)
            c.create_text(x1 + doz_w // 2, bot_y + bot_h // 2, text=label,
                         fill=GOLD_LIGHT, font=self.font_label)

        # Row 2: 1-18, Even, Red, Black, Odd, 19-36
        bot_y2 = bot_y + bot_h + 3
        six_w = total_w // 6
        outside_labels = [
            ("1-18", "1-18"),
            ("EVEN", "even"),
            ("◆ RED", "red"),
            ("◆ BLK", "black"),
            ("ODD", "odd"),
            ("19-36", "19-36"),
        ]
        outside_colors = [BG_FELT_DARK, BG_FELT_DARK, RED, BLACK, BG_FELT_DARK, BG_FELT_DARK]
        for i, ((label, _), fc) in enumerate(zip(outside_labels, outside_colors)):
            x1 = grid_x + i * six_w
            c.create_rectangle(x1, bot_y2, x1 + six_w, bot_y2 + bot_h,
                               fill=fc, outline=TABLE_LINE, width=1)
            fg = "white" if fc in (RED, BLACK) else GOLD_LIGHT
            c.create_text(x1 + six_w // 2, bot_y2 + bot_h // 2, text=label,
                         fill=fg, font=self.font_label)

        # Store layout info for click detection
        self._table_layout = {
            "ox": ox, "oy": oy, "cw": cw, "ch": ch,
            "zw": zw, "grid_x": grid_x, "rows": rows, "cols": cols,
            "col_x": col_x, "bot_y": bot_y, "bot_h": bot_h,
            "bot_y2": bot_y2, "six_w": six_w, "doz_w": doz_w,
            "total_w": total_w,
        }

    # ────────────────── TABLE CLICK → BET ────────────────────

    def _on_table_click(self, event):
        if self.spinning:
            return
        L = self._table_layout
        x, y = event.x, event.y
        bet_type, bet_value = None, None

        # ── Zero ──
        if L["ox"] <= x <= L["ox"] + L["zw"] and L["oy"] <= y <= L["oy"] + L["ch"] * 3:
            bet_type, bet_value = "straight", 0

        # ── Number grid ──
        elif L["grid_x"] <= x <= L["grid_x"] + L["cols"] * L["cw"] and \
             L["oy"] <= y <= L["oy"] + L["rows"] * L["ch"]:
            col = int((x - L["grid_x"]) / L["cw"])
            row = int((y - L["oy"]) / L["ch"])
            col = min(col, L["cols"] - 1)
            row = min(row, L["rows"] - 1)
            num = col * 3 + (3 - row)
            bet_type, bet_value = "straight", num

        # ── Column bets ──
        elif L["col_x"] <= x <= L["col_x"] + 50 and L["oy"] <= y <= L["oy"] + L["rows"] * L["ch"]:
            row = int((y - L["oy"]) / L["ch"])
            row = min(row, 2)
            col_map = {0: "col3", 1: "col2", 2: "col1"}
            bet_type, bet_value = col_map[row], None

        # ── Dozen bets ──
        elif L["oy"] + L["rows"] * L["ch"] + 5 <= y <= L["bot_y"] + L["bot_h"]:
            doz_i = int((x - L["grid_x"]) / L["doz_w"])
            doz_i = max(0, min(doz_i, 2))
            doz_map = {0: "1st12", 1: "2nd12", 2: "3rd12"}
            bet_type, bet_value = doz_map[doz_i], None

        # ── Outside bets row ──
        elif L["bot_y2"] <= y <= L["bot_y2"] + L["bot_h"]:
            oi = int((x - L["grid_x"]) / L["six_w"])
            oi = max(0, min(oi, 5))
            out_map = {0: "1-18", 1: "even", 2: "red", 3: "black", 4: "odd", 5: "19-36"}
            bet_type, bet_value = out_map[oi], None

        if bet_type is None:
            return

        # Attempt to place bet
        ok = self.game.place_bet(bet_type, bet_value, self.selected_chip)
        if ok:
            self._draw_bet_marker(x, y, self.selected_chip)
            self._update_bet_display()
            label = f"${self.selected_chip} on "
            if bet_type == "straight":
                label += str(bet_value)
            else:
                label += bet_type.upper()
            self.lbl_status.config(text=label, fg=GOLD_LIGHT)
        else:
            self.lbl_status.config(text="Insufficient balance!", fg=LOSE_COLOR)

    def _draw_bet_marker(self, x, y, amount):
        """Draw a small chip on the table to show the bet."""
        c = self.canvas_table
        r = 14
        chip_colors = {5: "#E74C3C", 25: "#27AE60", 100: "#2980B9", 500: "#8E44AD"}
        color = chip_colors.get(amount, "#27AE60")
        ids = []
        ids.append(c.create_oval(x - r, y - r, x + r, y + r,
                                  fill=color, outline="white", width=2))
        ids.append(c.create_text(x, y, text=f"${amount}", fill="white",
                                  font=("Consolas", 7, "bold")))
        self.bet_markers.extend(ids)

    # ────────────────── SPIN ANIMATION ───────────────────────

    def _on_spin(self):
        if self.spinning:
            return
        if self.game.total_bet() == 0:
            self.lbl_status.config(text="Place at least one bet!", fg=LOSE_COLOR)
            return

        self.spinning = True
        self.result_number = None
        self.btn_spin.config(state="disabled", bg=GRAY)
        self.btn_clear.config(state="disabled")
        self.lbl_result.config(text="Spinning…", fg=GOLD)

        # Determine result before animation
        self._spin_result = self.game.spin()

        # Animation parameters
        self._spin_speed = 18.0       # degrees per frame
        self._spin_decel = 0.96       # deceleration factor
        self._ball_speed = -25.0      # ball spins opposite
        self._ball_decel = 0.965
        self._spin_frames = 0
        self.ball_angle = random.uniform(0, 360)

        self._animate_spin()

    def _animate_spin(self):
        self.wheel_angle += self._spin_speed
        self.ball_angle += self._ball_speed
        self._spin_speed *= self._spin_decel
        self._ball_speed *= self._ball_decel
        self._spin_frames += 1

        self._draw_wheel()

        if abs(self._spin_speed) < 0.3 and self._spin_frames > 40:
            # Snap to result
            self.result_number = self._spin_result
            idx = WHEEL_ORDER.index(self.result_number)
            arc = 360 / len(WHEEL_ORDER)
            # Align so the result is at the pointer (top, 90°)
            self.wheel_angle = 90 - idx * arc - arc / 2
            self._draw_wheel()
            self._finish_spin()
            return

        self.after(30, self._animate_spin)

    def _finish_spin(self):
        result = self._spin_result
        color_name = RouletteGame.number_color(result)
        color_hex = {
            "red": RED, "black": "#AAA", "green": GREEN_NUM
        }[color_name]

        self.lbl_result.config(text=f"  {result}  ", fg=color_hex)

        # Resolve bets
        winnings = self.game.resolve(result)
        if winnings > 0:
            self.lbl_status.config(text=f"🎉 WIN! +${winnings}", fg=WIN_COLOR)
        else:
            self.lbl_status.config(text="No win this round.", fg=LOSE_COLOR)

        self._update_balance_display()
        self._draw_history()
        self._clear_bet_markers()
        self._update_bet_display()

        self.spinning = False
        self.btn_spin.config(state="normal", bg=GOLD)
        self.btn_clear.config(state="normal")

        # Check bankrupt
        if self.game.balance <= 0:
            self.lbl_result.config(text="GAME OVER", fg=LOSE_COLOR)
            self.lbl_status.config(text="You're out of chips! Click NEW GAME.", fg=LOSE_COLOR)
            self.btn_spin.config(state="disabled", bg=GRAY)

    # ────────────────── HISTORY STRIP ────────────────────────

    def _draw_history(self):
        c = self.canvas_hist
        c.delete("all")
        history = self.game.history[-15:]   # last 15
        r = 15
        spacing = 26
        for i, num in enumerate(history):
            x = 13 + i * spacing
            y = 18
            col = GREEN_NUM if num == 0 else (RED if num in RED_NUMBERS else "#333")
            c.create_oval(x - r // 2, y - r // 2, x + r // 2, y + r // 2,
                         fill=col, outline="#555")
            c.create_text(x, y, text=str(num), fill="white",
                         font=("Consolas", 8, "bold"))

    # ────────────────── CONTROLS ─────────────────────────────

    def _on_clear(self):
        if self.spinning:
            return
        self.game.clear_bets()
        self._clear_bet_markers()
        self._update_bet_display()
        self.lbl_status.config(text="Bets cleared.", fg=GRAY)

    def _on_reset(self):
        if self.spinning:
            return
        self.game = RouletteGame()
        self._clear_bet_markers()
        self._update_bet_display()
        self._update_balance_display()
        self.result_number = None
        self.wheel_angle = 0
        self._draw_wheel()
        self.canvas_hist.delete("all")
        self.lbl_result.config(text="Place your bets!", fg=GOLD)
        self.lbl_status.config(text="New game started!", fg=WIN_COLOR)
        self.btn_spin.config(state="normal", bg=GOLD)

    def _clear_bet_markers(self):
        for item_id in self.bet_markers:
            self.canvas_table.delete(item_id)
        self.bet_markers.clear()

    def _update_balance_display(self):
        self.lbl_balance.config(text=f"💰  Balance: ${self.game.balance:,}")

    def _update_bet_display(self):
        total = self.game.total_bet()
        self.lbl_total_bet.config(text=f"Total Bet: ${total:,}")


# ──────────────────────────── ENTRY POINT ─────────────────────────

if __name__ == "__main__":
    app = RouletteApp()
    app.mainloop()
