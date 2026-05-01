# Goal879 External Review — 2026-04-24

**Verdict: ACCEPT**

No correctness or API blockers. Changes are ready to commit as a local
app-surface improvement pending RTX artifact work.

---

## Question-by-question findings

### 1. Is `directed_threshold_prepared` a valid RT traversal mapping?

Yes. The Hausdorff <= radius decision reduces to two directed membership
queries: every point in A has a point in B within r, and vice versa.
`prepare_optix_fixed_radius_count_threshold_2d(..., threshold=1)` is exactly
that primitive. The two-pass structure in `_run_optix_directed_threshold` is
correct, and `_directed_threshold_from_count_rows` treats any point missing
from the result as a violation (default `threshold_reached=0`), which is
conservative and safe.

### 2. Does the implementation avoid claiming exact Hausdorff-distance acceleration?

Yes, consistently:
- `hausdorff_distance` key is `None` in the threshold path output (line 283).
- `rtdl_role` text explicitly says "decision subproblem … every source point
  has at least one target within the threshold."
- `rt_core_accelerated: True` is set only for the threshold path, not the KNN
  rows path (`rt_core_accelerated: False` on line 354).
- Matrix blocker note: "exact Hausdorff distance remains CUDA-through-OptiX
  KNN rows."
- Allowed claim: "prepared Hausdorff <= radius decision sub-path only; no
  exact-distance speedup claim."

No overclaim found anywhere.

### 3. Are the matrix changes conservative enough?

Yes. The three classifications mirror the identical stage used by
`service_coverage_gaps` and `event_hotspot_screening`:

| Dimension | Value | Rationale |
|---|---|---|
| `performance_class` | `optix_traversal_prepared_summary` | Only the explicit threshold mode uses traversal; default KNN rows path is CUDA-through-OptiX |
| benchmark readiness | `needs_real_rtx_artifact` | Local dry-run and baseline work complete; real RTX artifact not yet collected |
| RT-core maturity | `rt_core_partial_ready` | Threshold sub-path is traversal-backed; exact-distance KNN rows remain outside the claim |

The `_OPTIX_BENCHMARK_READINESS_MATRIX` blocker text is accurate: "exact
Hausdorff distance remains CUDA-through-OptiX KNN rows; only the threshold
decision sub-path is traversal-backed."

### 4. Correctness or API blockers?

None found.

- `_directed_threshold_from_count_rows` logic is correct; missing query IDs
  default to violating.
- `oracle_within_threshold` tolerance (`<= threshold + 1e-12`) is appropriate
  for floating-point fixture comparison.
- `matches_oracle` boolean comparison is correct.
- `--require-rt-core` guard (lines 95–104) correctly rejects any non-threshold
  OptiX path.
- Negative threshold input validation is present and tested.
- Goal690 and Goal705 tests confirm `hausdorff_distance` is classified as
  `optix_traversal_prepared_summary` / `needs_real_rtx_artifact` in the pinned
  fixture assertions.

**Minor gap (not a blocker):** `_FakePreparedThreshold` in the test always
returns `threshold_reached=1` for all points, so the "some points violate
threshold" path is not unit-tested. The production logic for that path is
straightforward and correct, but a follow-up test covering the False branch
would improve confidence.

---

## Summary

All four review questions are satisfied. The implementation is a well-scoped,
correctly-bounded local app surface improvement. The `needs_real_rtx_artifact`
classification is the correct gate; no cloud or speedup claim is authorized
until that gate passes (Goal879 next step).
