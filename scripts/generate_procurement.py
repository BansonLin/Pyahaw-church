# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — 採購執行計畫
輸出：docs/採購時程倒推圖.png、docs/採購執行計畫建議.md
資料來源：schedule_data.procurement()（由需求進場日倒推下單/詢價）
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

P = S.procurement()
today = S._d(S.TODAY)
n = len(P)
urgent_n = sum(1 for x in P if x[7])

# ---------- 倒推圖 ----------
fig, ax = plt.subplots(figsize=(20, 15))
bar_h = 0.6
for i, (name, cat, need, po, kick, val, note, urg) in enumerate(P):
    y = n - i
    col = S.PROC_CAT_COLOR[cat]
    xk, xp, xn = mdates.date2num(kick), mdates.date2num(po), mdates.date2num(need)
    # 詢價決標期(淺) + 供應製作期(實)
    ax.barh(y, xp - xk, left=xk, height=bar_h, color=col, alpha=0.30, zorder=3)
    ax.barh(y, xn - xp, left=xp, height=bar_h, color=col, alpha=0.95, zorder=3)
    # 下單截止標記
    ax.plot([xp, xp], [y - bar_h/2, y + bar_h/2], color="#111", lw=1.4, zorder=5)
    # 進場端
    ax.text(xn + 1.5, y, "進場", ha="left", va="center", fontsize=6.8, color="#555", zorder=4)
    # 左標
    tag = "⚠ " if urg else ""
    ax.text(xk - 2, y, f"{tag}{name}", ha="right", va="center", fontsize=8.6,
            color=("#C0392B" if urg else "#222"),
            fontweight=("bold" if urg else "normal"), zorder=4)

