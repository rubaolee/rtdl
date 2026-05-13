# Goal1858 — External Review: Goal1856 Overflow Fix and Refreshed Evidence

**Reviewer:** Claude (Sonnet 4.6, independent of Codex)
**Date:** 2026-05-13
**Verdict:** `accept-with-boundary`

---

## Summary

This review covers the Goal1856 follow-up fix: a host/device struct field-order
mismatch in `RayAnyHitAllWitnessesDeviceColumnsLaunchParams` that caused the
overflow guard to fire against the wrong capacity value, silently launcing fewer
rays than intended and suppressing the overflow signal. The fix, associated
contract test, and refreshed pod artifacts are sound. Overflow detection now
operates correctly for both CuPy and Torch at 512 and 2048 rows.

All claim boundaries from the original Goal1856 review (Goal1857) remain
blocked. The overflow gap cited as §5.7 in that review is resolved. The
remaining five open gaps from §5 are unchanged.

---

## Q1 — Does the Struct-Order Fix Correctly Address the Host/Device Mismatch?

**Yes. The fix is correct and the new contract test verifies the invariant.**

`rtdl_optix_workloads.cpp` lines 2990–3011 confirm the repaired layout:

```cpp
struct RayAnyHitAllWitnessesDeviceColumnsLaunchParams {
    // ... pointer fields omitted for brevity ...
    uint32_t*              emitted_count;
    uint32_t*              overflowed;
    uint32_t               witness_capacity;   // line 3009 — correct position
    uint32_t               ray_count;           // line 3010
};
```

`witness_capacity` precedes `ray_count`, matching the generated CUDA device
struct layout. Before the fix, the host struct had these two scalar fields
reversed, so a call with `ray_count=512` and `witness_capacity=256` would
deliver the values to the device swapped: the device read `witness_capacity`
as 512 (the actual ray count) and `ray_count` as 256 (the actual capacity),
launching only 256 rays against a perceived capacity of 512 and correctly
reporting no overflow — a silent correctness failure.

The Python contract test at
`tests/goal1848_optix_partner_bounded_all_witness_output_contract_test.py`
lines 73–76 now mechanically verifies the ordering on every CI run:

```python
self.assertLess(
    params_struct.index("uint32_t               witness_capacity;"),
    params_struct.index("uint32_t               ray_count;"),
)
```

This is a structural assertion that survives refactors that might accidentally
re-introduce the reversal. The post-fix overflow output cited in the handoff
(`emitted_count: 512, overflowed: True, exact_row_semantics_authorized: False`
at capacity 256) is the expected behaviour.

No objection to the fix or the test.

---

## Q2 — Do the Refreshed Artifacts Prove Fail-Closed Overflow Behavior?

**Yes for both partners at both scale points.**

### 512-row artifact (`goal1856_segment_polygon_v2_partner_perf_pod_512.json`)

| Partner | `overflow_check.status` | `tight_capacity` | `overflow_check.elapsed_s` |
|---------|------------------------|------------------|---------------------------|
| CuPy    | `pass`                 | 256              | 0.1348 s                  |
| Torch   | `pass`                 | 256              | 0.0103 s                  |

Both message strings are `"partner segment/polygon column adapter overflowed;
increase output_capacity"`. The overflow did not return rows — it raised a
`RuntimeError` before the timing loop, confirming fail-closed behavior.

### 2048-row artifact (`goal1856_segment_polygon_v2_partner_perf_pod_2048.json`)

| Partner | `overflow_check.status` | `tight_capacity` | `overflow_check.elapsed_s` |
|---------|------------------------|------------------|---------------------------|
| CuPy    | `pass`                 | 1024             | 0.1359 s                  |
| Torch   | `pass`                 | 1024             | 0.0106 s                  |

The tight capacity in both runs is `max(1, count // 2)`, correctly set to half
the row count, ensuring the output buffer overflows rather than merely filling.

**Observation on elapsed times:** CuPy overflow elapsed time (~135 ms at both
scales) is an order of magnitude longer than Torch (~10 ms at both scales).
Both confirm overflow detection, but this asymmetry likely reflects a CuPy
synchronization or stream-flush cost that occurs before the RuntimeError
propagates. This is not a correctness issue, but a future capacity-planning
benchmark should not infer CuPy overhead from the overflow path.

Both artifacts were produced from git commit `cb1937db4b36741897b3d0767ae15e147f0a6411`,
confirming they were built against the post-fix `librtdl_optix.so` described in
the handoff.

---

## Q3 — Are the Timing Evidence and Release/Speedup Boundaries Still Correctly Scoped?

**Yes. All claim boundaries are intact and consistent across artifact, report, and test.**

### Claim boundary table (both artifacts)

| Flag | Artifact | Runner code | Test assertion |
|------|---------|-------------|----------------|
| `same_contract_timing_row` | `true` | `True` literal | asserted present |
| `v2_0_release_authorized` | `false` | `False` literal | asserted false |
| `whole_app_speedup_claim_authorized` | `false` | `False` literal | asserted false |
| `broad_rt_core_speedup_claim_authorized` | `false` | `False` literal | asserted false |
| `package_install_claim_authorized` | `false` | `False` literal | asserted false |

