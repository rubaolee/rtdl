---

# Review: Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence

**Packet date:** 2026-06-21  
**Reviewer:** External review (strict)  
**GPU:** NVIDIA RTX 4000 Ada Generation (single pod, single run)

---

## 1. Verdict

**Approve only with changes — and the changes are not cosmetic.**

The evidence is real. The speedups exist. The packet correctly refuses to make forbidden claims. But the floor number in the candidate wording (`1.116x` at 524,288 points) is derived from exactly **2 measured iterations** (repeat=3 minus warmup=1), and no variance is reported. Publishing a speedup floor to four significant figures from 2 data points is not defensible. The 65,536-point row (4 measured iterations) is adequately supported. The 262,144 and 524,288 rows are not, and they set the lower bound of the claimed range.

The packet may proceed to M7 **only for a narrowed or repaired claim**. See Section 2 for the required change.

---

## 2. Required Wording Boundary

### Current candidate wording (rejected as written)

> RTDL V3 includes a generic component-signature continuation route where prepared OptiX fixed-radius threshold columns feeding the same Numba component signature are **1.116x to 1.236x** faster than the same-contract Embree route on clustered3d rows from 65,536 to 524,288 points on an RTX 4000 Ada pod.

### Problems with the current wording

- **`1.116x`** is the 524,288-point floor. It comes from `median_elapsed_sec` of 2 measured iterations. This number must not be published.
- **`1.236x`** is the 65,536-point peak. It comes from 4 measured iterations. This number is defensible on its own.
- The wording omits that at 262,144 and 524,288 points the **Numba continuation phase dominates** total wall time. A reader will infer that RT cores are accelerating the whole pipeline. They are not. The threshold phase is faster; the continuation phase erases most of that.
- **"clustered3d"** is a zero-noise, four-equal-cluster synthetic dataset. The wording gives no indication of that geometry restriction.

### Option A — Narrow to the 65,536-point row only (approved if changes in §3 are met)

> RTDL V3 includes a generic component-signature continuation route where the prepared OptiX fixed-radius threshold path feeding the Numba component-signature step is **1.236x** faster than the same-contract Embree path at 65,536 points on a zero-noise four-cluster synthetic clustered3d dataset on an RTX 4000 Ada pod.

### Option B — Keep the range, but rerun first (approved only after rerun)

Rerun 262,144 and 524,288 at repeat=5 (warmup=1, measured_iterations=4). If results stay consistent, the following is approved:

> RTDL V3 includes a generic component-signature continuation route where prepared OptiX fixed-radius threshold columns feeding the same Numba component signature are **1.116x to 1.236x** faster (full-path, threshold phase; Numba continuation dominates at ≥262,144 points) than the same-contract Embree route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to 524,288 points on an RTX 4000 Ada pod.

The `continuation dominates` disclosure in Option B is not optional.

### What remains forbidden regardless of which option is chosen

These must not appear in any derived public documentation, directly or by implication:

- RTDBSCAN (the paper algorithm) is faster than any baseline.
- V3 is faster than V2.
- RTDL reproduces the RTDBSCAN paper.
- RT cores accelerate full DBSCAN end-to-end.
- The speedup applies to noisy datasets or non-equal-cluster geometries.
- The speedup applies beyond the component-signature route (e.g. full label-assignment routes).
- The speedup is generalizable to other GPUs or hardware.

---

## 3. Missing Evidence / Required Fixes Before Public Docs May Mention This Row

### P0 — Blocks M7 regardless of wording choice

**P0-A: Inadequate repeat count at 262,144 and 524,288 points.**  
Both large rows use `repeat=3, warmup=1`, giving `measured_iterations=2`. The `median_elapsed_sec` is the average of 2 values. There is no variance, no standard deviation, no confidence interval. The speedups at these sizes are 11.3% and 11.6% respectively — differences of 0.31 s and 0.95 s. These margins are plausible for system noise on a shared pod. The 262,144 OptiX prepare cost is 2.43 s vs 0.97 s for Embree; the pod is not stationary between runs.

**Fix:** Rerun both rows at `repeat=5` (or minimum `repeat=4`). If the speedups hold within ±0.5% across 4 measured iterations, the range claim is defensible. If the Option A single-row wording is chosen instead, no rerun is required for P0-A.

**P0-B: No reference validation on the three serious rows.**  
The 65,536, 262,144, and 524,288 rows are run with `--no-validation` (`validation_requested: false`, `matches_reference: null`). Correctness at these sizes is established only by comparing OptiX component signature to Embree component signature on the same pod run — not against any external reference. This is acceptable evidence that OptiX and Embree agree with each other but does not establish that either is correct. This is an inherent design limitation (reference at scale is expensive), but it must be disclosed in the wording or claim boundary documentation, not silently omitted.

**Fix:** Add to the packet boundary: "correctness at ≥65,536 points is verified by OptiX/Embree intra-run component-signature agreement, not against an independent CPU reference." The public wording must not imply reference-validated correctness at scale.

---

### P1 — Should be fixed; acceptable to document as a known gap if not fixed before M7

