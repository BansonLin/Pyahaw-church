# -*- coding: utf-8 -*-
"""
碧侯教會 室內裝修工程 — 整合 PDF 報告產生器
輸出：docs/碧侯教會_工程規劃報告.pdf
內容：封面/摘要 → 預算 → 甘特圖 → 進度表 → 細部施工順序圖 → 分區進場時程圖/表 → 工程安排建議
"""
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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

PW, PH = 16.54, 11.69  # A3 橫向 (inch)
NAVY = "#1F3864"

def wrap_cjk(s, n):
    out, line = [], ""
    for ch in s:
        line += ch
        if ch == "\n":
            out.append(line.rstrip("\n")); line = ""
        elif len(line) >= n:
            out.append(line); line = ""
    if line:
        out.append(line)
    return out

def new_page(pdf, footer):
    fig = plt.figure(figsize=(PW, PH))
    fig.patch.set_facecolor("white")
    fig.text(0.012, 0.012, footer, fontsize=7.5, color="#999")
    fig.text(0.988, 0.012, "碧侯教會室內裝修工程 · 工程規劃報告", fontsize=7.5,
             color="#999", ha="right")
    return fig

def image_page(pdf, png, title, idx):
    fig = new_page(pdf, f"{idx}")
    fig.text(0.5, 0.965, title, ha="center", va="top", fontsize=17, fontweight="bold", color=NAVY)
    img = plt.imread(png)
    h, w = img.shape[0], img.shape[1]
    aspect = w / h
    # 可用區域 (figure fraction)
    ax_x, ax_y, ax_w, ax_h = 0.02, 0.03, 0.96, 0.88
    avail_w_in, avail_h_in = ax_w * PW, ax_h * PH
    if avail_w_in / avail_h_in > aspect:        # 高度受限
        draw_h = avail_h_in; draw_w = draw_h * aspect
    else:                                       # 寬度受限
        draw_w = avail_w_in; draw_h = draw_w / aspect
    fw, fh = draw_w / PW, draw_h / PH
    x0 = ax_x + (ax_w - fw) / 2
    y0 = ax_y + (ax_h - fh) / 2
    ax = fig.add_axes([x0, y0, fw, fh]); ax.axis("off")
    ax.imshow(img, aspect="auto")
    pdf.savefig(fig); plt.close(fig)

def table_page(pdf, title, col_labels, rows, idx, col_widths=None, fontsize=6.6,
               header_color=NAVY, note=None):
    fig = new_page(pdf, idx)
    fig.text(0.5, 0.965, title, ha="center", va="top", fontsize=17, fontweight="bold", color=NAVY)
    if note:
        fig.text(0.5, 0.93, note, ha="center", va="top", fontsize=9.5, color="#666")
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.88]); ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_labels, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(fontsize)
    nrow = len(rows) + 1
    tbl.scale(1, (0.88 * PH * 72) / (nrow * (fontsize + 6)))
    if col_widths:
        total = sum(col_widths)
        for (rr, cc), cell in tbl.get_celld().items():
            cell.set_width(col_widths[cc] / total)
    for (rr, cc), cell in tbl.get_celld().items():
        cell.set_edgecolor("#D0D0D0")
        if rr == 0:
            cell.set_facecolor(header_color); cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
        elif rr % 2 == 0:
            cell.set_facecolor("#F6F7F9")
    pdf.savefig(fig); plt.close(fig)

def text_page(pdf, title, blocks, idx):
    """blocks: list of (kind, text); kind in title/h/n"""
    fig = new_page(pdf, idx)
    fig.text(0.5, 0.965, title, ha="center", va="top", fontsize=17, fontweight="bold", color=NAVY)
    y = 0.90
    for kind, text in blocks:
        if kind == "h":
            y -= 0.012
            fig.text(0.06, y, text, fontsize=13, fontweight="bold", color=NAVY)
            y -= 0.030
        else:
            for ln in wrap_cjk(text, 58):
                fig.text(0.07, y, ln, fontsize=10.3, color="#222")
                y -= 0.0225
            y -= 0.006
    pdf.savefig(fig); plt.close(fig)

OUT = "docs/碧侯教會_工程規劃報告.pdf"
proto = S._d(S.PROTECTION_START).strftime("%Y/%m/%d")
handover = max(t[3] for t in S.tasks()).strftime("%Y/%m/%d")
today = dt.date.today().strftime("%Y/%m/%d")

