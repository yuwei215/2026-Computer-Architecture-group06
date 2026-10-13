#include "threshold.h"

int32_t threshold(int32_t rs1, int32_t rs2)
{
    if (rs1 >= rs2) {
        return 255;
    } else {
        return 0;
    }
}