The report (`goal1856_segment_polygon_v2_partner_perf_2026-05-13.md`) states
"not an all-app performance table and does not authorize v2.0 release wording."
Both the runner test and the scaled-artifact test assert `v2_0_release_authorized`
is false. The triple-check (source literal, artifact JSON, test assertion) is
the correct structure for a boundary that must not regress.

### Timing summary (post-fix runs)

**512 rows:**

| Path | Median query (s) | Ratio vs v1.8 |
|------|-----------------|---------------|
| v1.8 native OptiX | 0.001946 | 1.000× |
| v2.0 CuPy | 0.001127 | 0.579× |
| v2.0 Torch | 0.001054 | 0.542× |

**2048 rows:**

| Path | Median query (s) | Ratio vs v1.8 |
|------|-----------------|---------------|
| v1.8 native OptiX | 0.007565 | 1.000× |
| v2.0 CuPy | 0.002126 | 0.281× |
| v2.0 Torch | 0.002143 | 0.283× |

The test for the 2048-row artifact asserts `query_median_ratio_vs_v1_8_native < 0.5`
for both partners, which both pass (0.281x and 0.283x). These figures are
internal engineering data only and are not promoted to any public claim.

**Minor note on column_build_s values:** The 512-row report states
"CuPy caller column build: 0.0042869225 s" but the artifact records
`0.004222504794597626`. The 2048-row report states
"CuPy caller column build: 0.0070429966 s" but the artifact records
`0.007108539342880249`. The Torch values match to 10 significant digits
in both runs. The CuPy discrepancies (~1–2%) are small enough to suggest the
report was drafted from an intermediate run and the artifact captures the
final pod output. This is cosmetic and does not affect any conclusion, but it
should be noted as a minor documentation inconsistency.

---

## Q4 — Is Any Follow-Up Native Test or Pod Run Required Before the Next v2.0 App Adapter?

**No additional pod run is required for the overflow fix itself. Proceed with
the next adapter.**

The struct-order fix is complete, the contract test is in CI, and overflow
behavior is verified at two scale points for both partners. The fix resolves
the single highest-risk correctness issue introduced during the overflow check
addition.

The remaining open gaps from Goal1857 §5 are pre-existing and are not
invalidated by this fix:

| Gap | Status |
|-----|--------|
| §5.1 Column-build amortization and breakeven | **Open** |
| §5.2 Sample count (5 iterations) | **Open** |
| §5.3 Dataset scale (512/2048 rows only) | **Partially addressed** — 2048-row artifact added, but 3-OOM sweep remains outstanding |
| §5.4 Single app path | **Open** |
| §5.5 Single GPU / single pod | **Open** |
| §5.6 Synthetic 1:1 geometry parity | **Open** |
| §5.7 Overflow boundary test | **Resolved** by this goal |

None of §5.1–5.6 are blockers for beginning the next adapter goal. They block
only the public v2.0 performance claim and release authorization, which remain
correctly gated.

---

## Implementation Observations

**Positive:**

- The Python contract test extracts the struct body between the two struct
  delimiters and uses `str.index()` comparison, which is simple, unambiguous,
  and will catch any future field-order regression at the source level rather
  than relying on runtime behaviour.
- The overflow check is integrated into the perf runner as a default-on step
  (`--skip-overflow-check` is the opt-out), so future pod runs at any count
  automatically produce overflow evidence without requiring a separate run.
- The git_commit field in both artifacts matches the handoff's stated
  post-fix commit `cb1937db`, enabling exact reproduction.

**Non-blocking observations:**

- The CuPy overflow elapsed time (~135 ms) significantly exceeds the Torch
  path (~10 ms). If the overflow path is ever exercised in a production context
  (e.g., as a capacity auto-probe), the CuPy cost should be documented. For the
  current use case (pre-run guard), the cost is acceptable.
- The tight capacity formula `max(1, count // 2)` is correct for all `count ≥ 2`.
  For `count = 1`, tight_capacity = 1 = output_capacity = 2, which would not
  trigger overflow. This is a micro-scale edge case with no practical impact but
  worth noting if the harness is ever used at count=1 for debugging.

---

## Verdict

`accept-with-boundary`

The struct-order fix is mechanically correct, the new contract test enforces
the invariant on every CI run, and both refreshed artifacts confirm fail-closed
overflow behavior for CuPy and Torch at 512 and 2048 rows. Timing evidence
and all claim boundaries are correctly scoped and unchanged from the original
Goal1856 review.

The following remain **blocked**:

- v2.0 release authorization
- Any whole-app speedup claim
- Any broad RT-core speedup claim
- Any package-install claim
- Any public performance claim based on this data

Gap §5.7 (overflow boundary test) from the Goal1857 review is resolved.
Gaps §5.1–5.6 remain open and must be addressed before any public v2.0
performance claim.
