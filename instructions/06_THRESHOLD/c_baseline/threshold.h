#ifndef THRESHOLD_H
#define THRESHOLD_H

#include <stdint.h>

/* THRESHOLD rd, rs1, rs2 : rd = (rs1 >= rs2) ? 255 : 0   (有號比較) */
int32_t threshold(int32_t rs1, int32_t rs2);

#endif
