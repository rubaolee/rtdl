# Goal2031 External Review: Goal2030 Large-Scale v2.0 Dev Pod Findings

Reviewer: external (Gemini role)
Date: 2026-05-14
Verdict: **accept**

---

## Scope

Read-only review of:

- `docs/reports/goal2030_large_scale_v2_dev_pod_findings_2026-05-14.md`
- `docs/reports/goal2030_large_scale_v2_dev_pod_findings_2026-05-14.json`
- `docs/reports/goal2028_large_scale_dev_pod_sweep_936aff2f/` (35 files)
- `docs/reports/goal2029_targeted_large_dev_pod_sweep_936aff2f/` (20 files)
- `tests/goal2030_large_scale_v2_dev_pod_findings_test.py`

All numbers below were checked against the raw JSON artifacts and pod logs.
No source files were edited.

---

## Q1: Does Goal2030 accurately summarize the large-scale pod data?

**Yes.** Every number in the summary table cross-checks exactly against its
source artifact.

| Row | Reported medians | Artifact medians | Match |
|---|---|---|---|
| database 200k v1.8 | 14.213700 s | 14.21370005607605 s | pass |
| database 200k v2 | 2.870273 s | 2.8702725525945425 s | pass |
| database 500k v1.8 | 35.113168 s | 35.113168492913246 s | pass |
| database 500k v2 | 6.963365 s | 6.963365303352475 s | pass |
| polygon 10k pair v1.8 | 1.465724 s | 1.4657240863889456 s | pass |
| polygon 10k pair v2 | 0.337216 s | 0.33721559680998325 s | pass |
| polygon 10k jaccard v1.8 | 1.031353 s | 1.0313529670238495 s | pass |
| polygon 10k jaccard v2 | 0.234297 s | 0.2342971097677946 s | pass |
| polygon 12k pair v1.8 | 1.727046 s | 1.7270457483828068 s | pass |
| polygon 12k pair v2 | 0.342935 s | 0.3429349958896637 s | pass |
| polygon 12k jaccard v1.8 | 1.167387 s | 1.1673869173973799 s | pass |
| polygon 12k jaccard v2 | 0.253313 s | 0.2533129286020994 s | pass |
| segment 1M 3x v1.8 | 6.131052 s | 6.131051514297724 s | pass |
| segment 1M 3x v2 | 22.422607 s | 22.42260717600584 s | pass |
| segment 1M 4x v1.8 | 6.043373 s | 6.043373012915254 s | pass |
| segment 1M 4x v2 | 22.664319 s | 22.664319340139627 s | pass |
| robot 4M v1.8 | 0.303589 s | 0.30358915589749813 s | pass |
| robot 4M v2 | 0.005306 s | 0.005306189879775047 s | pass |
| robot 16M v1.8 | 1.289325 s | 1.2893250565975904 s | pass |
| robot 16M v2 | 0.019840 s | 0.019839569926261902 s | pass |
| road 8192 v1.8 | 0.017377 s | 0.01737692952156067 s | pass |
| road 8192 v2 | 0.003426 s | 0.003426436334848404 s | pass |
| road 16384 v1.8 | 0.041209 s | 0.04120857082307339 s | pass |
| road 16384 v2 | 0.005530 s | 0.0055295731872320175 s | pass |
| graph 100k v2-only | 0.000206 s | 0.0002064276486635208 s | pass |
| graph 1M v2-only | 0.000123 s | 0.00012318231165409088 s | pass |

The polygon 16k OOM is confirmed by the traceback in
`polygon_extent_16384.log`:
`cupy.cuda.memory.OutOfMemoryError: Out of memory allocating 6,442,450,944
bytes (allocated so far: 19,328,991,232 bytes)`.

The graph 5k timeout is confirmed by exit code 143 in
`graph_control_5000.status` (SIGTERM, process killed by timeout wrapper).

The fixed-radius PTX failure is confirmed verbatim in
`fixed_radius_default_probe.log`:
`CUDA driver error: the provided PTX was compiled with an unsupported
toolchain`.

The segment 2x overflow is confirmed by `segment_capacity_1m_x2.log`: v1.8
ran 3 iterations cleanly (producing the reported median 6.315167 s) and then
v2 raised `RuntimeError: partner segment/polygon column adapter overflowed`.

No discrepancies were found between the report and the raw data.

---

## Q2: Are the positive findings correctly bounded?

**Yes.** Each positive area is bounded to its tested range and mechanism:

- **Database** (200k–500k copies): ratio 0.198–0.202x confirmed at both sizes;
  claim is correctly scoped to columnar partner continuation.
- **Polygon** (10k–12k copies): both pair-overlap and Jaccard rows pass with
  exact oracle match; the upper bound is correctly stated as 12k (16k is OOM).
- **Robot** (4M–16M poses): zero-copy pose-flag parity confirmed
  (`colliding_pose_count_match: true`, `pose_collision_flags_match: true`) at
  both sizes; ratio improves with scale (0.017x to 0.015x).
- **Road hazard** (8192–16384 roads, prepared-only path): strict priority-flag
  match confirmed (`strict_priority_flags_match: true`); warmup spike is
  visible in artifact max_s (road 8192 v2 max=0.198 s vs median=0.003 s) and
  correctly flagged in Section 6.
