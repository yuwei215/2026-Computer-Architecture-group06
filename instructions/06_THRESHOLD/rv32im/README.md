# 06_THRESHOLD/rv32im/

- 對應 Checkpoint:CP2
- 內容:RV32IM 組合語言實作與指令統計(僅允許 RV32IM)

## 檔案

| 檔案 | 作者 | 說明 |
|---|---|---|
| `threshold_branch.s` | 簡嘉佑 | `threshold` 的 RV32IM 實作(有號比較,`bge`)。輸入 `a0` = rs1、`a1` = rs2,結果放 `a0`,最後 `ret` |
| `ripes_test_branch.s` | 林煉棠 | Ripes 驗證用:測試用 `main` + `threshold`。換測資只改 `main` 前兩行的 `li`,`threshold` 不要動 |
| `count_result.md` | 林煉棠 | 計數規則、靜態指令數、5 組測資的動態指令數與分支數、`bgeu` 無號對照 |

報告見 [`../report/CP2.md`](../report/CP2.md),截圖在 [`../report/figures/`](../report/figures/)。

## 結果摘要

| 項目 | 數量 |
|---|---:|
| 靜態指令數(`threshold:` 到 `ret`) | 5 |
| 條件分支(`bge`) | 1 |
| 跳躍(`jalr`,即 `ret`) | 2 |
| 動態指令數(5 組測資皆同) | 3 |

5 組測資(含 2 組邊界值)結果皆正確:(5,5)→255、(4,5)→0、(-1,0)→0、(2147483647,-2147483648)→255、(-2147483648,2147483647)→0。計數規則與每組細節見 `count_result.md`。

## 在 Ripes 重現

1. 使用 Ripes v2.3.0,點工具列最左邊的晶片圖示,選 **Single-cycle processor**,ISA Exts. 勾 **M**、**取消 C**,確認右下角顯示 `ISA: RV32IM`。
2. 在 Editor 貼上 `ripes_test_branch.s` 的內容。
3. 切到 Processor 頁,按重設鈕(圓形箭頭)後按播放鈕。
4. 看暫存器 `x10 (a0)` 與 `Instrs. retired`:`main` 前兩行為 (5,5) 時 `a0 = 0xff`、總 retired 為 8(扣掉 `main` 的 5 條,`threshold` 為 3 條)。
5. 換測資時只改 `main` 前兩行,每次先按重設鈕。

## 說明

- 本目錄的組合語言由 Ripes 內建組譯器組譯,沒有使用其他工具鏈。
- 只提交一個版本(`threshold_branch.s`);自訂指令版本屬於 CP3。
- `bge` 是有號比較。若換成 `bgeu`(無號)會在負數輸入時出錯,實驗結果見 `count_result.md`。
