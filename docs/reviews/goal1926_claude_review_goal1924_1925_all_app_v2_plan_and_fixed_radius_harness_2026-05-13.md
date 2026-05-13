# Goal1926 - Claude Independent Review: Goal1924/Goal1925 All-App v2 Plan and Fixed-Radius Harness

**Verdict: accept-with-boundary**

Reviewer: Claude (claude-sonnet-4-6), independent external review
Date: 2026-05-13
Distinct from Codex authoring: yes. This review was performed by a Claude instance
that did not author any of the reviewed artifacts. It is not a self-review.
Release decision: blocked. This review does not authorize v2.0 release.

---

## Scope

Reviewed files:

- `docs/reports/goal1924_all_app_v2_completion_and_perf_analysis_plan_2026-05-13.md`
- `tests/goal1924_all_app_v2_completion_and_perf_analysis_plan_test.py`
- `scripts/goal1925_fixed_radius_family_v2_partner_perf.py`
- `docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md`
- `tests/goal1925_fixed_radius_family_v2_partner_perf_test.py`
- `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`
- `scripts/goal1908_v2_local_preflight.py`
- `scripts/goal1911_v2_readiness_aggregator.py`

---

## Review Question 1: Does Goal1924 Correctly Identify Remaining All-App v2 Work?

**Finding: Yes, with one ambiguity.**

The plan correctly:

- Lists 16 active app rows and labels 4 as implemented-and-pod-timed, 1 as
  implemented-but-needs-rerun (`segment_polygon_anyhit_rows`), and 11 as missing.
- Acknowledges that current v2 pod evidence is "a strong slice, not a full all-app
  matrix." The `Status: execution-plan-not-complete` header and the explicit
  "No, all apps are not finished in v2.0 yet" conclusion are honest.
- Builds correctly on Goal1921 and Goal1923. Goal1921 established the fixed-radius
  positive result, mixed 512-row segment/polygon behavior, and positive 2048-row
  prepared-reuse result. Goal1923 closed the fresh Claude/Pro-class review blocker
  with `accept-with-boundary`. Goal1924 picks up from exactly that state without
  overclaiming it.
- The family decomposition (A through F) is logical. Grouping by reusable primitive
  rather than by app avoids duplicated implementation work and correctly identifies
  which families share the same underlying contract.

**Ambiguity: `segment_polygon_anyhit_rows` family status.**
Goal1924 classifies `segment_polygon_anyhit_rows` under Family B (Ray/Triangle
Any-Hit Flags) but its "current v2 state" is "implemented in earlier goals." The
report then defers the decision of whether this is a "final app row or a primitive
diagnostic row." This ambiguity should be resolved before the final all-app matrix
report, because if `segment_polygon_anyhit_rows` is reclassified as a diagnostic
row, the count of public comparison rows changes. This is a planning clarity issue,
not a correctness failure.

---

## Review Question 2: Does Goal1925 Cover Six Fixed-Radius Rows Without Overclaiming?

**Finding: Yes.**

The harness and report both carry explicit `False` claim boundary flags:

