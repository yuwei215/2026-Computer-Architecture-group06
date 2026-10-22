# CP2 指令統計結果(threshold_branch.s)

## 量測環境

- 工具:Ripes v2.3.0(Windows 版)
- 處理器:Single-cycle processor(`RV32_SS`)
- ISA:RV32IM(已取消 C 壓縮擴充)
- 程式:`threshold_branch.s`(簡嘉佑),測試用 `main` 見 `ripes_test_branch.s`

## 計數規則(待羅允辰確認,以他訂的為準)

- 範圍:`threshold:` 到 `ret`(含 `ret`),不含測試用 `main` 與呼叫它的 `jal`
- 以 Ripes 反組譯的真實指令計算:`ret` 實際是 `jalr x0 x1 0`,算 1 條;`li a0, 255` 是 1 條 `addi`
- 分支數:只算條件分支(`beq`/`bne`/`blt`/`bge`/`bltu`/`bgeu`);`jalr`(`ret`)另列為跳躍

## 靜態指令數

| 位址 | 指令(Ripes 反組譯) | 說明 |
|---|---|---|
| 0x14 | `bge x10 x11 12` | 條件分支(有號),成立則跳到 `ge_case`(0x20) |
| 0x18 | `addi x10 x0 0` | `li a0, 0` |
| 0x1c | `jalr x0 x1 0` | `ret` |
| 0x20 | `addi x10 x0 255` | `li a0, 255`(`ge_case`) |
| 0x24 | `jalr x0 x1 0` | `ret` |

靜態指令數 = **5**;其中條件分支 = **1**(`bge`),跳躍(`jalr`)= 2。

## 動態指令數(每組測資)

| 測資 (rs1, rs2) | 預期 | 實際 a0 | 走哪條路 | `bge` | 動態指令數(threshold) |
|---|---|---|---|---|---|
| (5, 5) | 255 | 255 | `bge`→`li 255`→`ret` | 成立(跳) | 3 |
| (4, 5) | 0 | 0 | `bge`→`li 0`→`ret` | 不成立 | 3 |
| (-1, 0) | 0 | 0 | `bge`→`li 0`→`ret` | 不成立 | 3 |
| (2147483647, -2147483648) | 255 | 255 | `bge`→`li 255`→`ret` | 成立(跳) | 3 |
| (-2147483648, 2147483647) | 0 | 0 | `bge`→`li 0`→`ret` | 不成立 | 3 |

- 動態指令數不隨輸入改變,最少 = 最多 = **3**;每次執行的分支指令(`bge`)= 1 條。
- 計算方式:Ripes 的 `Instrs. retired` 總數(每組皆為 6)扣掉 `main` 的 3 條(`jal`、`li a7, 10`、`ecall`)。
- 另一種算法交叉檢查:GUI 版 `ripes_test_branch.s`(`main` 用 `li` 載入輸入,共 5 條)的 (4,5)、(-1,0) 總數為 8,8 − 5 = 3,結果一致。

## 量測方式說明(照實寫)

- 上表 5 組由林煉棠以 Ripes 命令列模式批次執行(`--mode cli --proc RV32_SS --isaexts M`,暫存器 `a0`、`a1` 以 `--reginit` 初始化)。
- 簡嘉佑、羅允辰另在各自電腦用 Ripes GUI 手動執行 (5,5)、(4,5)、(-1,0),結果為 255、0、0。
- 截圖(待補):放在 `../report/figures/`。
