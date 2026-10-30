"""Compile riscv_probe.c with a RISC-V gcc and check the object code contains a THRESHOLD word.

Run inside WSL Ubuntu after installing gcc-riscv64-unknown-elf (see spec/README.md).
Skipped when no RISC-V toolchain is found. Follows mac_demo/test_riscv_encoding.py.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from threshold_encoding import decode_threshold

PREFIXES = ("riscv64-unknown-elf-", "riscv64-elf-")
GCC = next((shutil.which(p + "gcc") for p in PREFIXES if shutil.which(p + "gcc")), None)
OBJDUMP = next((shutil.which(p + "objdump") for p in PREFIXES if shutil.which(p + "objdump")), None)
HERE = Path(__file__).resolve().parent


@unittest.skipUnless(GCC and OBJDUMP, "RISC-V toolchain not installed")
class TestRiscvEncodingInCompilerOutput(unittest.TestCase):
    def test_threshold_insn_emits_custom0_encoding(self):
        with tempfile.TemporaryDirectory() as d:
            obj = Path(d) / "probe.o"
            subprocess.run(
                [GCC, "-march=rv32im", "-mabi=ilp32", "-ffreestanding", "-O1", "-c",
                 str(HERE / "riscv_probe.c"), "-I", str(HERE), "-o", str(obj)],
                check=True,
            )
            dump = subprocess.run([OBJDUMP, "-d", str(obj)], check=True,
                                  capture_output=True, text=True).stdout
            print("\n" + dump)
            words = []
            for line in dump.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].strip().endswith(":"):
                    try:
                        words.append(int(parts[1].strip().split()[0], 16))
                    except ValueError:
                        pass
            found = [(w, decode_threshold(w)) for w in words if decode_threshold(w) is not None]
            for w, (rd, rs1, rs2) in found:
                print(f"THRESHOLD word 0x{w:08X}: rd=x{rd} rs1=x{rs1} rs2=x{rs2}")
            self.assertTrue(found, "no custom-0 THRESHOLD instruction found in compiler output")


if __name__ == "__main__":
    unittest.main()
