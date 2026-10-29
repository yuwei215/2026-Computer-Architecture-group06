#ifndef THRESHOLD_H
#define THRESHOLD_H

#include <stdint.h>

/* threshold rd, rs1, rs2 : rd = (rs1 >= rs2) ? 255 : 0  (signed, custom-0, R-type, funct3=0, funct7=0) */
static inline int32_t threshold_insn(int32_t value, int32_t limit)
{
#if defined(__riscv)
    int32_t rd;
    __asm__ volatile(".insn r 0x0b, 0, 0, %0, %1, %2"
                     : "=r"(rd)
                     : "r"(value), "r"(limit));
    return rd;
#else
    return (value >= limit) ? 255 : 0;
#endif
}

#endif
