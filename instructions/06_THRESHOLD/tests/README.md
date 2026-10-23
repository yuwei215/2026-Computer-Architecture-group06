# 06_THRESHOLD/tests/

- 對應 Checkpoint:CP1–CP3
- 內容:測資與預期輸出(至少 10 組,含 3 組以上邊界值)

## 檔案

| 檔案 | 說明 |
|---|---|
| `threshold_tests.md` | 12 組測資與預期輸出(含邊界值) |
| `signed_vs_unsigned.c` | 有號(`int32_t`)與無號(`uint32_t`)比較的對照實驗程式 |
| `test_result_1114405033.txt` | 羅允辰在自己電腦執行 `test_threshold` 的結果 |

C 參考實作與測試程式在 [`../c_baseline/`](../c_baseline/);RV32IM 的 Ripes 驗證在 [`../rv32im/`](../rv32im/)。
