# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — 工程進度甘特圖產生器
依據：工程報價單 (2026/5/23, 總金額 NT$16,729,761)、施工圖、3D 設計簡報

說明：本排程為「規劃建議版」。
假設條件：
  - 開工日 = 2026/06/29（簽約後約 2 週備料、待確認項目決議、施工申請）
  - 每週 6 個工作天；社區規範工時 08:00-12:00 / 13:00-17:00
  - 不含且需業主另行界定之工項：泥作防水(尚未評估)、地坪、空調、油漆
"""
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import font_manager as fm

# ---------- 中文字型 ----------
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
try:
    fm.fontManager.addfont(FONT)
    _name = fm.FontProperties(fname=FONT).get_name()
except Exception:
    _name = "sans-serif"
plt.rcParams["font.family"] = _name
plt.rcParams["axes.unicode_minus"] = False

D = lambda s: dt.datetime.strptime(s, "%Y-%m-%d")

# ---------- 階段配色 ----------
PHASE_COLOR = {
    "前置作業":   "#8E9AAF",
    "假設/拆除":  "#B0855B",
    "結構(頂樓)": "#6D6875",
    "泥作防水":   "#5C8A8A",
    "水電":       "#4F86C6",
    "天花輕鋼架": "#5AA9A3",
    "木作":       "#C08552",
    "石材":       "#7D7D7D",
    "磁磚":       "#A26769",
    "油漆(業主)": "#9AA0A6",
    "系統櫃/櫃體":"#D08C42",
    "收尾/設備":  "#6AAE6F",
    "完工驗收":   "#2E7D32",
}

# 任務： (階段, 名稱, 起, 迄, 是否關鍵路徑)
TASKS = [
    ("前置作業", "施工圖深化 / 圖說會審",                 "2026-06-16", "2026-07-03", False),
    ("前置作業", "待確認項目決議(泥作/地坪/空調/油漆/防火門)", "2026-06-16", "2026-06-26", True),
    ("前置作業", "長交期發包下單(石材/系統櫃/廠製門/鋼構/設備)", "2026-06-22", "2026-07-17", True),
    ("前置作業", "室內裝修 / 社區施工申請許可",            "2026-06-16", "2026-07-03", False),

    ("假設/拆除", "保護工程 + 鷹架搭設(滿堂/活動/樓梯架)",   "2026-06-29", "2026-07-11", True),
    ("假設/拆除", "拆除工程(RC 開門/窗孔、舊門框)",          "2026-07-06", "2026-07-11", False),

    ("結構(頂樓)", "頂樓加蓋鋼構(吊裝/角浪/壁板/落地窗)",     "2026-07-06", "2026-08-15", False),

    ("泥作防水", "泥作打底 + 防水(濕區/開孔/收邊)〔需確認〕",  "2026-07-13", "2026-08-08", True),

    ("水電", "水電配管配線(總電源/迴路/出線/弱電)1F→3F",     "2026-07-13", "2026-08-22", True),

    ("天花輕鋼架", "輕鋼架天花 1F(餐廳/大廳/廁所等)",         "2026-08-03", "2026-08-22", False),
    ("天花輕鋼架", "輕鋼架天花 2F(含夾層/主會堂)",            "2026-08-10", "2026-08-29", True),
    ("天花輕鋼架", "輕鋼架天花 3F(主會堂80坪/副堂/交誼廳)",    "2026-08-17", "2026-09-05", True),
    ("天花輕鋼架", "消防/空調 天花內整合(封板前)〔界面〕",      "2026-08-10", "2026-09-05", True),

    ("木作", "木作-天花垂板/包樑/講台天花",                  "2026-08-24", "2026-09-19", True),
    ("木作", "木作-架高地板/壁面木皮/格柵/反射板",            "2026-09-07", "2026-10-03", True),
    ("木作", "門窗(廠製門/固定窗/會堂門)",                   "2026-09-14", "2026-10-03", False),
    ("木作", "木作-佈告欄/傢俱櫃體",                        "2026-09-21", "2026-10-10", False),

    ("石材", "石材-地坪(講台/教員辦公室/音控室)",            "2026-09-14", "2026-10-03", False),
    ("石材", "石材-壁面(主會堂/副堂 1,285才)",              "2026-09-21", "2026-10-24", True),
    ("石材", "石材-踢腳/講桌/花台",                         "2026-10-12", "2026-10-24", False),
    ("石材", "地坪花崗岩白華研磨美容(150坪)",                "2026-10-19", "2026-11-07", False),

    ("磁磚", "大板磚 FMG(1F 大廳主牆)",                     "2026-10-05", "2026-10-17", False),

    ("油漆(業主)", "油漆批土/塗裝(業主自辦)〔需界定〕",        "2026-10-05", "2026-10-31", True),

    ("系統櫃/櫃體", "系統櫃(聖器室/吧台/大廳櫃/辦公)",         "2026-10-19", "2026-11-07", True),
    ("系統櫃/櫃體", "被褥櫃 56 組 + 床組(金屬床架+床板)",       "2026-10-26", "2026-11-14", True),

    ("收尾/設備", "人造石檯面",                              "2026-11-02", "2026-11-14", False),
    ("收尾/設備", "玻璃 / 鏡",                               "2026-11-02", "2026-11-14", False),
    ("收尾/設備", "照明燈具安裝",                            "2026-11-02", "2026-11-21", True),
    ("收尾/設備", "消防設備延伸 / 系統測試",                  "2026-11-02", "2026-11-14", False),
    ("收尾/設備", "設備(飲水機/水槽/冰箱/烘碗機/各式扇/防墜網/機櫃)", "2026-11-09", "2026-11-28", True),
    ("收尾/設備", "窗簾(防火捲簾/百葉)/訂製家飾",             "2026-11-16", "2026-11-28", False),
    ("收尾/設備", "銘版/白板/活動家具進場",                  "2026-11-16", "2026-11-28", False),

    ("完工驗收", "粗清 + 細清(549坪)",                       "2026-11-23", "2026-12-05", True),
    ("完工驗收", "驗收 / 缺失改善",                          "2026-11-30", "2026-12-12", True),
]

# 里程碑： (名稱, 日期)
MILESTONES = [
    ("開工", "2026-06-29"),
    ("天花封板前整合完成", "2026-09-05"),
    ("主會堂石材完成", "2026-10-24"),
    ("系統櫃/床組完成", "2026-11-14"),
    ("交屋", "2026-12-12"),
]

TODAY = "2026-06-15"

# ---------- 繪圖 ----------
fig, ax = plt.subplots(figsize=(19, 13))
n = len(TASKS)
bar_h = 0.62

for i, (phase, name, s, e, crit) in enumerate(TASKS):
    y = n - i  # 由上而下
    start = mdates.date2num(D(s))
    width = mdates.date2num(D(e)) - start
    ax.barh(y, width, left=start, height=bar_h,
            color=PHASE_COLOR[phase],
            edgecolor=("#C0392B" if crit else "white"),
            linewidth=(2.2 if crit else 0.6),
            zorder=3, alpha=0.95)
    # 任務名稱
    ax.text(start - 2, y, name, ha="right", va="center", fontsize=10.5, zorder=4)
    # 關鍵路徑星號
    if crit:
        ax.text(start + width + 1.5, y, "★", ha="left", va="center",
                fontsize=11, color="#C0392B", zorder=4)

# 里程碑（菱形 + 標籤）
for name, d in MILESTONES:
    x = mdates.date2num(D(d))
    ax.scatter(x, 0.2, marker="D", s=120, color="#1A237E", zorder=6, clip_on=False)
    ax.text(x, -0.7, f"{name}\n{D(d).strftime('%m/%d')}", ha="center", va="top",
            fontsize=9, color="#1A237E", zorder=6)

# 今日線
tx = mdates.date2num(D(TODAY))
ax.axvline(tx, color="#C0392B", linestyle="--", linewidth=1.6, zorder=5)
ax.text(tx, n + 1.2, f"今日 {D(TODAY).strftime('%Y/%m/%d')}", color="#C0392B",
        ha="center", va="bottom", fontsize=10, fontweight="bold")

# 軸線設定
ax.set_ylim(-3, n + 2)
ax.set_xlim(mdates.date2num(D("2026-06-10")), mdates.date2num(D("2026-12-22")))
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

# 月份淡色帶（隔月）
months = list(mdates.MonthLocator().tick_values(D("2026-06-01"), D("2026-12-31")))
for k in range(len(months) - 1):
    if k % 2 == 0:
        ax.axvspan(months[k], months[k + 1], color="#f5f6f8", zorder=0)

# 標題
ax.set_title("碧侯教會 室內裝修工程  —  工程進度甘特圖（規劃建議版）",
             fontsize=20, fontweight="bold", pad=34)
fig.text(0.5, 0.935,
         "總金額 NT$16,729,761（含監管費 10% + 營業稅）｜ 3 層樓 + 頂樓加蓋 ｜ 約 549 坪 ｜ 報價日 2026/05/23",
         ha="center", fontsize=11, color="#555")

# 圖例（置於右上空白區，避開任務條與里程碑標籤）
legend_items = [Patch(facecolor=c, label=p) for p, c in PHASE_COLOR.items()]
legend_items += [
    Patch(facecolor="white", edgecolor="#C0392B", linewidth=2.2, label="★ 關鍵路徑"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor="#1A237E",
           markersize=10, label="里程碑"),
    Line2D([0], [0], color="#C0392B", linestyle="--", label="今日"),
]
ax.legend(handles=legend_items, loc="upper right", ncol=2, fontsize=9.5,
          framealpha=0.96, edgecolor="#cccccc", title="圖例")

fig.text(0.012, 0.012,
         "假設：開工 2026/06/29、週 6 工作天。〔需確認/界定〕之泥作防水、地坪、空調、油漆未含於本合約，"
         "須先確認施作介面與廠商，否則影響關鍵路徑。本圖為規劃版，實際依現場與備料進度滾動調整。",
         fontsize=8.5, color="#777")

plt.subplots_adjust(left=0.30, right=0.985, top=0.91, bottom=0.10)
out = "docs/工程進度甘特圖.png"
plt.savefig(out, dpi=150, facecolor="white")
print("saved:", out)
