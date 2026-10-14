# 06_THRESHOLD/c_baseline/

- 對應 Checkpoint:CP1
- 內容:C 參考實作(原始碼、與 spec 一致的參考函式)

## 檔案

| 檔案 | 說明 |
|---|---|
| `threshold.h`、`threshold.c` | 參考函式 `int32_t threshold(int32_t rs1, int32_t rs2)`,`rs1 >= rs2` 回傳 255,否則回傳 0(有號比較) |
| `test_threshold.c` | 測試程式:用 12 組測資逐筆驗證 `threshold()`,印出預期與實際並統計通過數 |

測資在 [`../tests/`](../tests/),有號與無號比較的實驗程式也在該目錄。

執行測試(在本目錄):

```
gcc -std=c11 -Wall -Wextra test_threshold.c threshold.c -o test_threshold
./test_threshold
```
