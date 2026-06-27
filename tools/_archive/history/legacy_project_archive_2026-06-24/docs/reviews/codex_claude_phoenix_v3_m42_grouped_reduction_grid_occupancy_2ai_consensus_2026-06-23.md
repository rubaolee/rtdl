# Codex + Claude Consensus: Phoenix V3 M42 Grouped-Reduction Grid Occupancy

Date: 2026-06-23

Consensus verdict: `accept_m42_shape_positive_require_tiled_kernel`

Inputs:

- Codex report: `docs/reports/phoenix_v3_m42_grouped_reduction_grid_occupancy_root_cause_2026-06-23.md`
- Claude recorded review: `docs/reviews/claude_phoenix_v3_m42_grouped_reduction_grid_occupancy_recorded_review_2026-06-23.md`
- Evidence: `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m42_lx1_shape_262144x65536_20260623_151852/summary.json`

## Agreement

Codex and Claude agree that the M41 serious free-local grouped-reduction blocker was a kernel launch-shape problem:

- The current offsets kernel parallelizes over `group_count`.
- At `262144` rows / `1024` groups, `program_count = ceil(1024 / 256) = 4`.
- Increasing `row_count` at fixed `1024` groups would not improve occupancy.
- Reducing `group_count` to `64` would worsen occupancy.
- The M42 shape (`262144` rows / `65536` groups) validly tested the hypothesis by increasing `program_count` to `256`.

M42 result:

- failed checks: `0`
- correctness: `allclose=true`
- runtime trunk executes end-to-end: `true`
- internal device residency between RTDL phases: `true`
- hot-path host materialization: `false`
- runner vs CPU hot: `6.443935850755532x`
- runner vs legacy hot: `18.706881313407262x`
- runner vs legacy wall: `25.558762196642736x`

This is accepted as real shape-positive generic grouped-reduction evidence.

## Required Redirect

M42 does not close grouped reduction as a full Step-2 family. Claude's review is correct: high-group-count / low-rows-per-group shapes work, but common low- or moderate-group-count shapes remain structurally disadvantaged because one CUDA thread serially reduces one whole group.

Authorized next step:

```text
M43 local-only tiled/row-parallel grouped-reduction kernel implementation.
```

M43 must remain generic runtime work:

- no app-specific route tuning
- no paid POD
- no all-app run
- no release decision
- no public speedup wording
- no broad V3-over-V2 claim
- no V4, embedding, C ABI, or true-zero-copy work

## M43 Acceptance Shape

The M43 local evidence should include at least the original blocked shape:

```text
row_count = 262144
group_count = 1024
```

It may also include one high-group-count sanity row, but the important pass condition is that the productized runner improves the original low-occupancy shape without weakening correctness or residency metadata.

The minimum local gate before any later external spend request:

- failed checks `0`
- all variants allclose `true`
- runtime trunk executes end-to-end `true`
- internal device residency `true`
- hot-path host materialization `false`
- launch metadata reports the tiled/row-parallel strategy
- `runner_vs_cpu_hot_speedup >= 1.0x` on `262144 x 1024`

## Goal-Level Decision Audit

Decision: accept M42 as shape-positive but require M43 tiled/row-parallel kernel work before grouped reduction can close as a Step-2 family.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be to declare grouped reduction done from the `65536`-group shape alone, hiding the original `1024`-group CPU inversion.
3. Was there another path that would avoid being stuck? Yes. We could abandon grouped reduction and switch family, but M42 proved the generic trunk works when launch shape is adequate, so a bounded local kernel fix is now the higher-value path.
4. Can I now try a different path that actually solves the problem? Yes. M43 is the different path: change the generic kernel's parallelization strategy, then rerun the original blocked shape locally before any paid-POD or release action.

## Non-Authorization

This consensus does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

