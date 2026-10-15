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
 * 輸出訊息使用英文,避免 Windows 終端機的中文編碼造成亂碼。
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
        {"official: equal", 5, 5, 255},
        {"official: off by one", 4, 5, 0},
        {"official: negative vs 0", -1, 0, 0},
        {"positive > threshold", 7, 3, 255},
        {"positive < threshold", 3, 7, 0},
        {"both zero", 0, 0, 255},
        {"both negative", -3, -5, 255},
        {"negative vs positive", -3, 2, 0},
        {"positive vs negative", 2, -3, 255},
        {"boundary: rs1 = INT32_MAX", INT32_MAX, INT32_MAX - 1, 255},
        {"boundary: rs1 = INT32_MIN", INT32_MIN, INT32_MIN + 1, 0},
        {"boundary: rs2 = INT32_MIN", INT32_MIN + 1, INT32_MIN, 255},
    };
    const int n = (int)(sizeof cases / sizeof cases[0]);
    int failed = 0;

    printf("%-3s %-22s %12s %12s %8s %8s  %s\n", "#", "case", "rs1", "rs2", "expected", "actual", "result");
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

    printf("\nTotal %d, passed %d, failed %d\n", n, n - failed, failed);
    return failed != 0;
}
