# -*- coding: utf-8 -*-
"""由 schedule_data.py 重生 docs/工程進度表.md（確保與甘特圖/Excel 日期一致）。"""
import schedule_data as S

T = S.tasks()
M = S.milestones()
proto = S._d(S.PROTECTION_START).strftime("%Y/%m/%d")
handover = max(t[3] for t in T).strftime("%Y/%m/%d")

def md(d):
    return d.strftime("%m/%d")

lines = []
A = lines.append
A("# 碧侯教會 室內裝修工程 — 工程進度表（規劃建議版）\n")
A("> 依據：工程報價單（2026/05/23，總金額 **NT$16,729,761**）、施工圖、天花/剖面大樣、3D 設計簡報（2026/01/26）")
A("> 本表為**規劃建議版**，實際依現場、備料、天候與業主決議滾動調整。\n")
A("## 一、基本假設\n")
A("| 項目 | 假設 |")
A("|---|---|")
A(f"| 進場保護日（開工） | **{proto}**（業主指定）|")
A("| 工時 | 週 6 工作天；社區規範 08:00–12:00 / 13:00–17:00（正常工時 8hr）|")
A(f"| 預估總工期 | **約 22～24 週（約 5.5 個月）**，預計 **{handover} 交屋** |")
A("| 不含合約之工項 | 泥作防水（尚未評估）、地坪、空調、油漆 → **須先界定施作介面與廠商** |\n")

A("## 二、工項預算總覽（依報價單）\n")
A("| 項次 | 工程項目 | 金額 (NT$) | 備註 |")
A("|---:|---|---:|---|")
for no, name, amt, note in S.BUDGET:
    amt_s = f"{amt:,}" if amt is not None else "—"
    A(f"| {no} | {name} | {amt_s} | {note} |")
A(f"| | **合計** | **{S.SUBTOTAL:,}** | |")
A(f"| | 監管費（工程款 10%） | {S.SUPERVISION:,} | |")
A(f"| | 營業稅（5%） | {S.TAX:,} | |")
A(f"| | **總金額** | **{S.TOTAL:,}** | |\n")

A("## 三、工程進度明細（甘特圖資料）\n")
A("> ★ = 關鍵路徑工項；〔需確認〕= 合約未含、須界定後才能定案\n")
A("| # | 階段 | 工項 | 開始 | 結束 | 工作天 | 關鍵 | 前置作業 | 備註 |")
A("|---:|---|---|---|---|---:|:--:|---|---|")
for i, (phase, name, s, e, crit, dep, note, wd) in enumerate(T, start=1):
    star = "★" if crit else ""
    A(f"| {i} | {phase} | {name} | {md(s)} | {md(e)} | {wd} | {star} | {dep} | {note} |")
A("")

A("## 四、關鍵里程碑\n")
A("| 里程碑 | 目標日 |")
A("|---|---|")
for name, d in M:
    A(f"| {name} | {d.strftime('%Y/%m/%d')} |")
A("")

A("## 五、關鍵路徑（Critical Path）\n")
A("```")
A("待確認項目決議 → 長交期下單 → 進場保護/鷹架 → 泥作防水 ┐")
A("                                              水電配管 ┴→ 輕鋼架天花(2F/3F主會堂)")
A("   → 天花內 消防/空調整合 → 木作(講台/壁面/反射板) → 石材壁面(主會堂/副堂)")
A("   → 油漆 → 系統櫃/床組 → 照明/設備 → 粗清+細清 → 驗收/交屋")
A("```\n")
A("**主會堂（鷹架＋80 坪天花＋花崗岩壁面/地坪/講台＋木作反射板）為全案資源最密集、"
  "工序最長之關鍵空間，主導總工期。**")

open("docs/工程進度表.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("regenerated docs/工程進度表.md | 開工", proto, "| 交屋", handover)
