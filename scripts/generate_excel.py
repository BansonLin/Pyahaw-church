# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — Excel 工程進度表 / 甘特圖 產生器
資料來源：schedule_data.py
輸出：docs/工程進度甘特圖.xlsx
  工作表：甘特圖(週曆式) / 工程進度表 / 預算總覽 / 工程安排建議
"""
import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import schedule_data as S

THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CRIT_FILL = PatternFill("solid", fgColor="C0392B")
TODAY_FILL = PatternFill("solid", fgColor="FDE7E7")
TODAY_HEAD = PatternFill("solid", fgColor="C0392B")
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
MONTH_FILL = PatternFill("solid", fgColor="2E4D7B")
MS_FILL = PatternFill("solid", fgColor="1A237E")
WHITE = Font(color="FFFFFF", bold=True)

def monday_of(d: dt.datetime) -> dt.datetime:
    return d - dt.timedelta(days=d.weekday())

def hex_fill(h):
    return PatternFill("solid", fgColor=h.lstrip("#"))

TASKS = S.tasks()
MILES = S.milestones()
TODAY = S._d(S.TODAY)

# 時間軸（週）
all_starts = [t[2] for t in TASKS]
all_ends = [t[3] for t in TASKS]
grid_start = monday_of(min(all_starts))
last = max(all_ends + [d for _, d in MILES])
n_weeks = ((monday_of(last) - grid_start).days // 7) + 2

def week_idx(d: dt.datetime) -> int:
    return (monday_of(d) - grid_start).days // 7

wb = Workbook()

# ============================================================
# 工作表 1：甘特圖（週曆式）
# ============================================================
ws = wb.active
ws.title = "甘特圖"
FIRST_WK_COL = 7  # G

# 標題
ws.cell(1, 1, "碧侯教會 室內裝修工程 — 工程進度甘特圖（規劃建議版）").font = Font(bold=True, size=16)
ws.cell(2, 1, f"總金額 NT$16,729,761｜3層樓+頂樓加蓋｜約549坪｜進場保護日 "
              f"{S._d(S.PROTECTION_START).strftime('%Y/%m/%d')}｜預估 "
              f"{(max(all_ends)).strftime('%Y/%m/%d')} 交屋").font = Font(size=10, color="555555")

# 表頭
HEAD_ROW = 4
WEEK_ROW = 5
heads = ["階段", "工項", "開始", "結束", "工作天", "關鍵"]
for c, h in enumerate(heads, start=1):
    cell = ws.cell(HEAD_ROW, c, h)
    cell.fill = HEAD_FILL; cell.font = WHITE
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(WEEK_ROW, c).fill = HEAD_FILL
# 合併固定欄表頭(跨兩列)
for c in range(1, 7):
    ws.merge_cells(start_row=HEAD_ROW, start_column=c, end_row=WEEK_ROW, end_column=c)

# 月份列 + 週列
cur_month = None; month_start_col = None
for w in range(n_weeks):
    col = FIRST_WK_COL + w
    wk_mon = grid_start + dt.timedelta(weeks=w)
    # 週標(該週週一 月/日)
    wcell = ws.cell(WEEK_ROW, col, f"{wk_mon.month}/{wk_mon.day}")
    wcell.font = Font(size=8, color="FFFFFF", bold=(week_idx(TODAY) == w))
    wcell.alignment = Alignment(horizontal="center")
    wcell.fill = TODAY_HEAD if week_idx(TODAY) == w else MONTH_FILL
    # 月份分組
    m = wk_mon.month
    if m != cur_month:
        if cur_month is not None:
            ws.merge_cells(start_row=HEAD_ROW, start_column=month_start_col,
                           end_row=HEAD_ROW, end_column=col - 1)
        cur_month = m; month_start_col = col
        mc = ws.cell(HEAD_ROW, col, f"{wk_mon.year}/{m}月")
        mc.fill = MONTH_FILL; mc.font = Font(size=9, color="FFFFFF", bold=True)
        mc.alignment = Alignment(horizontal="center")
ws.merge_cells(start_row=HEAD_ROW, start_column=month_start_col,
               end_row=HEAD_ROW, end_column=FIRST_WK_COL + n_weeks - 1)

# 任務列
r = WEEK_ROW + 1
for (phase, name, s, e, crit, dep, note, wd) in TASKS:
    ws.cell(r, 1, phase).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(r, 1).fill = hex_fill(S.PHASE_COLOR[phase])
    ws.cell(r, 1).font = Font(color="FFFFFF", size=9, bold=True)
    ws.cell(r, 2, name).font = Font(size=10, bold=crit)
    cs = ws.cell(r, 3, s); cs.number_format = "m/d"; cs.alignment = Alignment(horizontal="center")
    ce = ws.cell(r, 4, e); ce.number_format = "m/d"; ce.alignment = Alignment(horizontal="center")
    ws.cell(r, 5, wd).alignment = Alignment(horizontal="center")
    if crit:
        kc = ws.cell(r, 6, "★"); kc.font = Font(color="C0392B", bold=True)
        kc.alignment = Alignment(horizontal="center")
    # 條
    fill = hex_fill(S.PHASE_COLOR[phase])
    a, b = week_idx(s), week_idx(e)
    for w in range(a, b + 1):
        cell = ws.cell(r, FIRST_WK_COL + w)
        cell.fill = fill
        if crit:
            cell.border = Border(top=Side(style="thin", color="C0392B"),
                                 bottom=Side(style="thin", color="C0392B"))
    # 今日欄淡色（不覆蓋條）
    tcol = FIRST_WK_COL + week_idx(TODAY)
    if not (a <= week_idx(TODAY) <= b):
        ws.cell(r, tcol).fill = TODAY_FILL
    r += 1

# 里程碑列
ms_row = r + 1
ws.cell(ms_row, 2, "◆ 里程碑").font = Font(bold=True, color="1A237E")
for name, d in MILES:
    cell = ws.cell(ms_row, FIRST_WK_COL + week_idx(d), "◆")
    cell.font = Font(color="1A237E", bold=True, size=12)
    cell.alignment = Alignment(horizontal="center")
# 里程碑清單
lr = ms_row + 2
ws.cell(lr, 2, "里程碑").font = Font(bold=True)
ws.cell(lr, 3, "目標日").font = Font(bold=True)
for i, (name, d) in enumerate(MILES, start=1):
    ws.cell(lr + i, 2, name)
    c = ws.cell(lr + i, 3, d); c.number_format = "yyyy/m/d"

# 階段圖例
leg = lr + len(MILES) + 2
ws.cell(leg, 2, "階段圖例").font = Font(bold=True)
for i, (p, col) in enumerate(S.PHASE_COLOR.items()):
    cc = ws.cell(leg + 1 + i, 2, p)
    ws.cell(leg + 1 + i, 1).fill = hex_fill(col)

# 版面
ws.column_dimensions["A"].width = 12
ws.column_dimensions["B"].width = 42
ws.column_dimensions["C"].width = 8
ws.column_dimensions["D"].width = 8
ws.column_dimensions["E"].width = 7
ws.column_dimensions["F"].width = 5
for w in range(n_weeks):
    ws.column_dimensions[get_column_letter(FIRST_WK_COL + w)].width = 3.1
ws.freeze_panes = ws.cell(WEEK_ROW + 1, FIRST_WK_COL)
ws.sheet_view.showGridLines = False

# ============================================================
# 工作表 2：工程進度表（明細）
# ============================================================
ws2 = wb.create_sheet("工程進度表")
cols = ["#", "階段", "工項", "開始", "結束", "工作天", "關鍵路徑", "前置作業", "備註"]
widths = [5, 12, 44, 12, 12, 9, 10, 18, 26]
for c, (h, w) in enumerate(zip(cols, widths), start=1):
    cell = ws2.cell(1, c, h); cell.fill = HEAD_FILL; cell.font = WHITE
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws2.column_dimensions[get_column_letter(c)].width = w
for i, (phase, name, s, e, crit, dep, note, wd) in enumerate(TASKS, start=1):
    row = i + 1
    ws2.cell(row, 1, i).alignment = Alignment(horizontal="center")
    pc = ws2.cell(row, 2, phase); pc.fill = hex_fill(S.PHASE_COLOR[phase])
    pc.font = Font(color="FFFFFF", size=9, bold=True); pc.alignment = Alignment(horizontal="center")
    ws2.cell(row, 3, name).font = Font(bold=crit)
    c1 = ws2.cell(row, 4, s); c1.number_format = "yyyy/m/d"; c1.alignment = Alignment(horizontal="center")
    c2 = ws2.cell(row, 5, e); c2.number_format = "yyyy/m/d"; c2.alignment = Alignment(horizontal="center")
    ws2.cell(row, 6, wd).alignment = Alignment(horizontal="center")
    kc = ws2.cell(row, 7, "★ 是" if crit else ""); kc.alignment = Alignment(horizontal="center")
    if crit: kc.font = Font(color="C0392B", bold=True)
    ws2.cell(row, 8, dep)
    ws2.cell(row, 9, note)
    for c in range(1, 10):
        ws2.cell(row, c).border = BORDER
ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:I{len(TASKS)+1}"

# ============================================================
# 工作表 3：預算總覽
# ============================================================
ws3 = wb.create_sheet("預算總覽")
ws3.cell(1, 1, "碧侯教會 室內裝修工程 — 工項預算總覽（依報價單 2026/05/23）").font = Font(bold=True, size=13)
heads3 = ["項次", "工程項目", "金額 (NT$)", "備註"]
w3 = [6, 40, 16, 34]
for c, (h, w) in enumerate(zip(heads3, w3), start=1):
    cell = ws3.cell(3, c, h); cell.fill = HEAD_FILL; cell.font = WHITE
    cell.alignment = Alignment(horizontal="center")
    ws3.column_dimensions[get_column_letter(c)].width = w
row = 4
for no, name, amt, note in S.BUDGET:
    ws3.cell(row, 1, no).alignment = Alignment(horizontal="center")
    ws3.cell(row, 2, name)
    if amt is None:
        ac = ws3.cell(row, 3, "—"); ac.alignment = Alignment(horizontal="right")
    else:
        ac = ws3.cell(row, 3, amt); ac.number_format = "#,##0"
    ws3.cell(row, 4, note).font = Font(color="C0392B" if (amt is None and note in
             ("尚未評估", "未含")) else "000000")
    for c in range(1, 5):
        ws3.cell(row, c).border = BORDER
    row += 1
def total_row(label, value, bold=True, fill=None):
    global row
    ws3.cell(row, 2, label).font = Font(bold=bold)
    v = ws3.cell(row, 3, value); v.number_format = "#,##0"; v.font = Font(bold=bold)
    v.alignment = Alignment(horizontal="right")
    if fill:
        for c in range(1, 5): ws3.cell(row, c).fill = fill
    row += 1
row += 0
total_row("合計", S.SUBTOTAL)
total_row("監管費（工程款 10%）", S.SUPERVISION, bold=False)
total_row("營業稅（5%）", S.TAX, bold=False)
total_row("總金額", S.TOTAL, fill=PatternFill("solid", fgColor="FFF2CC"))

# ============================================================
# 工作表 4：工程安排建議
# ============================================================
ws4 = wb.create_sheet("工程安排建議")
ws4.column_dimensions["A"].width = 4
ws4.column_dimensions["B"].width = 110
advice = [
    ("title", "碧侯教會 室內裝修工程 — 工程安排建議（摘要）"),
    ("", ""),
    ("h", "最該優先處理的 5 件事"),
    ("n", "1. 先封口「合約未含 4 工項」：泥作防水(尚未評估)、地坪、空調、油漆 — 皆在關鍵路徑/隱蔽界面，開工前務必界定範圍、廠商、費用。"),
    ("n", "2. 長交期項目立刻發包：石材、系統櫃(56被褥櫃+床組)、廠製門、頂樓鋼構、設備；偏遠工地運輸提前 4~8 週。"),
    ("n", "3. 以 2F 主會堂為核心：鷹架(6.8M)+80坪天花+花崗岩壁/地/講台+木作反射板疊在同一空間，集中資源、嚴控工序交接。"),
    ("n", "4. 鷹架一次到位：高處工項(天花、上部石材、油漆、燈具)排同一鷹架週期，避免重複搭拆。"),
    ("n", "5. 天花封板前完成消防/空調整合：不可逆隱蔽工程，錯過要拆天花重做。"),
    ("", ""),
    ("h", "合約未含 / 待評估工項（風險第一）"),
    ("n", "泥作/防水(尚未評估)：石材/磁磚/地坪都要等它；濕區須試水。排在拆除後、天花前。"),
    ("n", "地坪(未含)：影響石材踢腳收頭與櫃體立面高程；確認施作者、材質與完成面標高。"),
    ("n", "空調(未含)：室內外機/管線多在天花內，務必封板前定位點位。"),
    ("n", "油漆(未含)：介於木作之後、燈具/細清之前，漏排會卡住收尾，須排入時程。"),
    ("n", "待確認/取消：電視、投影機、洗衣機、淋浴門、二三樓玻璃門(不符法規暫取消)、防火門待評估 — 彙整清單逐項以追加減結案。"),
    ("", ""),
    ("h", "施工順序（單一空間）"),
    ("n", "保護/鷹架→拆除→泥作打底/防水→水電配管→輕鋼架天花骨架→(消防/空調整合)→封板→木作底→石材/磁磚→木作面/油漆→系統櫃→人造石/玻璃→燈具/設備→窗簾/家飾→清潔→驗收"),
    ("", ""),
    ("h", "分樓層流水"),
    ("n", "濕程/水電/天花：由下而上 1F→3F；完成面收尾(油漆後)：由上而下 3F→1F 退場保護下層。各工班用 3 週前置看板滾動排程。"),
    ("", ""),
    ("h", "品質 / 安全 / 管控"),
    ("n", "每週工地會議＋月進度查核對照甘特圖；請款綁里程碑(開工/天花/石材/櫃體/交屋)。"),
    ("n", "高架作業(主會堂6.8M、頂樓吊裝、梯間防墜網)落實安全；教會若需部分使用採分區圍封。"),
    ("n", "頂樓鋼構為室外作業，雨季預留緩衝；偏遠運輸預留彈性；成品保護至細清前不拆。"),
    ("", ""),
    ("n", "※ 本建議為規劃版。詳見 docs/工程安排建議.md。開工日假設 2026/06/19、週6工作天，實際依現場、備料、天候與業主決議滾動調整。"),
]
rr = 1
for kind, text in advice:
    cell = ws4.cell(rr, 2, text)
    if kind == "title":
        cell.font = Font(bold=True, size=15)
    elif kind == "h":
        cell.font = Font(bold=True, size=12, color="1F3864")
    else:
        cell.font = Font(size=10)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    rr += 1

# ============================================================
# 工作表 5：分區進場時程（週曆式，rows=區域）
# ============================================================
ws5 = wb.create_sheet("分區進場時程")
ZF = 8  # 第一個週欄 (H)
ws5.cell(1, 1, "碧侯教會 室內裝修工程 — 分區進場時程（各區工序對應實際日期）").font = Font(bold=True, size=15)
ws5.cell(2, 1, "色塊＝該區當期工種；依進場順位排列。開工(進場保護) 2026/06/19。").font = Font(size=10, color="555555")
zheads = ["順位", "樓層", "區域", "類型", "進場", "退場", "週"]
for c, h in enumerate(zheads, start=1):
    cell = ws5.cell(4, c, h); cell.fill = HEAD_FILL; cell.font = WHITE
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws5.merge_cells(start_row=4, start_column=c, end_row=5, end_column=c)
# 月/週表頭
curm = None; mstart = None
for w in range(n_weeks):
    col = ZF + w
    wk = grid_start + dt.timedelta(weeks=w)
    wc = ws5.cell(5, col, f"{wk.month}/{wk.day}")
    wc.font = Font(size=8, color="FFFFFF", bold=(week_idx(TODAY) == w))
    wc.alignment = Alignment(horizontal="center")
    wc.fill = TODAY_HEAD if week_idx(TODAY) == w else MONTH_FILL
    if wk.month != curm:
        if curm is not None:
            ws5.merge_cells(start_row=4, start_column=mstart, end_row=4, end_column=col - 1)
        curm = wk.month; mstart = col
        mc = ws5.cell(4, col, f"{wk.year}/{curm}月")
        mc.fill = MONTH_FILL; mc.font = Font(size=9, color="FFFFFF", bold=True)
        mc.alignment = Alignment(horizontal="center")
ws5.merge_cells(start_row=4, start_column=mstart, end_row=4, end_column=ZF + n_weeks - 1)

r = 6
for (floor, name, typ, enter, exit_, weeks, ps, order) in S.zones():
    ws5.cell(r, 1, order).alignment = Alignment(horizontal="center")
    fc = ws5.cell(r, 2, floor); fc.alignment = Alignment(horizontal="center")
    ws5.cell(r, 3, name).font = Font(bold=("★" in name))
    ws5.cell(r, 4, typ).alignment = Alignment(horizontal="center")
    e1 = ws5.cell(r, 5, enter); e1.number_format = "m/d"; e1.alignment = Alignment(horizontal="center")
    e2 = ws5.cell(r, 6, exit_); e2.number_format = "m/d"; e2.alignment = Alignment(horizontal="center")
    ws5.cell(r, 7, weeks).alignment = Alignment(horizontal="center")
    # 分段上色
    for j, (trade, start) in enumerate(ps):
        seg_end = ps[j + 1][1] if j + 1 < len(ps) else exit_
        a = week_idx(start); b = week_idx(seg_end)
        for w in range(a, max(a + 1, b)):
            ws5.cell(r, ZF + w).fill = hex_fill(S.SEG_COLOR[trade])
        lc = ws5.cell(r, ZF + a)
        lc.value = trade
        lc.font = Font(size=7, color=("222222" if trade in ("人造石","燈具","鷹架") else "FFFFFF"))
    r += 1

ws5.column_dimensions["A"].width = 5
ws5.column_dimensions["B"].width = 6
ws5.column_dimensions["C"].width = 34
ws5.column_dimensions["D"].width = 7
ws5.column_dimensions["E"].width = 7
ws5.column_dimensions["F"].width = 7
ws5.column_dimensions["G"].width = 4
for w in range(n_weeks):
    ws5.column_dimensions[get_column_letter(ZF + w)].width = 3.4
ws5.freeze_panes = ws5.cell(6, ZF)
ws5.sheet_view.showGridLines = False
# 工種圖例
lg = r + 2
ws5.cell(lg, 3, "工種圖例").font = Font(bold=True)
for i, (k, c) in enumerate(S.SEG_COLOR.items()):
    ws5.cell(lg + 1 + i, 2).fill = hex_fill(c)
    ws5.cell(lg + 1 + i, 3, f"{k}：{S.SEG_LABEL[k]}")

import os
os.makedirs("docs", exist_ok=True)
out = "docs/工程進度甘特圖.xlsx"
wb.save(out)
print("saved:", out, "| weeks:", n_weeks, "| tasks:", len(TASKS), "| zones:", len(S.zones()))
