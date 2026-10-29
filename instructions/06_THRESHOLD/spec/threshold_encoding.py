"""THRESHOLD custom instruction: encoding, decoding, golden model.

Instruction:  threshold rd, rs1, rs2   ->   rd = (rs1 >= rs2) ? 255 : 0   (signed compare, rs2 = threshold)
Format:       R-type on custom-0 opcode (0b0001011 = 0x0B), funct3 = 0, funct7 = 0 (assigned by TA)

Structure follows the teacher's mac_demo/mac_encoding.py.
"""

OPCODE_CUSTOM0 = 0b0001011
FUNCT3_THRESHOLD = 0b000
FUNCT7_THRESHOLD = 0b0000000
MASK32 = 0xFFFF_FFFF
INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1


def encode_threshold(rd: int, rs1: int, rs2: int) -> int:
    for name, r in (("rd", rd), ("rs1", rs1), ("rs2", rs2)):
        if not 0 <= r <= 31:
            raise ValueError(f"{name} out of range: {r}")
    return (
        (FUNCT7_THRESHOLD << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (FUNCT3_THRESHOLD << 12)
        | (rd << 7)
        | OPCODE_CUSTOM0
    )


def decode_threshold(word: int):
    """Return (rd, rs1, rs2) if the word is a THRESHOLD instruction, else None."""
    if word & 0x7F != OPCODE_CUSTOM0:
        return None
    if (word >> 12) & 0x7 != FUNCT3_THRESHOLD or (word >> 25) != FUNCT7_THRESHOLD:
        return None
    return (word >> 7) & 0x1F, (word >> 15) & 0x1F, (word >> 20) & 0x1F


def to_signed32(v: int) -> int:
    """Interpret the low 32 bits of v as a signed two's-complement number."""
    v &= MASK32
    return v - (1 << 32) if v & 0x8000_0000 else v


def threshold_golden(rs1: int, rs2: int) -> int:
    """Golden model: signed compare of the two 32-bit values."""
    return 255 if to_signed32(rs1) >= to_signed32(rs2) else 0


def apply_threshold(regs, word: int) -> bool:
    """Execute one word on a 32-entry register list. Writes to x0 are discarded.

    Returns True if the word was a THRESHOLD instruction, False otherwise (regs unchanged).
    """
    fields = decode_threshold(word)
    if fields is None:
        return False
    rd, rs1, rs2 = fields
    result = threshold_golden(regs[rs1], regs[rs2])
    if rd != 0:
        regs[rd] = result
    return True


if __name__ == "__main__":
    for name, (rd, rs1, rs2) in (("threshold a0, a0, a1", (10, 10, 11)),
                                 ("threshold t0, t0, t1", (5, 5, 6)),
                                 ("threshold x0, a0, a1", (0, 10, 11))):
        w = encode_threshold(rd, rs1, rs2)
        b = f"{w:032b}"
        print(f"{name:22s} 0x{w:08X}  {b[0:7]} {b[7:12]} {b[12:17]} {b[17:20]} {b[20:25]} {b[25:32]}")
