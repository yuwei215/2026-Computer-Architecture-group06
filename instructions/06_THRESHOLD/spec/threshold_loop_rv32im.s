# threshold_loop_rv32im.s
# 用 RV32IM 標準指令把 8 個數字二值化(門檻 5):out[i] = (in[i] >= 5) ? 255 : 0
# 用途:在 Ripes 實際執行,量 RV32IM 基準的動態指令數,對照 threshold_bench.py 的模型
# Ripes v2.3.0,Single-cycle(RV32_SS),RV32IM
# 預期 out = 255, 0, 0, 255, 0, 0, 255, 0;Instrs. retired = 77(推導見 spec/README.md)

.data
in:     .word 5, 4, -1, 2147483647, -2147483648, 0, 7, -3
out:    .word 0, 0, 0, 0, 0, 0, 0, 0

.text
main:
    la    a0, in          # 輸入指標
    la    a1, out         # 輸出指標
    li    a2, 5           # 門檻(rs2)
    li    a3, 8           # 元素數
loop:
    lw    t0, 0(a0)
    bge   t0, a2, ge_case # 有號比較
    li    t1, 0
    j     store
ge_case:
    li    t1, 255
store:
    sw    t1, 0(a1)
    addi  a0, a0, 4
    addi  a1, a1, 4
    addi  a3, a3, -1
    bnez  a3, loop
    li    a7, 10
    ecall
