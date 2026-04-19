# Goal595 External Review

**Date:** 2026-04-19
**Verdict:** BLOCK

---

## Summary

The harness is well-structured and the report is honest about scope. However, the `ray_triangle_closest_hit_3d` workload—the only one where Apple RT outperforms Embree—has pathologically high variance that disqualifies it as a repeatable baseline. The other two workloads are stable but show Apple RT 12–142x slower than Embree.

---

## What passes

**Harness design**
- `native_only=True` on every `run_apple_rt` call prevents silent fallback to a non-Apple-RT path. This is correct.
- Cold call is recorded separately and excluded from the sample window. Methodology is transparent.
- `_rows_match` applies per-field float tolerance (`rel_tol=1e-5`/`abs_tol=1e-5` for `t`, `1e-6` for intersection points). Parity check is meaningful, not a trivial identity comparison.
- All three workloads pass parity (`matches_cpu_reference: true`). Correctness is not in question.

**Report honesty**
- The report explicitly labels itself "local measurement artifact" and "v0.9.2 baseline gate — not a final performance claim."
- The 142x and 12x regressions on `hit_count_3d` and `segment_intersection_2d` are reported without hedging. This is the right posture for a baseline document.

**Tests**
- The two unit tests cover the correct things: `_stats` field completeness and `_rows_match` float tolerance semantics. Minimal but not wrong.

---

## What blocks

### Critical: `ray_triangle_closest_hit_3d` apple_rt variance is non-repeatable

Raw apple_rt samples for this workload (seconds):

```
0.001341, 0.001444, 0.001356, 0.012109, 0.003021, 0.001705, 0.008023
```

- **min:** 1.34 ms, **median:** 1.70 ms, **max:** 12.11 ms
- **stdev:** 4.25 ms, **mean:** 4.14 ms
- **CV (stdev/mean): 1.03** — the standard deviation exceeds the mean.

A coefficient of variation above 1.0 means the distribution is dominated by outliers, not the central tendency. The median of 1.70 ms sits in a cluster of three fast samples, but 3 of 7 samples (43%) are 1.8–7.1× slower than that median. With only 7 repeats and 2 warmups, the "fast cluster" could reflect a warm GPU/NPU cache state that does not persist across benchmark runs in a different process or thermal state.

The reported Apple/Embree ratio of **0.663×** comes entirely from this unstable median. It is the only result that makes Apple RT look faster, and it is also the least reliable number in the report. Presenting it as a baseline invites future optimization goals to compare against a floor that may not be reproducible.

By contrast, embree's CV for the same workload is 4.5% (stdev 0.118 ms / mean 2.60 ms), and apple_rt's CV for the other two workloads is 9.4% and 13.9% — high but plausible for a maturing backend. The closest_hit_3d result is a qualitatively different failure mode.

### Minor: no CV or stability gate in the harness

The harness collects stdev but does not compute or report CV, and does not fail or warn when variance exceeds a threshold. A repeatable-baseline harness should refuse to write output (or at least emit a prominent warning) when `stdev / mean > threshold` for any backend result.

---

## Required before ACCEPT

1. **Increase warmups and repeats for apple_rt** on `ray_triangle_closest_hit_3d`. Try warmups=5, repeats=20 and check whether the fast cluster or the slow outliers dominate. If outliers persist, the workload is not ready for baselining under current Apple RT state.

2. **Add a CV gate.** After collecting samples, compute `stdev / mean`. If CV > 0.15 for any backend/workload pair, print a warning and either refuse to write the report or mark that cell as `UNSTABLE` in the markdown table.

3. **Re-run and re-submit** the `.json` and `.md` artifacts after the above changes. If the re-run shows apple_rt consistently below Embree on `closest_hit_3d` with CV < 0.15, the ACCEPT verdict is straightforward given that parity and honesty are already in good shape.

---

## Not blocking (informational)

- The 142× slowdown on `ray_triangle_hit_count_3d` is striking. If Apple RT v0.9.1 has no hardware-backed hit-count primitive and is falling back to a software path, that should be documented in the methodology section so future readers understand it is a known capability gap, not a measurement artifact.
- The segment_intersection_2d 12× slowdown is more consistent (CV≈14%) and is documented as expected given backend maturity. No action required.