tx = mdates.date2num(today)
ax.axvline(tx, color="#C0392B", linestyle="--", linewidth=1.7, zorder=6)
ax.text(tx, n + 1.4, f"今日 {today.strftime('%Y/%m/%d')}", color="#C0392B",
        ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_ylim(0, n + 2.5)
ax.set_xlim(mdates.date2num(S._d("2026-05-24")), mdates.date2num(S._d("2026-11-30")))
ax.set_yticks([])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y\n%m月"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.grid(axis="x", which="major", color="#9e9e9e", linewidth=0.9, alpha=0.7)
ax.grid(axis="x", which="minor", color="#dddddd", linewidth=0.5, alpha=0.6)
ax.set_axisbelow(True)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
months = list(mdates.MonthLocator().tick_values(S._d("2026-05-01"), S._d("2026-12-31")))
for k in range(len(months) - 1):
    if k % 2 == 0:
        ax.axvspan(months[k], months[k + 1], color="#f5f6f8", zorder=0)

ax.set_title("碧侯教會 室內裝修工程 — 採購時程倒推圖（由需求進場日反推下單/詢價）",
             fontsize=18, fontweight="bold", pad=24)
fig.text(0.5, 0.948,
         f"淺色＝詢價決標期；實色＝供應/製作/運輸期；│＝下單截止日。⚠ 與紅字＝詢價啟動日已到(今日 6/15)，"
         f"共 {urgent_n} 項須立即啟動。",
         ha="center", fontsize=10.5, color="#555")

handles = [Patch(facecolor=c, label=k) for k, c in S.PROC_CAT_COLOR.items()]
handles += [
    Line2D([0], [0], color="#111", lw=1.6, label="│ 下單截止日"),
    Line2D([0], [0], color="#C0392B", linestyle="--", label="今日"),
]
ax.legend(handles=handles, loc="lower right", ncol=2, fontsize=9.2,
          framealpha=0.95, edgecolor="#ccc", title="圖例")
fig.text(0.012, 0.012, "採購倒推為規劃值(含緩衝)；實際依詢價結果、供應商產能與偏遠運輸調整。",
         fontsize=8.5, color="#888")

plt.subplots_adjust(left=0.255, right=0.99, top=0.91, bottom=0.06)
out_png = "docs/採購時程倒推圖.png"
plt.savefig(out_png, dpi=150, facecolor="white")
print("saved:", out_png)

# ---------- 採購執行計畫建議.md ----------
def md(d):
    return d.strftime("%m/%d")

def money(v):
    return f"{v:,}" if v is not None else "—"

L = []
A = L.append
A("# 碧侯教會 室內裝修工程 — 採購執行計畫建議\n")
A("> 搭配圖檔：[採購時程倒推圖.png](採購時程倒推圖.png)　｜　開工(進場保護) **2026/06/19**、預計 **2026/12/02** 交屋")
A(f"> 報告日 {today.strftime('%Y/%m/%d')}。以**需求進場日**往回推算**下單截止日**與**詢價啟動日**，"
  f"目前共 **{urgent_n} 項**詢價啟動日已到、須**立即啟動**。\n")

A("## 一、採購總原則\n")
A("1. **倒推排程**：所有採購以「需求進場日 − 供應期 − 詢價決標期」回推啟動日，**寧早勿晚**，長交期項目優先。")
A("2. **關鍵路徑優先**：石材、系統櫃/床、廠製門、頂樓鋼構、照明為關鍵長交期(A 類)，主導工期，最優先發包。")
A("3. **先封口未含 4 項**：泥作防水、地坪、空調、油漆為業主自辦/未含，**須立即界定範圍再詢價**，否則卡關鍵路徑。")
A("4. **偏遠工地集中物流**：碧侯運距長，採『集中、分批、排定吊裝』，降低車次與二次搬運。")
A("5. **封樣先行**：石材、木皮、磁磚、玻璃、油漆色、布料須先封樣/送審核准，才可大量下單。\n")

A("## 二、採購分類（ABC / 發包型態）\n")
A("| 類別 | 內容 | 採購重點 |")
A("|---|---|---|")
A("| **關鍵長交期(A)** | 石材、系統櫃/被褥櫃、廠製門、頂樓鋼構、金屬床架、烘碗機、照明、FMG薄磚 | 金額高/工期長，**最優先**、需封樣與產能保留 |")
A("| **一般材料(B)** | 天花板材、木作主材、人造石、玻璃、白板、機櫃、設備、消防、捲簾、銘版、防墜網 | 中前置期，依倒推下單 |")
A("| **連工帶料分包** | 保護鷹架、拆除、水電、輕鋼架、木作、磁磚貼工、清潔 | 連工帶料工程發包，動員前決標 |")
A("| **業主自辦/未含** | 泥作防水、空調、地坪、油漆 | **先界定介面/範圍**再詢價，補回合約 |\n")

A("## 三、採購時程倒推表（核心）\n")
A("> 依「詢價啟動日」排序（最急在前）。狀態：🔴 立即＝啟動日已到；🟡 將到（30 日內）。\n")
A("| 採購包 | 類別 | 金額(NT$) | 需求進場 | 下單截止 | 詢價啟動 | 狀態 | 備註 |")
A("|---|---|---:|---|---|---|:--:|---|")
for name, cat, need, po, kick, val, note, urg in P:
    days = (kick - today).days
    if urg:
        st = "🔴 立即"
    elif days <= 30:
        st = "🟡 將到"
    else:
        st = f"{md(kick)}"
    short_cat = cat.replace("(A)", "").replace("(B)", "")
    A(f"| {name} | {short_cat} | {money(val)} | {md(need)} | {md(po)} | {md(kick)} | {st} | {note} |")
A("")

A("## 四、立即啟動清單（本週必辦）\n")
for name, cat, need, po, kick, val, note, urg in P:
    if urg:
        A(f"- **{name}**（{cat}）→ 下單截止 {md(po)}、需求進場 {md(need)}。{note}")
A("")

A("## 五、發包 / 下單波次\n")
A("- **W0 立即（6 月中）**：頂樓鋼構、保護鷹架、拆除、水電分包、泥作防水(界定)、空調(界定)、石材(詢價封樣)。")
A("- **W1（7 月初）**：輕鋼架(含板材)、天花板材、木作分包+主材、廠製門。")
A("- **W2（8 月初）**：系統櫃、被褥櫃+床板、防墜網、地坪(發包)。")
A("- **W3（9 月初）**：金屬床架、烘碗機、照明(含停產替代確認)、油漆(發包)、多媒體白板、機櫃、FMG確認。")
A("- **W4（10 月初）**：人造石、玻璃/鏡、設備、消防、防火捲簾、銘版、磁磚貼工、清潔。\n")

A("## 六、偏遠工地物流與進場交付\n")
A("1. **集中分批**：依『分區進場時程』排定各區材料到場週，避免零星車次。")
A("2. **排定吊裝日**：頂樓鋼構、石材、系統櫃/床組、大型設備需吊車/人力，預約並對應進場順序。")
A("3. **暫存與保護**：規劃工地內分層暫存區；石材、板材、櫃體到場即保護，先到先用避免堆置受損。")
A("4. **到場點驗**：依封樣/送審文件查驗品名、規格、數量、外觀，異常即退換，留紀錄。\n")

A("## 七、供應商管理與送審 / 封樣\n")
A("- **詢比議**：A 類至少 3 家詢價、比價、議價；保留產能與交期承諾(列入合約罰則)。")
A("- **封樣送審**：石材(雅典白消光/光面、小雕刻白)、天然白橡木皮、鐵杉、美耐板、FMG磚、玻璃(烤漆/灰鏡)、油漆色、布料 → 業主/設計核准後才下大單。")
A("- **施工圖/加工圖**：系統櫃、廠製門、鋼構、講台(石材+木作+金屬)需加工圖會審。")
A("- **認證文件**：防火捲簾/防火門之防火時效證明、消防器材審驗，提前備齊以利驗收。\n")

A("## 八、付款條件與現金流\n")
A("- **建議付款**：訂金 30% → 到場/進場 40% → 安裝完成 20% → 驗收尾款 10%（A 類大額拉高保留款）。")
A("- **對應業主估驗**：合約含監管費 10%(代表有監造/PM)，請款綁里程碑(開工/天花/石材/櫃體/交屋)分期估驗計價。")
A("- **現金流提醒**：7~9 月為長交期項目訂金高峰(石材/櫃/門/鋼構/設備)，須預先備妥資金。\n")

A("## 九、採購風險與對策\n")
A("| 風險 | 對策 |")
A("|---|---|")
A("| 未含 4 項(泥作防水/地坪/空調/油漆)未定義 | **本週**界定範圍與廠商，補入合約並排程 |")
A("| 長交期延誤(石材/櫃/門/鋼構) | 立即詢價、封樣、保留產能；交期列入合約罰則 |")
A("| 停產/型號不符(T5燈管、AICM平板燈、冰河石磚) | **提早確認替代品**並重新封樣/報價 |")
A("| 偏遠運輸/吊裝排程 | 集中分批、預約吊車、預留天候緩衝 |")
A("| 量大分批(56被褥櫃/62床板) | 分批生產進場，對應寢室完成面時點 |")
A("| 價格波動 / 誤工加成 | 報價註明社區壓縮工時有 2.5~4%/0.5hr 加成，控管工時規範 |")
A("| 取消/追加項目(電視/投影/淋浴門等) | 彙整待確認清單，逐項追加減正式變更 |\n")

A("## 十、採購控管工具\n")
A("- **採購總表(PO Log)**：採購包／供應商／金額／詢價啟動／下單／到場／驗收／付款 全程追蹤。")
A("- **週採購會議**：對照本倒推圖追蹤啟動/下單/到場狀態，落後即升級處理。")
A("- **RACI**：採購(R)、設計/監造(A 核准封樣)、業主(C 未含項決策)、工務(I 進場協調)。")

open("docs/採購執行計畫建議.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved: docs/採購執行計畫建議.md | packages:", n, "| urgent:", urgent_n)
