# 06_THRESHOLD/spec/

- 對應 Checkpoint:CP3
- 內容:語意規格、虛擬碼、編碼範例(格式見 HOMEWORK.md 第 6.7 節)

## A. 語意規格(負責:羅允辰)

### THRESHOLD
- 語意(公式):`rd = (rs1 ≥ rs2) ? 255 : 0`
  - 比較為**有號比較**(把 `rs1`、`rs2` 當成 32 位元二補數)。
  - `rs1` 是要判斷的輸入值,`rs2` 是門檻:輸入大於或等於門檻輸出 255,否則輸出 0。
- 運算元與定義域:
  - `rs1`、`rs2` 皆為 32 位元有號二補數,任何 32 位元值都是合法輸入。
  - 最小值:−2³¹ = −2147483648(`0x80000000`)
  - 最大值:2³¹ − 1 = 2147483647(`0x7FFFFFFF`)
- 結果範圍:
  - `rd` 只會是 0(`0x00000000`)或 255(`0x000000FF`)兩種值,高 24 位元永遠是 0,沒有第三種可能。
  - 例外:`rd` 為 `x0` 時,結果不會被保留(見下方邊界條件)。
- 邊界條件與溢位處理:
  - **溢位:** 指令只比較大小,不產生加減的結果,所以不會溢位,也不需要 wrap-around 處理。
  - **`rs1 == rs2`:** 條件是「≥」,相等也成立,結果為 255(官方測資 (5, 5) → 255)。
  - **`rs2` 為最小值:** `rs2` 是 −2147483648(`0x80000000`)時,結果一定是 255。−2147483648 是 32 位元有號數裡最小的值,沒有任何數比它還小。`rs1` 頂多跟它相等,而相等不算「小於」,所以 `rs1 < rs2` 永遠不成立,`rd` 一定是 255。
  - **`rd` 為 `x0`:** `x0` 不會變,永遠是 0,寫進去的值會被丟掉。
  - **改用無號比較會錯:** 以 (−1, 0) 為例,−1 在 32 位元裡是 `0xFFFFFFFF`。用有號來看它就是 −1,比 0 小,所以答案是 0。可是用無號來看,`0xFFFFFFFF` 是 4294967295,是最大的數,怎麼樣都不會比 0 小,答案就變成 255。位元一樣,只是解讀方式不同,結果就反過來了。
    - CP1 `tests/signed_vs_unsigned.c`(`uint32_t` 版):(−1, 0)、(−3, 2)、(2, −3) 三組結果錯誤。
    - CP2 `rv32im/count_result.md`(`bgeu` 對照):(−1, 0) → 255(應為 0),(2147483647, −2147483648) → 0(應為 255),(−2147483648, 2147483647) → 255(應為 0)。
- 測試向量(至少 3 組,含 1 組邊界值):

  | # | rs1 | rs2 | rd(預期) | 說明 |
  |---|---:|---:|---:|---|
  | 1 | 5 | 5 | 255 | 官方測資。兩者相等,「≥」成立,輸出 255。 |
  | 2 | −1 | 0 | 0 | 官方測資。有號比較下 −1 < 0,不成立,輸出 0;若誤用無號比較,−1 會變成 `0xFFFFFFFF`,反而得到 255。 |
  | 3 | 2147483647 | −2147483648 | 255 | **邊界值**:`rs1` 為最大值、`rs2` 為最小值。有號比較下最大值 ≥ 最小值,輸出 255;若誤用無號比較,`0x7FFFFFFF` < `0x80000000`,會得到 0。 |

- 對應的 RV32IM baseline 片段與指令數:
  - 片段:`rv32im/threshold_branch.s`(簡嘉佑)

    ```asm
    threshold:
        bge  a0, a1, ge_case
        li   a0, 0
        ret
    ge_case:
        li   a0, 255
        ret
    ```

  - 指令數(來源 `rv32im/count_result.md`,Ripes v2.3.0,Single-cycle,RV32IM):靜態 5 條、動態每次呼叫 3 條(5 組測資皆為 3)、條件分支 1 條(`bge`)。計數範圍為 `threshold:` 到 `ret`,不含測試用 `main`。

### 虛擬碼

```text
輸入:rs1(要判斷的值)、rs2(門檻),都當成 32 位元有號整數
1. 用有號比較判斷 rs1 是否大於或等於 rs2
2. 若成立,結果 = 255
   否則,結果 = 0
3. 若 rd 是 x0,不寫入(x0 永遠是 0)
   否則,把結果寫入 rd
```

## B. 機器碼與欄位說明(負責:簡嘉佑)

