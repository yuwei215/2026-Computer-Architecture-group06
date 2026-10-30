/*
 * threshold_sim.c
 * THRESHOLD 自訂指令的小模擬器：把 32 位元機器碼拆成欄位、確認是 THRESHOLD、照規格執行並寫回暫存器。
 * 語意：rd = (rs1 >= rs2) ? 255 : 0（有號比較，rs2 為門檻）；rd 為 x0 時不寫入。
 * 編碼：R-type，opcode = 0001011（custom-0），funct3 = 000、funct7 = 0000000（助教指定）。
 * 撰寫：Claude（Claude Code），林煉棠審閱並在本人電腦執行。輸出只用英文，避免終端機亂碼。
 */
#include <stdint.h>
#include <stdio.h>

#define OPCODE_CUSTOM0   0x0B
#define FUNCT3_THRESHOLD 0x0
#define FUNCT7_THRESHOLD 0x00

static int32_t regs[32]; /* x0 ~ x31 */

/* 執行一條指令。是 THRESHOLD 就執行並回傳 1，不是就回傳 0（不改暫存器）。 */
static int execute(uint32_t word)
{
    /* 拆欄位：先右移到最右邊，再用遮罩只留下該欄位的位元 */
    uint32_t opcode = word & 0x7F;          /* [6:0]   7 位 */
    uint32_t rd     = (word >> 7)  & 0x1F;  /* [11:7]  5 位 */
    uint32_t funct3 = (word >> 12) & 0x7;   /* [14:12] 3 位 */
    uint32_t rs1    = (word >> 15) & 0x1F;  /* [19:15] 5 位 */
    uint32_t rs2    = (word >> 20) & 0x1F;  /* [24:20] 5 位 */
    uint32_t funct7 = (word >> 25) & 0x7F;  /* [31:25] 7 位 */

    if (opcode != OPCODE_CUSTOM0 || funct3 != FUNCT3_THRESHOLD || funct7 != FUNCT7_THRESHOLD) {
        return 0;
    }

    /* regs 是 int32_t，所以這裡是有號比較 */
    int32_t result = (regs[rs1] >= regs[rs2]) ? 255 : 0;

    if (rd != 0) { /* x0 永遠是 0，寫入要丟掉 */
        regs[rd] = result;
    }
    return 1;
}

static void clear_regs(void)
{
    for (int i = 0; i < 32; i++) {
        regs[i] = 0;
    }
}

static int pass_count = 0;
static int fail_count = 0;

/* 測一組：設定 rs1、rs2 暫存器的值，執行機器碼，檢查 rd 暫存器的值 */
static void test(const char *name, uint32_t word, int r1, int32_t v1, int r2, int32_t v2,
                 int rd, int32_t expected)
{
    clear_regs();
    regs[r1] = v1;
    regs[r2] = v2;
    regs[0] = 0;
    int ok = execute(word) && regs[rd] == expected;
    printf("%-28s 0x%08X  rs1=%11d rs2=%11d  expect x%-2d=%3d  got %3d  %s\n",
           name, (unsigned)word, (int)v1, (int)v2, rd, (int)expected, (int)regs[rd],
           ok ? "PASS" : "FAIL");
    if (ok) pass_count++; else fail_count++;
}

int main(void)
{
    printf("THRESHOLD simulator: rd = (rs1 >= rs2) ? 255 : 0 (signed)\n\n");

    /* threshold a0, a0, a1 = 0x00B5050B（a0 = x10，a1 = x11） */
    test("official (5,5)",             0x00B5050Bu, 10, 5,           11, 5,             10, 255);
    test("official (4,5)",             0x00B5050Bu, 10, 4,           11, 5,             10, 0);
    test("official (-1,0) signed",     0x00B5050Bu, 10, -1,          11, 0,             10, 0);
    test("boundary (MAX,MIN)",         0x00B5050Bu, 10, 2147483647,  11, INT32_MIN,     10, 255);
    test("boundary (MIN,MAX)",         0x00B5050Bu, 10, INT32_MIN,   11, 2147483647,    10, 0);
    test("rs2 = MIN always 255",       0x00B5050Bu, 10, INT32_MIN,   11, INT32_MIN,     10, 255);

    /* threshold t0, t0, t1 = 0x0062828B（t0 = x5，t1 = x6） */
    test("t0,t0,t1 (-3,-5)",           0x0062828Bu, 5,  -3,          6,  -5,            5,  255);

    /* threshold x0, a0, a1 = 0x00B5000B：rd 欄位是 00000，結果要被丟掉，x0 仍是 0 */
    test("rd = x0 stays 0",            0x00B5000Bu, 10, 5,           11, 5,             0,  0);

    /* add a0, a0, a1 = 0x00B50533：opcode 不是 custom-0，不能被當成 THRESHOLD */
    clear_regs();
    regs[10] = 5;
    regs[11] = 5;
    int taken = execute(0x00B50533u);
    int ok = (taken == 0) && regs[10] == 5;
    printf("%-28s 0x%08X  rejected=%s  a0 unchanged=%d  %s\n",
           "add is not THRESHOLD", 0x00B50533u, taken ? "no" : "yes", (int)regs[10],
           ok ? "PASS" : "FAIL");
    if (ok) pass_count++; else fail_count++;

    printf("\n%d passed, %d failed\n", pass_count, fail_count);
    return fail_count == 0 ? 0 : 1;
}
