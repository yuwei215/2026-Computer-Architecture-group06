#include <stdint.h>

#include "threshold.h"

int32_t threshold_probe(int32_t value, int32_t limit)
{
    return threshold_insn(value, limit);
}
