# Goal980 Graph Baseline Correctness Audit

Date: 2026-04-26

Goal980 audits local graph baseline correctness only. It does not repair native graph kernels, collect cloud data, or authorize public speedup claims.

- status: `ok`
- mismatch rows: `0`
- public speedup authorized: `False`
- claim effect: graph local correctness check passed; timing review is still separate

| Copies | CPU sec | Embree sec | Status | Mismatched sections |
| ---: | ---: | ---: | --- | --- |
| 1 | 0.010130 | 0.010823 | `ok` |  |
| 2 | 0.000179 | 0.000256 | `ok` |  |
| 8 | 0.000752 | 0.000466 | `ok` |  |
| 16 | 0.002487 | 0.000743 | `ok` |  |
| 256 | 0.669467 | 0.009488 | `ok` |  |

## Mismatch Detail
