# threshold_branch.s
# 作者: 簡嘉佑
# 功能: a0 = (a0 >= a1) ? 255 : 0   
# 輸入: a0 = rs1, a1 = rs2
# 輸出: a0
.text
.globl threshold
threshold:
    bge   a0, a1, ge_case
    li    a0, 0
    ret
ge_case:
    li    a0, 255
    ret