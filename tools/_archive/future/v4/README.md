# V4 Maintainer Evidence

This directory preserves V4 design notes, evidence, release packets, and raw
benchmark material for maintainers.

New users should not start here. The current public V4 path is:

1. [../../README.md](../../README.md)
2. [../../docs/README.md](../../docs/README.md)
3. [../../tutorials/current/README.md](../../tutorials/current/README.md)
4. [../../examples/README.md](../../examples/README.md)

The public operator catalog is
[../../docs/learn/operator_catalog.md](../../docs/learn/operator_catalog.md).
The public app-level benchmark boundary is
[../../docs/app_level_benchmark_summary.md](../../docs/app_level_benchmark_summary.md).

Files under this directory are provenance, not first-time learning material.

Public claim reminder: most measured operators sit in the `1.2x` to `1.7x`
range against named brute-force partner/CPU baselines; larger outliers are
labeled as scale-dependent algorithmic-complexity wins. RT-BarnesHut
paper-reproduction wording remains outside the V4.0.0 public claim.

Release claim boundary: V4.0.0 does not claim that all benchmark apps are faster, does not authorize broad V4-over-V2.14 speedup wording, does not publish Tier-3 callback/PTX support claims, and does not make public true-zero-copy claims.
