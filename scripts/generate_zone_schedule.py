# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — 分區進場時程圖 + 時程表
輸出：docs/分區進場時程圖.png、docs/分區進場時程表.md
資料來源：schedule_data.zones()（已對應甘特圖實際日期，開工 6/19）
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

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
try:
    fm.fontManager.addfont(FONT)
    _name = fm.FontProperties(fname=FONT).get_name()
except Exception:
    _name = "sans-serif"
plt.rcParams["font.family"] = _name
plt.rcParams["axes.unicode_minus"] = False

Z = S.zones()
FLOOR_TAG = {"頂樓": "#6D6875", "1F": "#4F86C6", "2F": "#5AA9A3", "3F": "#C08552", "全區": "#8E9AAF"}

# ---------- 圖 ----------
fig, ax = plt.subplots(figsize=(21, 12.5))
n = len(Z)
bar_h = 0.6

for i, (floor, name, typ, enter, exit_, weeks, ps, order) in enumerate(Z):
    y = n - i
    # 分段
    for j, (trade, start) in enumerate(ps):
        seg_end = ps[j + 1][1] if j + 1 < len(ps) else exit_
        x0 = mdates.date2num(start)
        w = mdates.date2num(seg_end) - x0
        if w <= 0:
            continue
        ax.barh(y, w, left=x0, height=bar_h, color=S.SEG_COLOR[trade],
                edgecolor="white", linewidth=0.5, zorder=3)
        if w >= 12:   # 夠寬才標字
            ax.text(x0 + w / 2, y, trade, ha="center", va="center",
                    fontsize=6.6, color=("#222" if trade in ("人造石","燈具","鷹架") else "white"),
                    zorder=4)
    # 左標：順位 + 樓層 + 區域
    ax.text(mdates.date2num(enter) - 3, y, f"{order:>2}. [{floor}] {name}",
            ha="right", va="center", fontsize=9.3, zorder=4,
            fontweight=("bold" if "★" in name else "normal"))
    # 退場旗標（用 ASCII > 避免字型缺字）
    ax.text(mdates.date2num(exit_) + 1.5, y, f"> {exit_.strftime('%m/%d')} 退場",
            ha="left", va="center", fontsize=7.4, color="#2E7D32", zorder=4)

# 今日線
tx = mdates.date2num(S._d(S.TODAY))
ax.axvline(tx, color="#C0392B", linestyle="--", linewidth=1.5, zorder=5)
ax.text(tx, n + 0.9, f"今日 {S._d(S.TODAY).strftime('%m/%d')}", color="#C0392B",
        ha="center", va="bottom", fontsize=9.5, fontweight="bold")

ax.set_ylim(0, n + 2)
ax.set_xlim(mdates.date2num(S._d("2026-06-14")), mdates.date2num(S._d("2026-12-07")))
ax.set_yticks([])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y\n%m月"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.grid(axis="x", which="major", color="#9e9e9e", linewidth=0.9, alpha=0.7)
ax.grid(axis="x", which="minor", color="#dddddd", linewidth=0.5, alpha=0.6)
ax.set_axisbelow(True)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
months = list(mdates.MonthLocator().tick_values(S._d("2026-06-01"), S._d("2026-12-31")))
for k in range(len(months) - 1):
    if k % 2 == 0:
        ax.axvspan(months[k], months[k + 1], color="#f5f6f8", zorder=0)

ax.set_title("碧侯教會 室內裝修工程 — 分區進場時程圖（各區工序對應實際日期）",
             fontsize=18, fontweight="bold", pad=26)
fig.text(0.5, 0.945, "色塊＝該區當期工種；左側數字＝進場順位；右側為退場(清潔完)日。開工(進場保護) 2026/06/19。",
         ha="center", fontsize=10.5, color="#555")

handles = [Patch(facecolor=c, label=f"{k}") for k, c in S.SEG_COLOR.items()]
handles += [Line2D([0],[0], color="#C0392B", linestyle="--", label="今日")]
ax.legend(handles=handles, loc="lower center", ncol=9, fontsize=8.4,
          bbox_to_anchor=(0.5, -0.085), frameon=True, edgecolor="#ccc", title="工種")

plt.subplots_adjust(left=0.235, right=0.99, top=0.9, bottom=0.10)
out_png = "docs/分區進場時程圖.png"
plt.savefig(out_png, dpi=150, facecolor="white")
print("saved:", out_png)

# ---------- 時程表 Markdown ----------
def md(d):
    return d.strftime("%m/%d") if d else ""

L = []
A = L.append
A("# 碧侯教會 室內裝修工程 — 分區進場時程表\n")
A("> 搭配圖檔：[分區進場時程圖.png](分區進場時程圖.png)　｜　開工(進場保護) **2026/06/19**、預計 **2026/12/02** 交屋")
A("> 將 10 種施工順序(T1~T10)對應到甘特圖實際日期，標出每區進場順位、各工序時點與退場日，供現場照表調度工班。\n")
A("| 順位 | 樓層 | 區域 | 類型 | 進場 | 天花封板 | 木作 | 石材 | 油漆 | 櫃體/床 | 收尾起 | 退場 | 在場週 |")
A("|--:|---|---|---|---|---|---|---|---|---|---|---|--:|")
for floor, name, typ, enter, exit_, weeks, ps, order in Z:
    A("| {o} | {fl} | {nm} | {tp} | {en} | {cl} | {wd} | {st} | {pt} | {cab} | {fin} | {ex} | {wk} |".format(
        o=order, fl=floor, nm=name, tp=typ,
        en=md(enter),
        cl=md(S.zone_phase_date(ps, {"天花"})),
        wd=md(S.zone_phase_date(ps, {"木作"})),
        st=md(S.zone_phase_date(ps, {"石材", "磁磚"})),
        pt=md(S.zone_phase_date(ps, {"油漆"})),
        cab=md(S.zone_phase_date(ps, S._CABINET)),
        fin=md(S.zone_phase_date(ps, S._FINISH)),
        ex=md(exit_), wk=weeks))
A("")
A("## 進場波次（依進場順位）\n")
A("- **W1（6/19~）**：主會堂(鷹架先行)、梯間/通廊(保護)、頂樓鋼構(室外平行)。")
A("- **W2（7/06~）**：1F 全區(廁所/餐廚/大廳/教室/寢室/辦公) 由下而上先啟動。")
A("- **W3（7/13~）**：2F 全區(主會堂續、大廳/教室/辦公/傳道房/廁所)。")
A("- **W4（7/22~）**：3F 全區(副堂/交誼廳/音控/寢室/廁所)。\n")
A("## 使用方式\n")
A("1. **縱看**找區域、**橫看**對日期，即知該區某週應進什麼工種。")
A("2. 同一週多區同工種 → 該工班需備足人力或分批；可作為**工班排程與請款估驗**依據。")
A("3. 〔石材〕跨主會堂/副堂/大廳/音控室，**統一放樣開料、分批進場**（偏遠工地降車次）。")
A("4. 〔油漆/空調/泥作防水〕為業主自辦/未含，須於各區對應時點前完成界定，否則該區順延。")
A("5. **退場(▸)由上而下**：3F(11/18)→2F(11/20)→1F(11/24)→梯廊(11/25)，保護已完成樓層。")

open("docs/分區進場時程表.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved: docs/分區進場時程表.md | zones:", n)
