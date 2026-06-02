# Gemini Review for Goal3012-Goal3013 Hausdorff Numba Score-Rows

**Date:** 2026-06-01

**Reviewer:** Gemini CLI

## Files Inspected:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_6_roadmap.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `docs/reports/goal3012_numba_pairwise_score_rows_for_hausdorff_2026-06-01.md`
- `docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.md`
- `docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json`
- `tests/goal3012_numba_pairwise_score_rows_for_hausdorff_test.py`
- `tests/goal3013_hausdorff_numba_device_score_rows_pod_runner_test.py`

## Questions and Answers:

### 1. Is `pairwise_l2_sq_score_rows_2d` generic enough for the RTDL partner layer, without adding Hausdorff/app semantics to the native engine?

Yes. The `pairwise_l2_sq_score_rows_2d` primitive calculates squared L2 distances between two sets of 2D points. Its descriptor `describe_numba_pairwise_l2_sq_score_rows_2d()` states `score_semantics: squared_l2_distance` and `replaces_rt_traversal: False`. The relevant source code in `src/rtdsl/numba_partner_continuation.py` does not contain any "Hausdorff" specific terms. The Goal3012 report explicitly notes, "It produces device-resident generic score rows" and that "The native engine is not app-customized." This confirms a generic operation without specific Hausdorff or application-level semantics.

### 2. Does the Hausdorff app compose generic score rows and generic grouped witness reduction correctly while preserving oracle parity?

Yes. The Hausdorff app, when using the `partner_numba_witness_exact` backend, correctly composes generic score rows and generic grouped witness reduction. It first uses `rt.pairwise_l2_sq_score_rows_2d_partner_columns` to generate device-resident score rows, which are then passed to `rt.group_argmin_then_global_argmax_partner_columns` for grouped witness reduction. Oracle parity is preserved, as evidenced by the `matches_oracle: true` flag in the `run_app` output and the Goal3013 JSON artifact for large-scale runs.

### 3. Does Goal3013 provide credible clean L4 evidence: clean commit, GPU/driver, warmup/evidence runs, 1024x1024 directed score-row scale, and all claim flags false?

Yes, Goal3013 provides credible L4 evidence. The JSON artifact (`docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json`) explicitly records:
- **Clean commit:** `commit: "69d4818ad33bf2208014b43dd22d4cbfbcf4c2c4"` and `source_dirty: []`.
- **GPU/driver:** `gpu: "NVIDIA L4, 565.57.01"`.
- **Warmup/evidence runs:** A `warmup` run (`copies: 16`) precedes the main `evidence` run (`copies: 256`).
- **1024x1024 directed score-row scale:** The `copies=256` results in `point_count_a: 1024` and `point_count_b: 1024`, corresponding to "1,048,576 score rows per directed pass" as stated in the Goal3013 report.
- **All claim flags false:** `all_claim_flags_false: true` is present, and the `claim_boundary` object confirms all relevant claims (e.g., release, speedup, zero-copy, etc.) are `false`.

### 4. Does any code/report/artifact overclaim v2.6 release readiness, speedup, RT-core acceleration, whole-app acceleration, true zero-copy, automatic partner selection, or app-specific native-engine logic?

No. Across all inspected code, reports, and artifacts, there are clear and consistent disclaimers preventing overclaiming.
- The `v2_6_roadmap.py` sets `V2_6_ROADMAP_STATUS = "v2_6_started_planning_not_release_authorization"` and explicitly lists many `_authorized` flags as `False`.
- The `rtdl_hausdorff_distance_app.py` includes a `claim_boundary` in its Numba witness exact mode with all relevant flags set to `False`.
- Both Goal3012 and Goal3013 markdown reports contain explicit "Claim Boundary" sections that state these claims are **not authorized**.
- The Goal3013 JSON artifact explicitly shows `all_claim_flags_false: true` and a detailed `claim_boundary` where all listed flags are `false`.
This comprehensive and consistent boundary setting prevents any overclaiming.

### 5. What should be fixed before this path becomes a recommended Hausdorff benchmark implementation?

The primary area for improvement before this path can be a recommended Hausdorff benchmark implementation is the grouped arg reducer's preview compaction. As stated in the Goal3012 report's "Boundary" section, "present-group compaction and NaN validation still use host synchronization."

Additionally, for true RT-core acceleration, the Goal3012 "Next Step" indicates that a "real native hit-stream producer feeding this same generic witness reducer" is required. Currently, the path is not RT-core accelerated, and the native engine remains app-agnostic and is not directly called by this exact dense path. Addressing these points would enhance the implementation's completeness and performance for a recommended benchmark.

## Verdict:

accept-with-boundary