### 欄位格式(HOMEWORK 第四節,R-type、custom-0)

```
31      25 24   20 19   15 14  12 11    7 6       0
+----------+-------+-------+------+-------+---------+
|  funct7  |  rs2  |  rs1  |funct3|  rd   | 0001011 |
+----------+-------+-------+------+-------+---------+
```

| 欄位 | 位元 | 值 | 說明 |
|---|---|---|---|
| `funct7` | [31:25] | `0000000`| **助教指定** |
| `rs2` | [24:20] | 5 位元暫存器編號 | (門檻) |
| `rs1` | [19:15] | 5 位元暫存器編號 | (輸入) |
| `funct3` | [14:12] | `000`| **助教指定** |
| `rd` | [11:7] | 5 位元暫存器編號 | (結果 0 或 255) |
| `opcode` | [6:0] | `0001011` | custom-0(0x0B),HOMEWORK 第四節規定 |


### 機器碼範例

| 組合語言 | funct7 | rs2 | rs1 | funct3 | rd | opcode | 十六進位 |
|---|---|---|---|---|---|---|---|
| `threshold a0, a0, a1` |0000000|01011|01010|000|01010|0001011|0x00B5050B|
| `threshold t0, t0, t1` |0000000|00110|00101|000|00101|0001011|0x0062828B|

以上機器碼為手算,因為一般 Ripes 不認得custom-0,無法直接組譯 threshold。

我用 Ripes 組譯 add a0, a0, a1(0x00B50533),確認前 6 位十六進位與 threshold a0, a0, a1 相同，驗證手算方法正確。

## C. 指令數比較表(負責:簡嘉佑)

| 項目 | RV32IM baseline(`threshold_branch.s`) | 自訂指令 `threshold` |
|---|---|---|
| 計數方法 | 靜態+動態;Ripes v2.3.0(Windows),Single-cycle(`RV32_SS`),RV32IM | 依規格推算,未在模擬器實際執行(一般 Ripes 不支援 custom-0) |
| 計數範圍 | `threshold:` 到 `ret`(含 `ret`),不含測試用 `main` | 與左欄一致：函式內為 threshold a0, a0, a1 + ret,含 ret,不含 main |
| 靜態指令數 | 5 | 2 |
| 動態指令數(每次呼叫) | 3(5 組測資皆為 3) | 2 |
| 條件分支數 | 1(`bge`) | 0 |

- 左欄數字來源:`rv32im/count_result.md`(CP2,Ripes GUI 手動執行並截圖)。
- 靜態指令由 5 條減為 2 條，動態由 3 條減為 2 條，條件分支由 1 條減為 0 條，因為 threshold 一條指令就完成比較並寫入 0 或 255,不需要 bge 和 li。
- 自訂指令欄的數字是依規格推算,不是模擬器量到的。

## D. 實作與驗證(照老師 `mac_demo` 的做法)

程式由 Claude(Claude Code)撰寫,林煉棠審閱並在自己的電腦執行。結構對照老師倉庫的 `mac_demo/`。

| 檔案 | 對照 `mac_demo` | 內容 |
|---|---|---|
| `threshold_encoding.py` | `mac_encoding.py` | 編碼、解碼、golden model、執行一條指令(`rd = x0` 不寫入) |
| `test_threshold_encoding.py` | `test_mac_encoding.py`、`test_r4_and_x0.py` | 機器碼對照 B 段手算、欄位、官方測資、邊界值、`x0`、不會誤認 `add` 或其他 funct |
| `threshold.h`、`riscv_probe.c` | `mac.h`、`riscv_probe.c` | 用 `.insn r 0x0b, 0, 0, rd, rs1, rs2` 讓 RISC-V gcc 產生自訂指令 |
| `test_riscv_encoding.py` | `test_riscv_encoding.py` | RISC-V gcc 編譯 + objdump 反組譯,確認目的碼中真的有 THRESHOLD 指令 |
| `threshold_bench.py`、`test_threshold_bench.py` | `benchmark/dotbench.py` | 二值化 N 個數字的指令數模型與加速比(CPI = 1,模型估計) |
| `threshold_loop_rv32im.s` | — | RV32IM 迴圈版,在 Ripes 實際執行,驗證模型的基準指令數 |
| `threshold_sim.c` | — | C 版解碼與執行(補充) |

### 執行方式(VS Code 終端機,PowerShell)

```powershell
cd D:\ca-group06\instructions\06_THRESHOLD\spec
python -B -m unittest discover -s . -p "test_*.py" -v
python -B threshold_encoding.py
python -B threshold_bench.py
gcc -std=c11 -Wall -Wextra -o threshold_sim.exe threshold_sim.c
.\threshold_sim.exe
```

