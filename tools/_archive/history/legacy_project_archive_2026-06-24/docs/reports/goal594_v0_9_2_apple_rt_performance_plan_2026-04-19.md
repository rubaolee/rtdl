# Goal594: v0.9.2 Apple RT Performance Plan

Date: 2026-04-19

Status: accepted by 3-AI planning consensus

## Purpose

v0.9.2 should make Apple Metal/MPS RT a credible developer-facing backend for
Apple machines. The goal is not to claim that Apple RT is broadly
performance-leading before evidence exists. The goal is to remove known
avoidable overheads, produce repeatable correctness/performance evidence, and
document the remaining honest boundary.

## Baseline Evidence

Current artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/apple_rt_vs_embree_perf_macos_2026-04-19.json
```

Local Apple M4 baseline:

| Workload | Embree median | Apple RT median | Apple RT vs Embree |
| --- | ---: | ---: | ---: |
| 3D `ray_triangle_closest_hit` | 0.000204 s | 0.001802 s | about 8.8x slower |
| 3D `ray_triangle_hit_count` | 0.000203 s | 0.338369 s | about 1664x slower |
| 2D `segment_intersection` | 0.010139 s | 0.095927 s | about 9.5x slower |

All three Apple RT paths matched the CPU reference in that bounded smoke.

## Root Cause Read

The current Apple RT backend is correct but structurally inefficient:

- `ray_triangle_closest_hit` builds one MPS triangle acceleration structure per
  call and dispatches one nearest-hit traversal.
- `ray_triangle_hit_count` loops over every triangle, builds a one-triangle
  acceleration structure, and dispatches MPS any-hit for all rays once per
  triangle.
- `segment_intersection` loops over every right segment, builds a one-quad
  acceleration structure, and dispatches MPS any-hit for all left segments once
  per right segment.

MPS supports `Nearest` and `Any` intersection modes. It can return primitive
index for nearest intersections, but MPS documents primitive index as undefined
for `Any`. That makes "all hits in one dispatch" unavailable through the simple
MPS intersector API.

## v0.9.2 Scope

Goal594 proposes v0.9.2 as an Apple RT performance stabilization release with
the following bounded targets:

1. Build a repeatable Apple macOS performance harness that reports correctness,
   cold-call time, repeated-call time, and backend comparison against Embree and
   CPU reference.
2. Add an optimized prepared path for 3D `ray_triangle_closest_hit`, so repeated
   ray batches can reuse the device, queue, intersector, triangle buffer, and
   acceleration structure.
3. Replace 3D `ray_triangle_hit_count`'s per-triangle acceleration-structure
   loop with a single-AS traversal strategy if correctness is proven. The first
   candidate is iterative nearest-hit traversal: find the nearest hit, advance
   that ray's minimum distance, count it, and repeat until no active rays remain
   or a bounded pass limit is reached.
4. Investigate `segment_intersection` performance separately. Preferred path is
   a nearest-hit plus primitive-index iterative MPS strategy if it can preserve
   RTDL all-pair output. If MPS cannot provide sufficient all-hit enumeration
   semantics, keep the current MPS RT path correct and document a future Apple
   Metal compute assist as a separate non-RT optimization path.
5. Update front-page/public docs only after measurements prove the final state.

## Non-Goals

- Do not claim Apple RT is "optimized" or "super fast" until repeatable measured
  results support that wording.
- Do not replace Embree as the mature baseline in documentation unless Apple RT
  wins broad measured comparisons.
- Do not silently move Apple work to CPU/Python fallback and call it Apple RT.
- Do not merge adaptive-engine WIP into this release.
- Do not add a full custom Apple data system or renderer.

## Candidate Implementation Goals

### Goal595: Apple RT Repeatable Perf Harness

Sequencing rule: Goal595 is a hard prerequisite for any performance benefit
claim in Goals596, 597, or 598. If later goals are deferred, Goal595 remains in
scope because it is the evidence foundation.

Deliver a script/report that runs on this Mac and records:

- Apple device name and Apple RT version.
- Embree version.
- CPU reference parity.
- cold-call median and repeated-call median.
- warmup policy and variance metrics such as min, median, max, and standard
  deviation.
- fixture sizes for closest-hit, hit-count, and segment-intersection.
- JSON artifact plus concise Markdown interpretation.

### Goal596: Prepared Closest-Hit Path

Deliver a native prepared-handle API for 3D triangles and a Python wrapper such
as `prepare_apple_rt_ray_triangle_closest_hit(triangles)`.

Expected benefit: reduce repeated-call overhead by avoiding repeated device,
queue, intersector, triangle-buffer, and AS setup.

Correctness gate: parity with existing Apple RT and CPU reference on bounded
closest-hit fixtures.

### Goal597: Optimized Hit-Count Path

Deliver a single-AS hit-count implementation if feasible:

- Build the triangle acceleration structure once.
- Use nearest-hit intersections with primitive index.
- Advance per-ray `minDistance` beyond the last accepted hit using a written
  deterministic epsilon policy before implementation starts.
- Track hit primitive IDs where needed to prevent double-counting.
- Count hits until no active hits remain or a documented ceiling is reached.
- Preserve current public result shape: one row per input ray.

Expected benefit: remove the current O(triangle_count) AS rebuild/dispatch
pattern.

Risk: repeated nearest-hit traversal must not double-count the same primitive or
miss co-located/very-near intersections. This requires strict parity tests.
Before implementation, Goal597 must record the epsilon policy and pass ceiling.
Parity fixtures must include dense-hit and near/co-planar geometry. If iterative
correctness cannot be proven within the release window, v0.9.2 ships with the
existing O(triangle_count) path and a documented deferral note rather than
blocking the release.

### Goal598: Segment-Intersection Performance Feasibility

Deliver either:

- an optimized MPS nearest-hit/primitive-index all-pair strategy with parity, or
- a written technical stop proving why the current MPS API cannot efficiently
  enumerate the all-pair segment-intersection result without a separate compute
  assist.

Expected benefit if feasible: reduce per-right-segment AS rebuilds.

Risk: MPS `Any` cannot supply a defined primitive index, and nearest-hit only
returns one primitive per pass. Dense all-pair cases may still require many
passes.
Before implementation, Goal598 must include a break-even analysis comparing
current per-right-segment AS rebuilds against iterative nearest-hit dispatches
over representative `(left_count, right_count, hit_density)` cases. If the math
does not close, Goal598 should stop with the written limitation report rather
than spending the release on a likely dead end.

### Goal599: Public Apple RT Documentation Refresh

Update public docs after code and measurements:

- README/front page backend summary.
- tutorial/backend docs.
- `docs/backend_maturity.md`.
- examples that show an easy Apple RT path without overclaiming.

### Goal600: v0.9.2 Pre-Release Gate

Run:

- full local tests,
- Apple RT focused correctness tests,
- Apple RT repeatable performance suite,
- public example smoke,
- doc/link/freshness audit,
- 2+ AI review consensus for each closure goal,
- 3-AI final consensus if public performance wording changes materially.

## Expected Release Wording If Successful

Acceptable wording if performance improves but does not beat Embree:

> v0.9.2 substantially reduces Apple Metal/MPS RT overhead for supported native
> slices and provides repeatable Apple-vs-Embree measurements. Apple RT remains
> bounded and workload-dependent.

Acceptable wording only if measurements support it:

> For selected repeated ray/triangle workloads on the tested Apple M4 host,
> prepared Apple RT is competitive with or faster than Embree.

Forbidden without evidence:

> Apple RT is generally super fast.

> Apple RT is the default optimized backend for all RTDL workloads.

## Codex Planning Verdict

ACCEPT as the v0.9.2 direction. The highest-value near-term work is prepared
closest-hit plus hit-count removal of per-triangle AS rebuilds. Segment
intersection should be investigated but must not block the version if MPS cannot
efficiently enumerate all hits with defined primitive identity.

## 3-AI Planning Consensus

Consensus status: ACCEPT.

- Codex: ACCEPT with evidence-first execution and no broad performance claim
  before measurement.
- Claude: ACCEPT with four conditions: Goal595 first, explicit Goal597 epsilon
  and pass-ceiling policy, Goal598 break-even analysis before implementation,
  and an explicit Goal597 fallback if parity cannot be proven.
- Gemini Flash: ACCEPT with emphasis on warmup/statistical harness discipline,
  double-count prevention for iterative nearest-hit, and timeboxed
  segment-intersection feasibility.

External review files:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal594_claude_review_2026-04-19.md
/Users/rl2025/rtdl_python_only/docs/reports/goal594_gemini_flash_review_2026-04-19.md
```
