/*
 * 有號 vs 無號比較實驗(CP1 報告第 3 段)
 *
 * 目的:驗證規格要求的「有號比較」不能用 uint32_t 實作。
 * 作法:用同樣 12 組測資,分別呼叫
 *   - threshold()   :正式的 C 參考實作(int32_t,有號比較)
 *   - threshold_u() :實驗版,把同一組位元當作 uint32_t 做無號比較
 * 並與預期輸出比對。
 *
 * 編譯與執行(在 instructions/06_THRESHOLD/tests/ 底下):
 *   gcc -std=c11 -Wall -Wextra -I../c_baseline signed_vs_unsigned.c ../c_baseline/threshold.c -o signed_vs_unsigned
 *   ./signed_vs_unsigned
 *
 * 測資與 threshold_tests.md 的 12 組相同。
 */
#include <stdint.h>
#include <stdio.h>

#include "threshold.h"

/* 實驗版:同一組位元,當作無號數比較(錯誤的做法) */
static int32_t threshold_u(uint32_t rs1, uint32_t rs2)
{
    return (rs1 >= rs2) ? 255 : 0;
}

struct test_case {
    int32_t rs1;
    int32_t rs2;
    int32_t expected;
};

int main(void)
{
    const struct test_case cases[] = {
        {5, 5, 255},
        {4, 5, 0},
        {-1, 0, 0},
        {7, 3, 255},
        {3, 7, 0},
        {0, 0, 255},
        {-3, -5, 255},
        {-3, 2, 0},
        {2, -3, 255},
        {INT32_MAX, INT32_MAX - 1, 255},
        {INT32_MIN, INT32_MIN + 1, 0},
        {INT32_MIN + 1, INT32_MIN, 255},
    };
    const int n = (int)(sizeof cases / sizeof cases[0]);
    int bad_signed = 0;
    int bad_unsigned = 0;

    printf("%-24s %8s %9s %10s\n", "(rs1, rs2)", "expected", "int32_t", "uint32_t");
    for (int i = 0; i < n; i++) {
        int32_t s = threshold(cases[i].rs1, cases[i].rs2);
        int32_t u = threshold_u((uint32_t)cases[i].rs1, (uint32_t)cases[i].rs2);

        if (s != cases[i].expected) {
            bad_signed++;
        }
        if (u != cases[i].expected) {
            bad_unsigned++;
        }
        printf("(%11d,%11d) %8d %9d %10d%s\n", cases[i].rs1, cases[i].rs2,
               cases[i].expected, s, u,
               (u != cases[i].expected) ? "   <-- 無號版錯誤" : "");
    }

    printf("\nint32_t  版失敗 %d 組\n", bad_signed);
    printf("uint32_t 版失敗 %d 組\n", bad_unsigned);
    printf("(uint32_t)-1 = %u\n", (uint32_t)-1);

    /* 正式實作必須全部通過 */
    return bad_signed != 0;
}
