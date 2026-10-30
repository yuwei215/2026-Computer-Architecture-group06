import unittest

from threshold_encoding import (
    INT32_MAX,
    INT32_MIN,
    OPCODE_CUSTOM0,
    apply_threshold,
    decode_threshold,
    encode_threshold,
    threshold_golden,
)


class TestEncoding(unittest.TestCase):
    def test_known_encodings_match_hand_calculation(self):
        # Hand-calculated values in spec/README.md section B (by Chien Chia Yu)
        self.assertEqual(encode_threshold(10, 10, 11), 0x00B5050B)  # threshold a0, a0, a1
        self.assertEqual(encode_threshold(5, 5, 6), 0x0062828B)     # threshold t0, t0, t1

    def test_fields(self):
        word = encode_threshold(10, 10, 11)
        self.assertEqual(word & 0x7F, OPCODE_CUSTOM0)
        self.assertEqual((word >> 7) & 0x1F, 10)
        self.assertEqual((word >> 12) & 0x7, 0)
        self.assertEqual((word >> 15) & 0x1F, 10)
        self.assertEqual((word >> 20) & 0x1F, 11)
        self.assertEqual(word >> 25, 0)

    def test_round_trip_all_registers(self):
        for rd in range(32):
            for rs1, rs2 in ((0, 31), (31, 0), (10, 11), (5, 6)):
                self.assertEqual(decode_threshold(encode_threshold(rd, rs1, rs2)), (rd, rs1, rs2))

    def test_range_checked(self):
        with self.assertRaises(ValueError):
            encode_threshold(32, 0, 0)
        with self.assertRaises(ValueError):
            encode_threshold(0, -1, 0)

    def test_other_instructions_are_not_threshold(self):
        self.assertIsNone(decode_threshold(0x00B50533))  # add a0, a0, a1 (opcode 0110011)
        word = encode_threshold(10, 10, 11)
        self.assertIsNone(decode_threshold(word | (1 << 12)))  # funct3 = 1
        self.assertIsNone(decode_threshold(word | (1 << 25)))  # funct7 = 1


class TestSemantics(unittest.TestCase):
    def test_official_vectors(self):
        self.assertEqual(threshold_golden(5, 5), 255)
        self.assertEqual(threshold_golden(4, 5), 0)
        self.assertEqual(threshold_golden(-1, 0), 0)

    def test_boundaries(self):
        self.assertEqual(threshold_golden(INT32_MAX, INT32_MIN), 255)
        self.assertEqual(threshold_golden(INT32_MIN, INT32_MAX), 0)
        self.assertEqual(threshold_golden(INT32_MIN, INT32_MIN), 255)
        self.assertEqual(threshold_golden(INT32_MAX, INT32_MAX), 255)

    def test_rs2_min_always_255(self):
        for rs1 in (INT32_MIN, -1, 0, 1, INT32_MAX):
            self.assertEqual(threshold_golden(rs1, INT32_MIN), 255)

    def test_signed_not_unsigned(self):
        # Register bit patterns: 0xFFFFFFFF is -1 when signed, so -1 >= 0 is false
        self.assertEqual(threshold_golden(0xFFFFFFFF, 0), 0)
        self.assertEqual(threshold_golden(0x7FFFFFFF, 0x80000000), 255)

    def test_result_is_only_0_or_255(self):
        for a in (INT32_MIN, -5, -1, 0, 1, 5, INT32_MAX):
            for b in (INT32_MIN, -5, -1, 0, 1, 5, INT32_MAX):
                self.assertIn(threshold_golden(a, b), (0, 255))


class TestExecute(unittest.TestCase):
    def test_writes_rd(self):
        regs = [0] * 32
        regs[10], regs[11] = 5, 5
        self.assertTrue(apply_threshold(regs, 0x00B5050B))
        self.assertEqual(regs[10], 255)

    def test_rd_x0_is_discarded(self):
        regs = [0] * 32
        regs[10], regs[11] = 5, 5
        self.assertTrue(apply_threshold(regs, encode_threshold(0, 10, 11)))
        self.assertEqual(regs[0], 0)
        self.assertEqual(regs[10], 5)

    def test_non_threshold_word_changes_nothing(self):
        regs = [0] * 32
        regs[10], regs[11] = 5, 5
        self.assertFalse(apply_threshold(regs, 0x00B50533))
        self.assertEqual(regs[10], 5)


if __name__ == "__main__":
    unittest.main()
