# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — 工程進度甘特圖產生器
資料來源：schedule_data.py（單一來源；改開工日只需改該檔 PROTECTION_START）

本版：進場保護日 = 2026/06/19（業主指定）
"""
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import font_manager as fm

import schedule_data as S

# ---------- 中文字型 ----------
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
try:
    fm.fontManager.addfont(FONT)
    _name = fm.FontProperties(fname=FONT).get_name()
except Exception:
    _name = "sans-serif"
plt.rcParams["font.family"] = _name
plt.rcParams["axes.unicode_minus"] = False

TASKS = S.tasks()
MILESTONES = S.milestones()

# ---------- 繪圖 ----------
fig, ax = plt.subplots(figsize=(19, 13))
n = len(TASKS)
bar_h = 0.62

for i, (phase, name, s, e, crit, dep, note, wd) in enumerate(TASKS):
    y = n - i
    start = mdates.date2num(s)
    width = mdates.date2num(e) - start
    ax.barh(y, width, left=start, height=bar_h,
            color=S.PHASE_COLOR[phase],
            edgecolor=("#C0392B" if crit else "white"),
            linewidth=(2.2 if crit else 0.6),
            zorder=3, alpha=0.95)
    ax.text(start - 2, y, name, ha="right", va="center", fontsize=10.5, zorder=4)
    if crit:
        ax.text(start + width + 1.5, y, "★", ha="left", va="center",
                fontsize=11, color="#C0392B", zorder=4)

for name, d in MILESTONES:
    x = mdates.date2num(d)
    ax.scatter(x, 0.2, marker="D", s=120, color="#1A237E", zorder=6, clip_on=False)
    ax.text(x, -0.7, f"{name}\n{d.strftime('%m/%d')}", ha="center", va="top",
            fontsize=9, color="#1A237E", zorder=6)

# 今日線
tx = mdates.date2num(S._d(S.TODAY))
ax.axvline(tx, color="#C0392B", linestyle="--", linewidth=1.6, zorder=5)
ax.text(tx, n + 1.2, f"今日 {S._d(S.TODAY).strftime('%Y/%m/%d')}", color="#C0392B",
        ha="center", va="bottom", fontsize=10, fontweight="bold")

# 軸線
ax.set_ylim(-3, n + 2)
ax.set_xlim(mdates.date2num(S._d("2026-05-31")), mdates.date2num(S._d("2026-12-14")))
ax.set_yticks([])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y\n%m月"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.grid(axis="x", which="major", color="#9e9e9e", linewidth=0.9, alpha=0.7)
ax.grid(axis="x", which="minor", color="#dddddd", linewidth=0.5, alpha=0.7)
ax.set_axisbelow(True)
ax.tick_params(axis="x", labelsize=11)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

months = list(mdates.MonthLocator().tick_values(S._d("2026-05-01"), S._d("2026-12-31")))
for k in range(len(months) - 1):
    if k % 2 == 0:
        ax.axvspan(months[k], months[k + 1], color="#f5f6f8", zorder=0)

ax.set_title("碧侯教會 室內裝修工程  —  工程進度甘特圖（規劃建議版）",
             fontsize=20, fontweight="bold", pad=34)
fig.text(0.5, 0.935,
         "總金額 NT$16,729,761（含監管費 10% + 營業稅）｜ 3 層樓 + 頂樓加蓋 ｜ 約 549 坪 ｜ "
         f"進場保護日 {S._d(S.PROTECTION_START).strftime('%Y/%m/%d')}",
         ha="center", fontsize=11, color="#555")

legend_items = [Patch(facecolor=c, label=p) for p, c in S.PHASE_COLOR.items()]
legend_items += [
    Patch(facecolor="white", edgecolor="#C0392B", linewidth=2.2, label="★ 關鍵路徑"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor="#1A237E",
           markersize=10, label="里程碑"),
    Line2D([0], [0], color="#C0392B", linestyle="--", label="今日"),
]
ax.legend(handles=legend_items, loc="upper right", ncol=2, fontsize=9.5,
          framealpha=0.96, edgecolor="#cccccc", title="圖例")

fig.text(0.012, 0.012,
         "假設：進場保護 2026/06/19、週 6 工作天，預估 2026/12/02 交屋。〔需確認/界定〕之泥作防水、地坪、空調、"
         "油漆未含於本合約，須先確認施作介面與廠商，否則影響關鍵路徑。本圖為規劃版，依現場與備料進度滾動調整。",
         fontsize=8.5, color="#777")

plt.subplots_adjust(left=0.30, right=0.985, top=0.91, bottom=0.10)
out = "docs/工程進度甘特圖.png"
plt.savefig(out, dpi=150, facecolor="white")
print("saved:", out)
