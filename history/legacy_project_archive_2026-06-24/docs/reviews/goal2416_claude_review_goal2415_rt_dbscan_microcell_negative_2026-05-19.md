# Goal2416 Claude Review: Goal2415 RT-DBSCAN Microcell Negative Result

Date: 2026-05-19

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept**

---

## Scope

This review covers:

- The Goal2415 pod evidence report and six JSON timing artifacts
- The Goal2414 unit test results recorded on the pod
- The `future_version_to_do_list.md` entry under
  `RT-DBSCAN-Informed Fixed-Radius Component Continuation`
- The four handoff questions about correctness validity, promotion decision,
  pivot target, and implementation guardrails

---

## Q1: Is the corrected microcell continuation correctness-valid but performance-negative?

**Accept.**

Correctness evidence is solid:

- `goal2414_unittest.txt` records five tests, all passing, on the pod at commit
  `0d95c045`.
- All six timing artifacts report `signatures_match = true`. This covers both
  dataset shapes and all three point-count tiers (32k, 65k, 131k).

The performance-negative conclusion is directly supported by the warm-tail
timing in every artifact:

| Dataset / points | RT-grid app sec | Microcell app sec | Ratio |
| --- | ---: | ---: | ---: |
| clustered3d / 32768 | 0.209644 | 0.239261 | 1.141x |
| clustered3d / 65536 | 0.543523 | 0.572950 | 1.054x |
| clustered3d / 131072 | 1.407486 | 1.412520 | 1.004x |
| road3d / 32768 | 0.194789 | 0.298301 | 1.531x |
| road3d / 65536 | 0.451593 | 0.748663 | 1.658x |
| road3d / 131072 | 1.056031 | 2.162319 | 2.048x |

No artifact shows a microcell speedup. The `clustered3d/32768` row records a
correct fallback with `fallback_reason = "not_all_points_core"`, which is itself
a real correctness boundary: the microcell fast path requires all points to be
core points and cannot activate without that guarantee.

The mechanistic explanation is consistent with the data: `radius / sqrt(3)`
microcells are clique-safe by construction but produce more cells than the
radius grid, require a `5 x 5 x 5` neighbor stencil instead of `3 x 3 x 3`,
and add exact cross-microcell pair checks. Sparse road-shaped data suffers most
because microcells have low useful aggregation per cell but still pay the full
stencil cost.

---

## Q2: Does the pod evidence support not promoting the microcell path?

**Yes, conclusively.**

Five of six artifacts show the fast path activating and still losing. The one
exception (`clustered3d/32768`) never activates the fast path at all. For
road-shaped data the degradation is severe:

- `road3d/65536` continuation: 0.431s microcell vs 0.088s CuPy-grid (4.9x
  slower)
- `road3d/131072` continuation: 1.515s microcell vs 0.292s CuPy-grid (5.2x
  slower)

At the closest point (`clustered3d/131072`), microcell nearly ties the existing
RT-grid path (1.4125s vs 1.4075s, within measurement noise), but does not beat
it. No evidence exists that a tighter tuning of the current microcell design
would cross into positive territory on road-shaped inputs.

The test `test_microcell_fast_path_activated_but_did_not_beat_existing_rt_grid`
codifies this conclusion correctly: fast path activated on at least one row, and
`tail_median(microcell) >= tail_median(RT-grid)` holds for all five activating
artifacts.

The `future_version_to_do_list.md` entry records the decision accurately:

> Do not treat microcell graph compression as the next performance path for
> RT-DBSCAN.

This reviewer agrees.

---

## Q3: Is the pivot to prepared CuPy grid continuation hardening the right next target?

**Yes.**

The existing CuPy device-grid continuation is already the stronger algorithmic
base. Road3d continuation at 131k takes 0.292s with the grid path versus 1.515s
with microcell. The grid path is not a weak baseline being protected by inertia;
it genuinely dominates across both data shapes.

The prepared-grid hardening target attacks a real cost: the continuation
re-derives point columns, cell ids, sorted order, unique cells, starts/counts,
and output buffers on every call, even though none of that geometric state
changes between repeated fixed-radius queries on the same point set. Caching
and reusing that state is a bounded, lower-risk engineering target with a clear
payoff path and no correctness complexity beyond a cache-validity gate.

This contrasts favorably with further microcell work, which would require either
a tighter cell size (risking correctness regression) or a different stencil
reduction strategy (uncharted territory with no current evidence of viability).

---

## Q4: Implementation guardrails for the next prepared-grid goal

The following guardrails should be written into the next goal's contract before
any implementation begins.

**Contract shape**

Keep the primitive generic: fixed-radius component-label output, grouped
union-find continuation, or row-stream continuation. Do not add
DBSCAN-specific parameter names or semantic fields to the prepared state API or
claim metadata. The contract must remain usable by any fixed-radius graph
application, not just DBSCAN.

**Prepared state scope**

The cached state is: point columns, cell ids, sorted order (argsort), unique
cells, starts, counts, and pre-allocated output label buffers. These are all
derivable from the point geometry and the radius parameter alone. The prepared
state key must be stable under repeated calls on the same geometry; it must not
embed application-layer parameters (density threshold, min-neighbor count) that
are not part of the grid structure.

**Correctness gate before any timing claim**

Before recording any timing comparison, the goal must run a fresh (uncached) and
a prepared path on the same input and assert `signatures_match` between their
outputs. A timing artifact that does not carry a `signatures_match = true` field
is not admissible as evidence.

**Dataset coverage**

Test on both `clustered3d` and `road3d` at all three tier sizes (32k, 65k,
131k). Road3d at 131k is the hard case; a prepared-grid win there is stronger
evidence than a clustered-only result because the road shape is where the
existing continuation is cheapest, making a genuine speedup harder to achieve.

**Claim metadata**

Preserve explicit claim metadata fields for: RT-core phase flag, partner
continuation phase flag, row materialization policy, and zero-copy/direct-device
handoff policy. Mark `steady_state_probe_only = true` until a complete
pod-run comparison establishes full pipeline timing (RT-count phase plus
continuation).

**Claim boundary**

Do not authorize a broad RT-core speedup claim, a paper-dataset reproduction
claim, or a v2.x closure from a prepared-grid continuation result alone. The
prepared-grid work is an internal engineering improvement to continuation cost.
Speedup over the pure CuPy baseline requires the full pipeline (RT-count phase
plus prepared continuation) to beat pure CuPy in warm-tail median, verified on
pod, before any external speedup claim is recorded.

---

## Evidence Integrity

All six JSON artifacts were read directly for this review. Warm-tail medians
(median of repeats 2 and 3) were independently verified against the values in
the report summary table; all values match to the reported precision. The unit
test output records five passing tests. The environment file confirms the pod
hardware, driver, CUDA version, and commit used.

No anomalies were found in the artifact structure. All artifacts carry
`claim_boundary.broad_rt_core_speedup_claim_authorized = false` and
`steady_state_probe_only = true`, consistent with the scope stated in the
report.

---

## Boundary

This review does not authorize a release claim, a broad RT-core speedup claim,
an RT-DBSCAN paper reproduction claim, or v2.x closure. It records acceptance
of a negative performance result and endorses the stated pivot to prepared CuPy
grid continuation hardening.