with PdfPages(OUT) as pdf:
    # ---- 封面 ----
    fig = new_page(pdf, "封面")
    cax = fig.add_axes([0, 0, 1, 1]); cax.set_xlim(0, 1); cax.set_ylim(0, 1); cax.axis("off")
    cax.add_patch(plt.Rectangle((0, 0.80), 1, 0.20, facecolor=NAVY, edgecolor="none"))
    cax.add_patch(plt.Rectangle((0.11, 0.305), 0.78, 0.003, facecolor="#C0392B", edgecolor="none"))
    fig.text(0.5, 0.905, "碧侯教會 室內裝修工程", ha="center", va="center", color="white",
             fontsize=31, fontweight="bold")
    fig.text(0.5, 0.852, "工程規劃報告　Construction Planning Report", ha="center", va="center",
             color="#D9E2F3", fontsize=14)
    meta = [
        ("專案規模", "3 層樓 + 頂樓加蓋，約 549 坪"),
        ("總金額", "NT$ 16,729,761（工程款 14,484,642 + 監管費 10% + 營業稅）"),
        ("報價日 / 設計簡報", "2026/05/23　/　2026/01/26"),
        ("進場保護日（開工）", f"{proto}（業主指定）"),
        ("預估交屋", f"{handover}（總工期約 22～24 週）"),
        ("報告產出日", today),
    ]
    yy = 0.66
    for k, v in meta:
        fig.text(0.12, yy, k, fontsize=12.5, fontweight="bold", color=NAVY)
        fig.text(0.34, yy, v, fontsize=12.5, color="#222")
        yy -= 0.045
    fig.text(0.12, 0.33, "關鍵提醒", fontsize=14, fontweight="bold", color="#C0392B")
    risks = [
        "1. 合約未含/待評估 4 工項（泥作防水、地坪、空調、油漆）皆在關鍵路徑或隱蔽界面，開工前務必界定。",
        "2. 長交期項目（石材、系統櫃、廠製門、頂樓鋼構、設備）應立即發包；偏遠工地運輸提前備料。",
        "3. 2F 主會堂（鷹架＋80坪天花＋花崗岩＋木作）為資源最密集之關鍵空間，主導總工期。",
        "4. 天花封板前須完成消防/空調整合（不可逆隱蔽工程）。",
    ]
    yy = 0.29
    for r in risks:
        for ln in wrap_cjk(r, 70):
            fig.text(0.13, yy, ln, fontsize=10.5, color="#333"); yy -= 0.025
    fig.text(0.5, 0.05, "※ 本報告為規劃建議版，實際依現場、備料、天候與業主決議滾動調整。",
             ha="center", fontsize=9, color="#888")
    pdf.savefig(fig); plt.close(fig)

    # ---- 預算總覽 ----
    brows = []
    for no, name, amt, note in S.BUDGET:
        brows.append([str(no), name, f"{amt:,}" if amt is not None else "—", note])
    brows += [
        ["", "合計", f"{S.SUBTOTAL:,}", ""],
        ["", "監管費（工程款 10%）", f"{S.SUPERVISION:,}", ""],
        ["", "營業稅（5%）", f"{S.TAX:,}", ""],
        ["", "總金額", f"{S.TOTAL:,}", ""],
    ]
    table_page(pdf, "工項預算總覽（依報價單）", ["項次", "工程項目", "金額 (NT$)", "備註"],
               brows, "P2 預算", col_widths=[1, 5, 2, 4], fontsize=8.5)

    # ---- 甘特圖 ----
    image_page(pdf, "docs/工程進度甘特圖.png", "工程進度甘特圖（規劃建議版）", "P3 甘特圖")

    # ---- 進度明細表 ----
    trows = []
    for i, (phase, name, s, e, crit, dep, note, wd) in enumerate(S.tasks(), start=1):
        trows.append([str(i), phase, name, s.strftime("%m/%d"), e.strftime("%m/%d"),
                      str(wd), "★" if crit else "", dep, note])
    table_page(pdf, "工程進度明細表", ["#", "階段", "工項", "起", "迄", "工天", "關鍵", "前置", "備註"],
               trows, "P4 進度表", col_widths=[0.6, 1.5, 4.5, 1, 1, 0.8, 0.8, 2, 2.5], fontsize=6.3,
               note="★＝關鍵路徑")

    # ---- 細部施工順序圖 ----
    image_page(pdf, "docs/細部施工順序圖.png", "細部施工順序圖（依空間類型，涵蓋所有區域）", "P5 施工順序")

    # ---- 分區進場時程圖 ----
    image_page(pdf, "docs/分區進場時程圖.png", "分區進場時程圖（各區工序對應實際日期）", "P6 分區時程圖")

    # ---- 分區進場時程表 ----
    zrows = []
    for floor, name, typ, enter, exit_, weeks, ps, order in S.zones():
        zrows.append([str(order), floor, name, typ, enter.strftime("%m/%d"),
                      (S.zone_phase_date(ps, {"天花"}) or "").strftime("%m/%d") if S.zone_phase_date(ps, {"天花"}) else "",
                      (S.zone_phase_date(ps, {"木作"}) or "").strftime("%m/%d") if S.zone_phase_date(ps, {"木作"}) else "",
                      (S.zone_phase_date(ps, {"石材", "磁磚"}) or "").strftime("%m/%d") if S.zone_phase_date(ps, {"石材", "磁磚"}) else "",
                      (S.zone_phase_date(ps, {"油漆"}) or "").strftime("%m/%d") if S.zone_phase_date(ps, {"油漆"}) else "",
                      (S.zone_phase_date(ps, S._CABINET) or "").strftime("%m/%d") if S.zone_phase_date(ps, S._CABINET) else "",
                      exit_.strftime("%m/%d"), str(weeks)])
    table_page(pdf, "分區進場時程表（供現場照表調度）",
               ["順位", "樓層", "區域", "類型", "進場", "天花", "木作", "石材", "油漆", "櫃體/床", "退場", "週"],
               zrows, "P7 分區時程表",
               col_widths=[0.7, 0.8, 4.5, 1, 1, 1, 1, 1, 1, 1.2, 1, 0.7], fontsize=7.2)

    # ---- 採購時程倒推圖 ----
    image_page(pdf, "docs/採購時程倒推圖.png", "採購時程倒推圖（由需求進場日反推下單/詢價）", "P8 採購倒推圖")

    # ---- 採購執行計畫倒推表 ----
    prows = []
    for name, cat, need, po, kick, val, note, urg in S.procurement():
        days = (kick - dt.datetime.combine(dt.date.today(), dt.time())).days
        st = "立即" if urg else ("將到" if days <= 30 else "")
        prows.append([name, cat.replace("(A)", "").replace("(B)", ""),
                      f"{val:,}" if val is not None else "—",
                      need.strftime("%m/%d"), po.strftime("%m/%d"),
                      kick.strftime("%m/%d"), st, note])
    table_page(pdf, "採購執行計畫倒推表（依詢價啟動日排序）",
               ["採購包", "類別", "金額(NT$)", "需求進場", "下單截止", "詢價啟動", "狀態", "備註"],
               prows, "P9 採購倒推表",
               col_widths=[4.2, 1.6, 1.3, 1, 1, 1, 0.8, 3], fontsize=6.4,
               note="狀態「立即」＝詢價啟動日已到（今日 6/15），須本週啟動")

    # ---- 採購執行計畫建議(摘要) ----
    proc_adv = [
        ("h", "立即啟動清單（本週必辦）"),
    ]
    for name, cat, need, po, kick, val, note, urg in S.procurement():
        if urg:
            proc_adv.append(("n", f"・{name} → 下單截止 {po.strftime('%m/%d')}、進場 {need.strftime('%m/%d')}（{note}）"))
    proc_adv += [
        ("h", "採購總原則"),
        ("n", "1. 倒推排程，寧早勿晚；長交期(石材/系統櫃/床/廠製門/鋼構/照明)最優先發包。"),
        ("n", "2. 先封口未含 4 項(泥作防水/地坪/空調/油漆)：先界定範圍再詢價，否則卡關鍵路徑。"),
        ("n", "3. 封樣先行：石材/木皮/磁磚/玻璃/油漆色/布料核准後才大量下單。"),
        ("n", "4. 偏遠工地集中分批物流、排定吊裝(鋼構/石材/櫃/床/大型設備)。"),
        ("h", "發包/下單波次"),
        ("n", "W0 立即(6月中)：頂樓鋼構、保護鷹架、拆除、水電、泥作防水/空調(界定)、石材(詢價封樣)。"),
        ("n", "W1 7月初：輕鋼架+板材、天花板材、木作+主材、廠製門。"),
        ("n", "W2 8月初：系統櫃、被褥櫃+床板、防墜網、地坪發包。"),
        ("n", "W3 9月初：金屬床架、烘碗機、照明(停產替代)、油漆、白板、機櫃、FMG確認。"),
        ("n", "W4 10月初：人造石、玻璃、設備、消防、防火捲簾、銘版、磁磚貼工、清潔。"),
        ("h", "付款與現金流"),
        ("n", "建議 訂金30%→到場40%→安裝20%→驗收尾款10%(大額拉高保留款)；請款綁里程碑估驗(監管費10%)。7~9月為長交期訂金高峰，預備資金。"),
        ("h", "採購風險對策"),
        ("n", "停產/型號不符(T5燈管/AICM平板燈/冰河石磚)→提早確認替代並重新封樣；交期列入合約罰則；待確認/取消項以追加減正式變更。"),
    ]
    text_page(pdf, "採購執行計畫建議（摘要）", proc_adv, "P10 採購建議")

    # ---- 工程安排建議 ----
    adv1 = [
        ("h", "最該優先處理的 5 件事"),
        ("n", "1. 先封口「合約未含 4 工項」：泥作防水(尚未評估)、地坪、空調、油漆 — 皆在關鍵路徑/隱蔽界面，開工前務必界定範圍、廠商、費用。"),
        ("n", "2. 長交期項目立刻發包：石材、系統櫃(56被褥櫃+床組)、廠製門、頂樓鋼構、設備；偏遠工地運輸提前 4~8 週。"),
        ("n", "3. 以 2F 主會堂為核心：鷹架(6.8M)+80坪天花+花崗岩壁/地/講台+木作反射板疊在同一空間，集中資源、嚴控工序交接。"),
        ("n", "4. 鷹架一次到位：高處工項(天花、上部石材、油漆、燈具)排同一鷹架週期，避免重複搭拆。"),
        ("n", "5. 天花封板前完成消防/空調整合：不可逆隱蔽工程，錯過要拆天花重做。"),
        ("h", "合約未含 / 待評估工項（風險第一）"),
        ("n", "泥作/防水(尚未評估)：石材/磁磚/地坪都要等它；濕區須試水。排在拆除後、天花前。"),
        ("n", "地坪(未含)：影響石材踢腳收頭與櫃體立面高程；確認施作者、材質與完成面標高。"),
        ("n", "空調(未含)：室內外機/管線多在天花內，務必封板前定位點位。"),
        ("n", "油漆(未含)：介於木作之後、燈具/細清之前，漏排會卡住收尾，須排入時程。"),
        ("n", "待確認/取消：電視、投影機、洗衣機、淋浴門、二三樓玻璃門(不符法規暫取消)、防火門待評估 — 彙整清單逐項以追加減結案。"),
    ]
    text_page(pdf, "工程安排建議（一）", adv1, "P8 建議")
    adv2 = [
        ("h", "施工順序（單一空間）"),
        ("n", "保護/鷹架→拆除→泥作打底/防水→水電配管→輕鋼架天花骨架→(消防/空調整合)→封板→木作底→石材/磁磚→木作面/油漆→系統櫃→人造石/玻璃→燈具/設備→窗簾/家飾→清潔→驗收"),
        ("h", "分樓層流水"),
        ("n", "濕程/水電/天花：由下而上 1F→2F→3F；完成面收尾(油漆後)：由上而下 3F→1F 退場保護下層。各工班用 3 週前置看板滾動排程。"),
        ("h", "主會堂(關鍵空間)"),
        ("n", "鷹架搭設後先完成高處(天花/上部石材/燈具預留)再拆；講台為石材+木作+金屬三方交界，先做 1:1 放樣與大樣會審(B01系列)。"),
        ("h", "品質 / 安全 / 管控"),
        ("n", "每週工地會議＋月進度查核對照甘特圖；請款綁里程碑(開工/天花/石材/櫃體/交屋)。"),
        ("n", "高架作業(主會堂6.8M、頂樓吊裝、梯間防墜網)落實安全；教會若需部分使用採分區圍封。"),
        ("n", "頂樓鋼構為室外作業，雨季預留緩衝；偏遠運輸預留彈性；成品保護至細清前不拆。"),
        ("h", "工期優化"),
        ("n", "頂樓鋼構(室外)與室內泥作/水電平行省3~4週；可分區提前點交(如先交1F或2F主會堂)；注意社區壓縮工時之誤工加成(2.5~4%/0.5hr)。"),
    ]
    text_page(pdf, "工程安排建議（二）", adv2, "P9 建議")

print("saved:", OUT)
