# Independent Review: Goal2802 RT-DBSCAN v2.5 Live Grouped-Stream Harness

Reviewer: Claude (external AI reviewer)
Date: 2026-05-31
Verdict: **accept-with-boundary**

---

## Blocking Issues

None. No blocking issues prevent acceptance.

---

## Review Question Findings

### 1. Real live harness vs. historical Goal2478 artifacts

The harness calls `run_project_close_matrix` imported from
`scripts.goal2478_rt_dbscan_project_close_pod_runner`. This is infrastructure
reuse, not artifact replay. The pod artifact confirms a fresh live run against
commit `afcea27599c4738cdee62b111e22c3111598efe8` with fresh timing values. The
`elapsed_sec` field (31.99 s) is consistent with a real multi-point-count
execution.

One honest disclosure: the `source_dirty` list in the artifact records
`?? scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py` — the
harness script was untracked (copied into the checkout) for the first pod run.
The report explicitly acknowledges this: "The Goal2802 script was copied into
that checkout for the first artifact run." Clean-from-Git re-run is correctly
deferred (see Q6).

**Finding: satisfied. The harness executes live against the current runtime.**

### 2. Three-way comparison clarity

The compact rows expose all three legs:

| Field group | Present |
| --- | --- |
| `prepared_cupy_grid_tail_median_sec` | yes |
| `rt_count_prepared_grid_tail_median_sec` + `rt_count_speedup_vs_prepared_cupy_grid` | yes |
| `grouped_stream_tail_median_sec` + `grouped_stream_native_tail_median_sec` + `grouped_stream_speedup_vs_prepared_cupy_grid` | yes |

The mode names `PREPARED_CUPY_GRID_MODE` and `PREPARED_GRID_MODE` are imported
from `goal2403_rt_dbscan_repeat_probe`, keeping constant names stable rather
than hardcoded strings. The report table presents all three legs legibly.

One nuance worth noting: at 32,768 points the planner selects
`optix_rt_core_adjacency_cupy_components_3d` (full adjacency fits budget), not
the grouped-stream mode. The grouped-stream timing is still measured and
reported for that point count, which is valid evidence. The table footnote
("full adjacency fits") reflects this correctly; no misleading wording.

**Finding: satisfied.**

### 3. Signature correctness and architectural contract fields

The JSON artifact records at the aggregate level:

```json
"signatures_match": true,
"grouped_stream_rt_core_accelerated": true,
"grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream": true
```

Per-row fields confirm:

```json
"grouped_stream_signature_match": true,
"grouped_stream_rt_core_accelerated": true,
"grouped_stream_materializes_neighbor_rows": false,
"grouped_stream_materializes_directed_adjacency_stream": false
```

These hold for all three point counts. The harness sets `status = "mismatch"`
whenever any of the three boolean invariants fail, making the pass/fail
criterion machine-enforced rather than asserted only in prose.

**Finding: satisfied. Signature and contract fields are present and
machine-checked.**

### 4. Claim boundary — excluded claims

The `CLAIM_BOUNDARY` dict in the harness code and the embedded JSON both record
every excluded claim as `false`:

| Excluded claim | Code | JSON |
| --- | --- | --- |
| `public_speedup_claim_authorized` | `False` | `false` |
| `whole_app_speedup_claim_authorized` | `False` | `false` |
| `paper_reproduction_claim_authorized` | `False` | `false` |
| `paper_speedup_claim_authorized` | `False` | `false` |
| `broad_dbscan_speedup_claim_authorized` | `False` | `false` |
| `pure_triton_components_claim_authorized` | `False` | `false` |
| `native_engine_customization` | `False` | `false` |

The report prose reinforces this: "This is not a paper-reproduction claim and
not a broad DBSCAN speedup claim." The boundary section is explicit and
complete. The test `test_pod_artifact_records_signature_match_and_claim_boundary`
checks `paper_speedup_claim_authorized: false` and `native_engine_customization:
false` by string search.

**Finding: satisfied. All excluded claims are explicitly recorded as false in
code, artifact, and prose.**

### 5. Manifest honesty about blocked pure Triton component auto-selection

The `rt_dbscan` manifest row in `v2_5_triton_app_migration.py` records:

```python
next_action=(
    "keep Goal2802 live harness current; keep pure Triton components "
    "auto-selection blocked until a generic component continuation beats the "
    "same-contract CuPy/grid/grouped-stream opponent"
)
```

The test `test_manifest_records_goal2802_rt_dbscan_status` asserts
`"auto-selection blocked"` is present in `next_action`. The
`V25TritonBenchmarkAppPlan.to_metadata()` method always emits
`"auto_select_preview_partner_allowed": False` — this is structural, not a
per-app override. The manifest validator enforces
`auto_select_preview_partner_allowed is not False` as a reject condition.

The `rt_dbscan` plan row lists `v2_5_status` as
`"app_chosen_cupy_phase_allowed_generic_fallback_partner_remains_numba"` which
correctly describes the current state: CuPy component phase is app-chosen, not
the generic partner path.

**Finding: satisfied. Blocked auto-selection is structurally enforced and
manifestly honest.**

### 6. Clean-from-Git validation status

The artifact's `source_dirty` includes the harness script as an untracked file,
confirming the first run was not clean from Git. The report states:
"Focused tests, external review, consensus, and clean-from-Git pod validation
are still pending at the time this report was first written."

The initial report verdict reads "accept-with-boundary pending external review
and clean-from-Git rerun." This is the correct framing.

**Finding: correctly identified as pending. No false clean-run claim is made.**

---

## Minor Observations (Non-Blocking)

**Consensus file not yet present.** The test
`test_report_and_consensus_keep_boundary` references
`docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_consensus_2026-05-31.md`.
That file is not in scope for Goal2802 itself, but the test will fail if run
before the consensus file is written. This is expected sequencing, not a defect
in Goal2802.

**Raw artifacts not retained.** `raw_artifacts_retained: false`. The
intermediate per-point raw files were discarded via `tempfile.mkdtemp`. For a
first evidence run this is acceptable; the compact artifact is sufficient for
the boundary checks. A clean-from-Git re-run should retain raw artifacts if
available.

**repeat_count = 3 drops one row.** The harness enforces `repeat_count >= 2`
so the first timing row can be dropped as warm-up. With `repeat_count = 3` the
tail median is over the second and third values. This is correct; the guard
prevents the warm-up timing from inflating the tail.

**cuda_nvcc is null.** The artifact records `"cuda_nvcc": null`. This is not a
claim defect but reduces reproducibility metadata. Not blocking.

---

## Summary

Goal2802 delivers a substantive live harness, not a wrapper around historical
artifacts. The three-way same-contract comparison is clear and machine-enforced.
The signature and architectural-contract fields are present and checked at both
row and aggregate level. Every excluded claim is encoded as `false` in code,
artifact, and prose. The manifest update is honest that pure Triton component
auto-selection remains blocked. The first pod run's not-clean-from-Git status is
correctly disclosed, and the report defers clean-from-Git validation as pending.

**Verdict: accept-with-boundary.**

Conditions for full acceptance:
1. A clean-from-Git pod re-run that matches or exceeds the grouped-stream
   speedup range (4.0x–4.9x) recorded here.
2. The consensus file referenced in the test should be written by the reviewing
   party before that test is run.
