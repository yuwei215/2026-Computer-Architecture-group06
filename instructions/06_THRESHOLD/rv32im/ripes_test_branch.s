# ripes_test_branch.s
# 用途: 在 Ripes 驗證 threshold_branch.s(測試用 main + 簡嘉佑的 threshold)
# 使用: 改 main 前兩行的 li 數字即可換測資, threshold 不要動
# 每次改完要先按 Ripes 的重設鈕(圓形箭頭)再執行
#
# 測資:  (5,5)->255  (4,5)->0  (-1,0)->0
#        (2147483647,-2147483648)->255  (-2147483648,2147483647)->0
# 註: 大數字的 li 會被組譯成 lui+addi 兩條, 但不在 threshold 計數範圍內
.text
main:
    li   a0, 5
    li   a1, 5
    jal  ra, threshold
    li   a7, 10
    ecall

# ---- 以下是 threshold_branch.s(簡嘉佑)的內容 ----
threshold:
    bge   a0, a1, ge_case
    li    a0, 0
    ret
ge_case:
    li    a0, 255
    ret
