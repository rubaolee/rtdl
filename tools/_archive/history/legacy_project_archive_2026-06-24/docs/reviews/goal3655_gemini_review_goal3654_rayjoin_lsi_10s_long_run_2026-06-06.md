# Independent Gemini Review for Goal3654 RayJoin LSI 10s Prepared-Left Long Run

**Date:** 2026-06-06

**Verdict:** `accept-with-boundary`

## Review Summary

This review assesses Goal3654, which aimed to harden the evidence for the 4096-row public county/soil LSI visible-count contract with a long, LSI-only run. The goal successfully introduced new runner improvements (`--workloads lsi` and `--rtdl-internal-query-repeat`) to achieve 10-second-class total timing measurements for both RayJoin and RTDL, moving beyond previous sub-second diagnostics. The artifact confirms count parity between RayJoin and RTDL, and the RTDL prepared-left route demonstrates a significantly lower per-query median timing for this specific contract. All specified claim boundaries (e.g., release readiness, public speedup claims) remain in place.

## Answers to Questions

### 1. Does the artifact genuinely show an LSI-only 4096-row same-slice run with matching visible count (`4977` RayJoin, `4977` RTDL)?

**Answer:** Yes, the artifact genuinely shows an LSI-only 4096-row same-slice run with matching visible counts. The primary report explicitly states that the "long-run packet therefore records: count parity: `4977` RayJoin visible LSI count and `4977` RTDL count." The `lsi_4096_10s_summary.json` artifact further corroborates this with `"selected_workloads": ["lsi"]`, `"rayjoin_visible_count": 4977`, and `"rtdl_count": 4977`, along with a `"count_contract_status": "matching_visible_lsi_count"`. The associated test also validates these specific values.

### 2. Does the runner's new `--workloads lsi` and `--rtdl-internal-query-repeat` telemetry support a 10-second-class RTDL hot-loop claim without forcing unrelated PIP work?

**Answer:** Yes, the new runner improvements effectively support a 10-second-class RTDL hot-loop claim without extraneous PIP work. The `--workloads lsi` flag ensures that only LSI tests are executed, preventing time expenditure on unrelated PIP rows. The `--rtdl-internal-query-repeat` feature allows the RTDL prepared-left native query to be repeated many times within a single session, enabling accurate measurement of "10-second-class hot-loop totals." The runner script explicitly enforces that `internal_query_repeat` is used only for LSI's `left_id_dense_count` route, confirming correct scoping. The artifact shows a median RTDL hot-loop total time of `10.31 s`, confirming the 10-second-class measurement.

### 3. Does RayJoin process wall timing (`~12.94 s` median) plus RTDL prepared-query total timing (`~10.31 s` median) make this stronger evidence than the short Goal3650 packet?

**Answer:** Yes, the significantly extended run times observed in Goal3654 (median `~12.94 s` for RayJoin process wall time and `~10.31 s` for RTDL prepared-query total timing) provide substantially stronger evidence compared to the short Goal3650 packet. The primary report explicitly states that Goal3654 "hardens that evidence with a long LSI-only run so the RayJoin and RTDL measurements are no longer sub-second diagnostics," highlighting that "10-second-class hot-loop totals rather than millisecond-only timing" constitute the "cleanest current RayJoin LSI evidence."

### 4. Is the per-query ratio (`0.284x`, about `3.52x` lower RTDL median) scoped correctly to the narrow visible LSI count contract?

**Answer:** Yes, the per-query ratio of `0.284x` (indicating RTDL is approximately `3.52x` faster) is correctly scoped to the narrow visible LSI count contract. The report specifies this ratio is for "this narrow visible-count contract," and the interpretation section notes it applies to "prepared-left reuse inside a native generic segment-pair count primitive." The implementation in `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` and `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` confirms that the `left_id_dense_count` route, designed for this specific type of scalar count, is used.

### 5. Are release, public speedup, broad RT-core, true zero-copy, whole-app, and full RayJoin reproduction claims still blocked?

**Answer:** Yes, all listed claims remain explicitly blocked. The "Boundary" section of the primary report clearly states, "This goal does not authorize: release readiness; public speedup wording; broad RT-core speedup wording; whole-app benchmark claims; true zero-copy claims; full RayJoin paper reproduction claims..." The `claim_boundary` field within the `lsi_4096_10s_summary.json` artifact also sets all corresponding flags to `false`, reinforcing these restrictions. The status in the artifact is "pass_with_optimization_gap", which indicates further work is needed.

### 6. What should the next performance target be after this: integrate this row into the broader v2.9 benchmark table, repeat on a second GPU, or move to the next weak app row?

**Answer:** Following the successful hardening of evidence for this specific LSI contract, the most logical and impactful next performance target would be to **integrate this row into the broader v2.9 benchmark table**. This action would effectively leverage the "cleanest current RayJoin LSI evidence" within a more comprehensive performance context. While repeating on a second GPU or addressing other "weak app rows" are valid subsequent steps, incorporating this validated data into the existing benchmark framework appears to be the most direct and valuable progression at this stage.
