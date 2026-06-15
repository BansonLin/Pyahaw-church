# 碧侯教會 室內裝修工程

真耶穌教會 碧侯教會（Pyahaw）室內裝修工程之專案資料整理與工程規劃。

- **規模**：3 層樓 + 頂樓加蓋，約 549 坪
- **總金額**：NT$16,729,761（含監管費 10% + 營業稅）
- **報價日**：2026/05/23　｜　**設計簡報**：2026/01/26
- **空間**：主/副會堂、主日學教室、寢室、餐廳廚房、接待大廳、辦公室

## 交付物（docs/）

| 文件 | 說明 |
|---|---|
| [工程進度甘特圖.xlsx](docs/工程進度甘特圖.xlsx) | **Excel 版**：週曆式甘特圖＋進度表＋預算總覽＋安排建議（可編輯） |
| [工程進度甘特圖.png](docs/工程進度甘特圖.png) | 全案工程進度甘特圖（規劃建議版，含關鍵路徑與里程碑） |
| [細部施工順序圖.png](docs/細部施工順序圖.png) | 細部施工順序圖（依空間類型，涵蓋所有區域） |
| [細部施工順序.md](docs/細部施工順序.md) | 逐區施工工序明細＋空間類型對照＋跨區依存 |
| [工程進度表.md](docs/工程進度表.md) | 工項預算總覽、進度明細、里程碑、關鍵路徑 |
| [工程安排建議.md](docs/工程安排建議.md) | 工程安排建議書（風險、備料、工序、界面整合、管控） |

## 重點摘要

- **預估工期**：約 22～24 週（約 5.5 個月），進場保護日（開工）2026/06/19，預計 2026/12/02 交屋。
- **關鍵路徑**：進場保護/鷹架 → 泥作防水/水電 → 輕鋼架天花（主會堂）→ 木作 → 石材 → 油漆 → 系統櫃/床組 → 燈具/設備 → 清潔 → 驗收。
- **最大風險**：合約**未含/待評估**的 4 工項（泥作防水、地坪、空調、油漆）皆在關鍵路徑或界面上，須於開工前界定。

## 重新產生 / 調整排程

所有日期由 `scripts/schedule_data.py` 單一來源管理。**要改開工日，只需改該檔的 `PROTECTION_START`**，再重跑下列指令即可同步更新甘特圖、Excel 與進度表：

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install matplotlib openpyxl
PYTHONPATH=scripts python scripts/generate_gantt.py     # → docs/工程進度甘特圖.png（需 Noto Sans CJK 字型）
PYTHONPATH=scripts python scripts/generate_excel.py     # → docs/工程進度甘特圖.xlsx
PYTHONPATH=scripts python scripts/generate_markdown.py  # → docs/工程進度表.md
PYTHONPATH=scripts python scripts/generate_sequence.py  # → docs/細部施工順序圖.png
```

> 排程為規劃版，實際依現場、備料、天候與業主決議滾動調整。
