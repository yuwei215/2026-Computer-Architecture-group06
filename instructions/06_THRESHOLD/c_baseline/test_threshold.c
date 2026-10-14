/*
 * THRESHOLD 測試程式(CP1)
 *
 * 用 threshold_tests.md 的 12 組測資,逐筆呼叫 C 參考實作 threshold(),
 * 把「預期輸出」和「實際輸出」並排印出,並回報通過/失敗。
 * 全部通過時程式結束碼為 0,有任何一組失敗則為 1。
 *
 * 編譯與執行(在 instructions/06_THRESHOLD/c_baseline/ 底下):
 *   gcc -std=c11 -Wall -Wextra test_threshold.c threshold.c -o test_threshold
 *   ./test_threshold
 *
 * 注意:下面的測資必須和 threshold_tests.md 保持一致。
 */
#include <stdint.h>
#include <stdio.h>

#include "threshold.h"

struct test_case {
    const char *name;
    int32_t rs1;
    int32_t rs2;
    int32_t expected;
};

int main(void)
{
    const struct test_case cases[] = {
        {"官方:相等", 5, 5, 255},
        {"官方:差 1", 4, 5, 0},
        {"官方:負對 0", -1, 0, 0},
        {"正數大於門檻", 7, 3, 255},
        {"正數小於門檻", 3, 7, 0},
        {"兩個都是 0", 0, 0, 255},
        {"兩個都是負數", -3, -5, 255},
        {"負數對正數", -3, 2, 0},
        {"正數對負數", 2, -3, 255},
        {"邊界:rs1 = INT32_MAX", INT32_MAX, INT32_MAX - 1, 255},
        {"邊界:rs1 = INT32_MIN", INT32_MIN, INT32_MIN + 1, 0},
        {"邊界:rs2 = INT32_MIN", INT32_MIN + 1, INT32_MIN, 255},
    };
    const int n = (int)(sizeof cases / sizeof cases[0]);
    int failed = 0;

    printf("%-3s %-22s %12s %12s %8s %8s  %s\n", "#", "類型", "rs1", "rs2", "預期", "實際", "結果");
    for (int i = 0; i < n; i++) {
        int32_t actual = threshold(cases[i].rs1, cases[i].rs2);
        int ok = (actual == cases[i].expected);

        if (!ok) {
            failed++;
        }
        printf("%-3d %-22s %12d %12d %8d %8d  %s\n", i + 1, cases[i].name,
               cases[i].rs1, cases[i].rs2, cases[i].expected, actual,
               ok ? "PASS" : "FAIL");
    }

    printf("\n共 %d 組,通過 %d 組,失敗 %d 組\n", n, n - failed, failed);
    return failed != 0;
}