RISC-V gcc 組譯檢查(WSL Ubuntu,需先安裝 `gcc-riscv64-unknown-elf`、`binutils-riscv64-unknown-elf`):

```bash
cd /mnt/d/ca-group06/instructions/06_THRESHOLD/spec
python3 -B -m unittest test_riscv_encoding -v
```

### 指令數模型(每個元素的動態指令數)

| 版本 | 迴圈本體 | 每元素 |
|---|---|---:|
| RV32IM 分支版(`bge`,同 CP2) | `lw`、`bge`、`li`、(`j`)、`sw`、`addi`×3、`bnez` | 成立 8、不成立 9 |
| RV32IM 無分支版(`slt`) | `lw`、`slt`、`addi`、`andi`、`sw`、`addi`×3、`bnez` | 9 |
| THRESHOLD | `lw`、`threshold`、`sw`、`addi`×3、`bnez` | 7 |

每次執行另有固定開銷 8 條(`la`×2 = 4、`li`×2 = 2、結束 `li a7`、`ecall`)。

### 驗證結果

**林煉棠本人執行(2026/10/30,截圖在 `../report/figures/1114405011/`):**

| 執行內容 | 環境 | 結果 | 截圖 |
|---|---|---|---|
| `python -B -m unittest discover -s . -p "test_*.py" -v` | Windows 11、VS Code 終端機(PowerShell)、Python 3 | 共 19 項:18 項通過,1 項跳過(RISC-V 組譯檢查,Windows 沒有 RISC-V gcc,改在 WSL 跑) | `cp3_unittest.png` |
| `python3 -B -m unittest test_riscv_encoding -v` | WSL Ubuntu、`gcc-riscv64-unknown-elf`、Python 3.12 | 通過。objdump 反組譯 `threshold_probe` 得到 `00b5050b`(`.insn 4, 0x00b5050b`)與 `ret`,解碼為 rd = x10、rs1 = x10、rs2 = x11,與 B 段手算 `0x00B5050B` 一致 | `cp3_riscv_gcc_objdump.png` |
| `.\threshold_sim.exe` | Windows、gcc(MSYS2) | 9 組全部 PASS | `cp3_threshold_sim.png` |
| `python -B threshold_bench.py` | Windows、Python 3 | 見下方加速比 | `cp3_bench.png` |
| Ripes GUI 執行 `threshold_loop_rv32im.s`(N = 8,門檻 5) | Ripes v2.3.0、Single-cycle processor、RV32IM | `Instrs. retired` = **77**、Cycles = 77、CPI = 1,與模型 6 + 8×3 + 9×5 + 2 = 77 一致;程式正常結束(exit code 0) | `cp3_ripes_loop_77.png` |
| 同上,執行後在 Memory 分頁(Signed)檢查 `.data` | 同上 | `in`(`0x10000000`～`0x1000001c`)= 5, 4, −1, 2147483647, −2147483648, 0, 7, −3;`out`(`0x10000020`～`0x1000003c`)= 255, 0, 0, 255, 0, 0, 255, 0,全部正確 | `cp3_ripes_loop_out.png` |

- 同樣的 N = 8,THRESHOLD 版依模型為 6 + 7×8 + 2 = 64 條,RV32IM 分支版 77 條,加速比約 **1.20×**(動態指令數比,模型估計)。
- 較大的工作負載(`threshold_bench.py`):對分支版約 1.19～1.21×,對無分支版約 1.28×;若自訂指令讓時脈週期變慢 20%(T 比 1.2),加速比降到約 1.0×。

**Claude Code 在林煉棠電腦以 Ripes 命令列模式(`--mode cli --proc RV32_SS --isaexts M`)預先執行(不是本人手動):**

- `threshold_loop_rv32im.s`(N = 8,門檻 5):`Instrs. retired` = 77、輸出 255, 0, 0, 255, 0, 0, 255, 0,與上方本人 GUI 結果相同。
- 一般 Ripes 無法執行 custom-0:把 `.word 0x00B5050B` 放進程式、`a0 = a1 = 5` 執行後,`a0` 仍是 5(預期 255),表示 Ripes 沒有執行這條指令。所以 THRESHOLD 那欄是模型推算,不是模擬器量到的。
- 加速比小的原因:RV32IM 本來每個元素只要 8～9 條,THRESHOLD 只省掉 1～2 條;迴圈的 `lw`、`sw`、指標與計數器更新都還在。