- **Graph** (100k–1M, v2-only): the artifact JSON correctly records
  `all_match_v1_8_python_rtdl_oracle: false` and `v1_8_payload_signature:
  null` for both runs because no oracle comparison was run; the report
  correctly labels these "v2-only pass" with no cross-version ratio claimed.

The report does not extrapolate any positive finding beyond its tested range.

---

## Q3: Are the negative findings honestly preserved?

**Yes.**

- **Polygon 16k OOM**: documented in Section 2 with root-cause diagnosis (dense
  all-pairs CuPy extent intermediate requiring 6 GiB in a single allocation on
  a 24 GiB card that had 19 GiB already allocated). Correctly bounds the
  polygon claim to 8k–12k in release notes.
- **Graph 5k v1 timeout**: documented in Section 3 and attributed to the v1.8
  oracle bottleneck rather than any v2 failure. The fix recommendation (separate
  correctness/ratio/scale-probe benchmark modes) follows from the diagnosis.
- **Segment 1M materialized rows**: the 3x capacity JSON shows ratio 3.657x and
  the 4x JSON shows 3.750x; the report correctly notes that adding capacity does
  not fix the row-materialization cost. The `overflow_check: skipped` field in
  both artifacts is consistent with capacity being deliberately oversized.
- **Fixed-radius CUDA 13 PTX failure**: correctly characterized as a pod
  toolchain compatibility blocker (not a performance regression) and scoped to
  this pod's driver/NVRTC combination.

No negative finding is softened, omitted, or hidden behind aggregate language.

---

## Q4: Are the next engineering targets reasonable and app-agnostic?

**Yes.** The five targets are:

1. Tiled/chunked extent candidate discovery — addresses the dense all-pairs OOM
   root cause without any app-specific native hook.
2. Compact segment output contract — moves the aggregation choice to the Python
   app layer rather than fixing it in the native adapter.
3. Separate benchmark modes — addresses the oracle-timing bottleneck problem
   surfaced by the graph 5k run.
4. Warmup/allocation phase reporting — separates first-run outliers (visible in
   road hazard and robot max_s values) from steady-state medians.
5. Fix/quarantine CUDA 13 PTX mismatch — scoped to toolchain repair, not
   application changes.

All five targets are framed as design or infrastructure improvements. None
assumes a specific application or requires exposing new app-specific hooks.

---

## Q5: Does the report avoid overclaiming?

**Yes.** The claim boundary section is explicit and the JSON machine-checkable
block confirms it:

```json
"claim_boundary": {
  "v2_0_release_authorized": false,
  "whole_app_speedup_claim_authorized": false,
  "broad_rt_core_speedup_claim_authorized": false,
  "package_install_claim_authorized": false,
  "unbounded_polygon_graph_or_segment_claim_authorized": false
}
```

The JSON `status` field is `"development-evidence-not-release-authorization"`,
matching the report's opening caveat (`Status: development evidence, not
release authorization`).

The database speedup claim in Section 1 ("about 5.0x faster than v1.8") is
conservative: the actual 500k ratio is 0.1983x, which is 5.04x; rounding down
to 5.0x is appropriate. No RT-core attribution, whole-app claim, or unbounded
scale claim appears anywhere in the report.

---

## Minor Observations (non-blocking)

1. **Road hazard warmup spike not visible in the table**: the summary table
   shows medians only. At 8192 roads the v2 first-run max is 0.198 s vs a
   median of 0.003 s, a 58x outlier. Section 6 calls this out in prose, but
   adding a `first_run_max_s` column to the table in a future revision would
   make it harder to miss.

2. **Segment 2x row records v1.8 baseline without a v2 data point**: the 2x
   row correctly shows v1.8 median (6.315167 s) and marks v2 as n/a/overflow.
   A note clarifying that v1.8 ran to completion before v2 overflowed would
   remove any ambiguity about why a v1.8 time appears for a failed row.

3. **Graph v2-only oracle status sentinel**: `all_match_v1_8_python_rtdl_oracle:
   false` in the v2-only graph artifacts is technically correct (no oracle was
   run) but could be misread as a correctness failure. Changing this sentinel to
   `null` or `"not_applicable"` for v2-only runs would remove the ambiguity;
   the current value does not affect the report's accuracy.

---

## Test Coverage

`tests/goal2030_large_scale_v2_dev_pod_findings_test.py` covers:

- Key win markers present in the markdown report text
- Key design-debt section headings present in the markdown report text
- JSON `status` string, quantitative bounds on the four main ratios, polygon
  OOM status, and all five `claim_boundary` flags
- Existence of all eight required artifact files from goal2028 and goal2029

Coverage is adequate for a development evidence report. The numeric thresholds
(`< 0.21` for database 500k, `< 0.02` for robot 16M, `< 0.15` for road 16384,
`> 1.0` for segment 3x ratio) are correctly tighter than the actual observed
values, making the assertions meaningful rather than vacuous.

---

## Verdict

**accept**

The report is an accurate, honest, and well-bounded development evidence
document. All numbers match their source artifacts exactly. Negative findings
are fully preserved and correctly attributed. Positive findings are bounded to
their tested ranges and mechanisms. The claim boundary is explicit and
machine-checkable. The engineering targets are reasonable and app-agnostic. No
release authorization is claimed or implied.