- `v2_0_release_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `broad_rt_core_speedup_claim_authorized: False`
- `package_install_claim_authorized: False`
- `fixed_radius_family_true_zero_copy_authorized: False`

The `goal1925` report explicitly states:

- "does not authorize a v2.0 release"
- "does not claim true zero-copy for this family"
- "does not claim whole-app speedup"
- Status is `harness-ready-pod-needed`, not a performance conclusion

The test suite (`goal1925_fixed_radius_family_v2_partner_perf_test.py`) verifies
all six app names appear in the script and verifies all three critical `False` claim
flags are present in the script source. The boundary enforcement is structural,
not commentary-only.

The description of what the harness does measure is precise: it measures the
shared fixed-radius prepared subpath under same-contract result normalization.
Whole-app claims are explicitly deferred to the final all-app report and external
review.

---

## Review Question 3: Is the v1.8 Prepared OptiX vs. v2 Prepared Partner Comparison Reasonable?

**Finding: Reasonable for five of the six apps. One scenario has a degenerate
dataset that should be fixed before the pod run.**

### Per-app assessment

| App | Comparison contract | Assessment |
| --- | --- | --- |
| `facility_knn_assignment` | coverage-threshold decision (not ranked KNN) | Reasonable. The boundary is explicit. Does not claim ranked KNN assignment. |
| `hausdorff_distance` | bidirectional threshold decision (not exact Hausdorff metric) | Reasonable contract, but see degenerate dataset issue below. |
| `ann_candidate_search` | candidate-coverage threshold decision (not FAISS/HNSW) | Reasonable. The report explicitly disclaims ANN index behavior. |
| `outlier_detection` | scalar outlier count at threshold=3 | Reasonable. `_summarize_counts` correctly classifies non-reaching points as outliers. |
| `dbscan_clustering` | scalar core count at threshold=3 | Reasonable. Core-point definition matches the DBSCAN threshold contract. |
| `barnes_hut_force_app` | node-coverage threshold decision (not force-vector evaluation) | Reasonable. Force-vector evaluation remains Python/app logic per Goal1924 Family A description. |

The bidirectional path for `hausdorff_distance` is correctly implemented: `_run_one_direction`
is called twice (query→search, search→query), and `result["status"]` is `"pass"` only
if both parity checks pass. This correctly models the directed-distance symmetry required
for a bidirectional threshold decision.

---

## Review Question 4: Are Claim Boundaries and Pod-Needed Status Clear Enough?

**Finding: Yes. The boundary enforcement is structural and machine-verifiable.**

Goal1911 (`goal1911_v2_readiness_aggregator.py`) always returns `status: "blocked"` via
a hardcoded three-item permanent blocker list (final source-tree/packaging decision,
final release consensus, explicit user-requested release action). These are appended
unconditionally and cannot be cleared by artifact presence alone. This is the correct
design for a release gate that requires human action.

Goal1908 (`goal1908_v2_local_preflight.py`) correctly includes both `goal1924` and
`goal1925` test modules in `TEST_MODULES` and carries its own `v2_0_release_authorized: False`
claim boundary in its output JSON.

Goal1899 correctly records Goal1924 and Goal1925 in its "Newly Added Since The Last Board"
section and updates the "Immediate Next Hardware Step" to reference the Goal1925 pod command.
The board verdict remains "v2.0 is still not born."

---

## Review Question 5: Correctness and Performance-Analysis Traps Before the RTX Pod Run

### TRAP 1 (fix before pod run): Degenerate hausdorff_distance scenario

**Severity: medium.**

The `hausdorff_distance` scenario in `SCENARIOS` uses:

```
query_count=4096, search_count=4096,
query_spacing=2.0, search_spacing=2.0
```

Both sets are generated by `_points` with `y_offset=0.0` (the default). This produces
two identical point sets: both on the y=0 line at positions 0.0, 2.0, 4.0, .... With
`radius=0.01`, every query point at position `2k` finds exactly one search point at the
same position `2k` at distance 0. The threshold is `1`, so all 4096 query points trivially
reach threshold in both directions. The parity check passes vacuously.

This means the hausdorff test:
- Does not exercise threshold-failure paths (all points succeed).
- Does not test sparse cross-set coverage scenarios where the bidirectional decision is
  non-trivial.
- Will produce a timing measurement dominated by prepared-scene overhead with essentially
  no per-point RT work variation.

**Recommended fix before pod run**: Offset the search set by a `y_offset` (e.g., 1.0) or
use different spacings so the two sets are genuinely distinct and only a subset of queries
reach threshold. For example:

```python
"hausdorff_distance": FixedRadiusScenario(
    ...
    query_spacing=2.0,
    search_spacing=2.0,
    radius=1.5,  # enough to catch nearby but not all
    ...
),
```

And generate search points with a non-zero y_offset:

```python
search_points = _points(scenario.search_count, spacing=scenario.search_spacing, y_offset=1.0)
```

Alternatively, use different spacings so point positions don't coincide.

### TRAP 2 (low severity, acceptable): No warmup exclusion in timing loop

The `_time` function runs `repeat=5` iterations without excluding a warmup iteration.
The first iteration typically includes CUDA/OptiX JIT compilation overhead and driver
context startup. This inflates `min_s` (not `median_s`). Since the ratio uses `median_s`,
the performance conclusion is insulated from this effect. However, the `min_s` field
in the output JSON should not be cited as a best-case timing unless warmup is excluded.

**Recommended**: Document in the report that `median_s` is the cited statistic, and that
`min_s` may include first-iteration JIT overhead. No code change strictly required.

### TRAP 3 (low severity, intentional): v2 timing excludes host materialization

The v1.8 baseline (`prepared_v1.run(...)`) returns host-side rows already materialized.
The v2 path is timed with a `partner` sync barrier but `_to_host_uint32` is called
_outside_ the timing window. This correctly measures the GPU sub-path comparison, but
means the reported v2 time does not include the cost of host materialization if the
calling app requires it.

This is intentional design: the claim is that partner-owned device output avoids host
materialization for chained GPU operations. This is correct within the stated boundary.
It becomes a trap only if someone cites the v2 timing as a whole-app latency. The
`whole_app_speedup_claim_authorized: False` flag guards against this.

### TRAP 4 (low severity, trivial): `_git_commit()` called twice in payload

```python
"git_commit": _git_commit(),
"source_commit_label": _git_commit(),
```

Two separate subprocess calls to `git rev-parse HEAD`. Theoretically they could diverge
if a commit occurs between calls. In practice this is not a real risk during a pod run.
Cosmetically the duplication is unnecessary; assign once and reuse.

### TRAP 5 (low severity): `barnes_hut_force_app` has very sparse query-to-search overlap

With `query_spacing=4.0`, `search_spacing=16.0`, `radius=1.1`, the search points are at
0, 16, 32, ... and query points at 0, 4, 8, 12, 16, .... Only query points within 1.1
units of a search point will reach threshold. Query point at index 0 (position 0.0) is
at distance 0 from search point at 0; query point at index 4 (position 16.0) is at
distance 0 from search point at 1 (position 16.0), etc. Only about 1 in 4 query points
has a near neighbor. `threshold_reached_count` will be small, meaning the summary
contrast is dominated by the not-reached majority. This is actually a valid sparse
scenario, not a defect. Note it in the analysis so the low `threshold_reached_count`
ratio is not misread as a parity failure.

---

## Goal1908 and Goal1911 Assessment

Both scripts are correct. Goal1908 now includes the two new test modules
(`goal1924_all_app_v2_completion_and_perf_analysis_plan_test`,
`goal1925_fixed_radius_family_v2_partner_perf_test`) and keeps all prior modules.
Goal1911 includes `goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md` in
`SUPPORTING_REQUIRED`. The readiness aggregator hardcodes three permanent blockers
that require human action, which is the correct design.

---

## Summary

| Question | Finding |
| --- | --- |
| Goal1924 correctly identifies remaining all-app v2 work | Yes. One planning ambiguity: `segment_polygon_anyhit_rows` family/diagnostic row decision deferred. |
| Goal1925 covers six rows without overclaiming whole-app or true zero-copy | Yes. Structural `False` claim flags enforced in code and tested. |
| Same-contract comparison is reasonable for all six apps | Yes for five. `hausdorff_distance` scenario is degenerate (identical point sets). Fix before pod run. |
| Claim boundaries and pod-needed status are clear enough | Yes. Machine-verifiable. Goal1911 permanently blocks release without human action. |
| Traps to fix before RTX pod run | One fix needed: `hausdorff_distance` scenario must use non-identical query and search sets. Three lower-severity notes documented above. |

---

## Verdict

**accept-with-boundary**

The Goal1924 plan and the Goal1925 harness are structurally sound. The claim boundaries
are explicit, enforced in code, and verified by tests. The analysis rules in Goal1924
(classify rows, not just tabulate ratios) are the right design for the final all-app
report.

The one required fix before the RTX pod run is the `hausdorff_distance` scenario:
the current identical-point-set dataset tests overhead but not the bidirectional
threshold decision under realistic cross-set geometry. All other traps are low
severity or intentional.

The release decision remains blocked. This review does not grant authorization for
v2.0 release, whole-app speedup claims, true zero-copy claims, or package-install
claims. Pod timing artifacts are still required.