**P1-A: Single pod, single run.**  
One hardware instance, one execution date (2026-06-21). No reproducibility evidence from a second pod, second date, or second seed. A single-pod result on a shared-pod environment is structurally risky. This does not block Option A, but it limits the strength of the claim. The approved wording already pins "RTX 4000 Ada pod" which partially mitigates this, but a second independent run (different seed, same sizes) would materially strengthen the evidence.

**P1-B: Dataset geometry not disclosed in candidate wording.**  
All four runs use exactly 4 equal-size clusters with `noise_count: 0`. Real DBSCAN workloads have noise and irregular cluster sizes. The claim must include "zero-noise synthetic" to prevent readers from inferring applicability to noisier or more realistic data distributions. (Option A and Option B above both include this language; the current candidate wording does not.)

**P1-C: Continuation bottleneck omitted from candidate wording.**  
At 262,144 points: `optix_numba_component_continuation_sec` = 1.730 vs `optix_rt_count_threshold_sec` = 0.672. The RT-core-accelerated threshold phase is 38% of OptiX wall time. At 524,288: RT threshold = 1.236 s vs continuation = 6.904 s. The RT threshold is 15% of OptiX wall time. A reader seeing "1.116x faster" will not infer that 85% of wall time is Numba, not RT cores. This is misleading by omission even if technically accurate.

---

### P2 — Informational; does not block M7

**P2-A:** The 4,096 control row produces a 1.673x speedup. The packet correctly excludes it from the serious-row range. However, the summary JSON's `point_counts` array lists only `[65536, 262144, 524288]`, not 4,096. The pair table in the `.md` file includes 4,096. The exclusion is correct but the dual representation creates a consistency question that a future auditor will need to re-resolve. Documenting why 4,096 is excluded from the range (small-N validation control, not a serious row) would prevent future confusion.

**P2-B:** The `rt_threshold_speedup_vs_embree_compact_rows` column shows 1.27x and 1.54x speedups for the threshold-only phase at 262,144 and 524,288 respectively. These are legitimately stronger than the full-path numbers and might be worth citing as a separate, narrower sub-phase claim in a future packet — but they must not be used to justify the full-path speedup range in this packet.

---

## 4. Forbidden-Claim Audit

The packet passes on all four forbidden categories:

| Forbidden claim | Present in packet? | Assessment |
|---|---|---|
| RTDBSCAN paper is faster | No | All `paper_reproduction_claim_authorized: false` fields correctly set. No paper mention in candidate wording. Pass. |
| Full DBSCAN end-to-end | No | Route is explicitly restricted to component-signature path. Label publication is not claimed. Pass. |
| Broad V3 performance claim | No | Claim is row-scoped, route-scoped, dataset-scoped, and hardware-scoped. No "V3 is faster" language. Pass. |
| V2 comparison | No | No V2 mention anywhere in the packet. Pass. |

The internal self-critique in the "Goal-Level Decision Audit" section is accurate and does not overclaim.

---

## 5. Risk List

**P0**

1. **Thin repeat count at 262,144 and 524,288 (repeat=3, measured_iterations=2).** The floor claim of 1.116x is the weakest-supported number in the packet and is the number most likely to reverse on a rerun. Publishing it without variance disclosure or a rerun is a reproducibility failure waiting to surface.

2. **No reference validation at serious scales; not disclosed in candidate wording.** If a downstream reader treats the published result as reference-verified correctness, the claim's basis is weaker than implied.

**P1**

3. **Single-pod, single-run result.** If the pod has any background workload variation between the Embree and OptiX runs, the speedup number absorbs that noise. Two runs × two backends on a single busy pod = 4 total data points at the largest size. A second independent run would materially de-risk this.

4. **Continuation bottleneck at scale not in wording.** Omitting this from the published row is the single most misleading aspect of the current candidate wording. Any engineer reading "1.116x faster" will attribute that to RT cores. The RT cores contribute roughly 15% of wall time at 524,288 points.

5. **Zero-noise equal-cluster synthetic geometry not disclosed.** Claim applicability to real datasets is currently implied but unsupported.

**P2**

6. **Range breadth (65K–524K) is 3 data points, two of which have the thin-repeat problem.** Once the repeat problem is fixed, this risk drops substantially. Until then, the range is held up primarily by the 65,536 result.

7. **No stddev or variance in any row.** Timing evidence without spread is always riskier than it appears, especially on a shared pod with variable background load. This is a chronic gap in the evidence standard, not specific to this packet.

---

## Summary Ruling

The packet may not proceed to M7 as written. The 4,096-point validation control is clean. The 65,536 result (1.236x, 4 measured iterations, same-signature verified) is the only row in the packet that is adequately supported for a public numeric claim without a rerun. The 262,144 and 524,288 results are real but thin (2 measured iterations each), and the floor claim of 1.116x built on those results must not be published without either a rerun or a restriction to the 65,536 row.

**Choose one path:**

- **Option A:** Restrict the M7 claim to the 65,536-point row. Update wording to include zero-noise synthetic geometry and the route boundary. Approve immediately without a rerun.
- **Option B:** Rerun 262,144 and 524,288 at repeat=5. Disclose the continuation bottleneck in the wording. Approve the range claim after the rerun confirms consistency.

Either path, the forbidden-claim controls are in place and must remain in place. The `component_union` capability boundary is the ceiling; nothing above it is supported by this evidence.
