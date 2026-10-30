"""Binarize benchmark: standard RV32IM loop vs THRESHOLD loop (instruction-count model, CPI = 1).

CPU Time = Instruction Count x CPI x Clock Cycle Time.  Model estimate, not a measurement.
Only the RV32IM branch version is checked in Ripes (threshold_loop_rv32im.s, N = 8);
general Ripes cannot execute custom-0, so the THRESHOLD column is derived from the loop below.
Structure follows the teacher's mac_demo/benchmark/dotbench.py.

Loop bodies (dynamic instructions per element):
  branch    (CP2 style, bge):  lw, bge, li, [j], sw, addi, addi, addi, bnez -> 8 if in >= limit else 9
  branchless (slt):            lw, slt, addi, andi, sw, addi, addi, addi, bnez -> 9
  threshold (custom):          lw, threshold, sw, addi, addi, addi, bnez       -> 7
Fixed cost per run: setup 6 (la x2 = 4, li x2 = 2) + exit 2 (li a7, ecall).
"""

import random

from threshold_encoding import INT32_MAX, INT32_MIN, threshold_golden

SEED = 2026
SETUP = 6
EXIT = 2
RATIOS = (1.0, 1.1, 1.2)

WORKLOADS = [
    {"id": "W1", "kind": "pixel", "n": 64},
    {"id": "W1", "kind": "pixel", "n": 256},
    {"id": "W1", "kind": "pixel", "n": 1024},
    {"id": "W2", "kind": "full_range", "n": 256},
    {"id": "W3", "kind": "edge", "n": 64},
]


def make_inputs(kind: str, n: int, seed: int = SEED):
    """Return (values, limit)."""
    rng = random.Random(seed)
    if kind == "pixel":
        return [rng.randint(0, 255) for _ in range(n)], 128
    if kind == "full_range":
        return [rng.randint(INT32_MIN, INT32_MAX) for _ in range(n)], 0
    if kind == "edge":
        return [INT32_MAX if i % 2 == 0 else INT32_MIN for i in range(n)], -1
    raise ValueError(kind)


def baseline_branch_result(value: int, limit: int) -> int:
    """What the bge loop computes (signed compare via Python ints)."""
    return 255 if value >= limit else 0


def baseline_branchless_result(value: int, limit: int) -> int:
    """What slt / addi -1 / andi 255 computes."""
    t = 1 if value < limit else 0
    return (t - 1) & 0xFF


def count_branch(values, limit) -> int:
    body = sum(8 if v >= limit else 9 for v in values)
    return SETUP + body + EXIT


def count_branchless(values) -> int:
    return SETUP + 9 * len(values) + EXIT


def count_threshold(values) -> int:
    return SETUP + 7 * len(values) + EXIT


def run_case(kind: str, n: int, ratio: float = 1.0):
    values, limit = make_inputs(kind, n)
    golden = [threshold_golden(v, limit) for v in values]
    correct = (golden == [baseline_branch_result(v, limit) for v in values]
               == [baseline_branchless_result(v, limit) for v in values])
    ic_branch = count_branch(values, limit)
    ic_branchless = count_branchless(values)
    ic_custom = count_threshold(values)
    return {
        "kind": kind,
        "n": n,
        "ratio": ratio,
        "ic_branch": ic_branch,
        "ic_branchless": ic_branchless,
        "ic_threshold": ic_custom,
        "correct": correct,
        "speedup_branch": ic_branch / (ic_custom * ratio),
        "speedup_branchless": ic_branchless / (ic_custom * ratio),
    }


def run_all(ratios=RATIOS):
    return [run_case(w["kind"], w["n"], r) for r in ratios for w in WORKLOADS]


def to_markdown(rows) -> str:
    out = ["| workload | N | T ratio | IC branch | IC branchless | IC threshold | correct | speedup vs branch | speedup vs branchless |",
           "|---|---:|---:|---:|---:|---:|:---:|---:|---:|"]
    for r in rows:
        out.append(f"| {r['kind']} | {r['n']} | {r['ratio']:.1f} | {r['ic_branch']} | {r['ic_branchless']} | "
                   f"{r['ic_threshold']} | {'OK' if r['correct'] else 'FAIL'} | "
                   f"{r['speedup_branch']:.2f}x | {r['speedup_branchless']:.2f}x |")
    return "\n".join(out)


def ripes_case():
    """The exact N = 8 input of threshold_loop_rv32im.s, for comparing with Ripes."""
    values = [5, 4, -1, INT32_MAX, INT32_MIN, 0, 7, -3]
    return values, 5, count_branch(values, 5), count_threshold(values)


if __name__ == "__main__":
    values, limit, ic_b, ic_t = ripes_case()
    print(f"Ripes case N=8 limit={limit}: model IC branch = {ic_b}, threshold = {ic_t}, "
          f"speedup = {ic_b / ic_t:.2f}x")
    print("expected out =", [threshold_golden(v, limit) for v in values])
    print()
    print(to_markdown(run_all()))
