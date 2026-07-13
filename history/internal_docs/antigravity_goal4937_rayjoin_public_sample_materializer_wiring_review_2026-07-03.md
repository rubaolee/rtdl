# Goal4937 Critical External Review: RayJoin Public Sample Materializer Wiring

Date: 2026-07-03

## Verdict Label
**`approve_goal4937_byte_equal_but_not_faster_stop`**

***

## Executive Summary

This critical review evaluates the experimental app-layer integration of the generic grouped-output materializer (from Goal4936) into the RayJoin Section 5.7 public sample application path. The integration was tested on the County x Soil dataset public sample in two runs (`first_run` and `rerun1`).

The review confirms that:
1. The materializer-wired route successfully preserved byte-for-byte correctness against the author output, matching the answer file checksum exactly.
2. The materializer-wired route missed the performance gate on both trials, executing slower than the baseline plain writer.
3. The failure is due to a structural limitation: the materializer was inserted downstream of the custom application-layer chain-loop logic. As a result, it added a generic assembly pass (~1.037s in `rerun1`) rather than replacing the custom structure assembly phase.
4. The experimental app changes have been successfully reverted in the source tree to prevent retaining a slower code path.

Accordingly, the verdict is **`approve_goal4937_byte_equal_but_not_faster_stop`**. The performance gate was missed, no public speedup is authorized, and the source code must not retain these changes.

***

## Timings & Evidence Summary

The integration was evaluated using two POD execution runs on an NVIDIA RTX 4000 Ada Generation GPU, with the county/soil dataset:
* **Dataset Specs**: County segments: 326,193; Soil segments: 251,011; Group count: 64,459; Item rows: 673,371; Output size: 16,631,243 bytes (737,830 lines).
* **Correctness Validation**: Both routes produced identical outputs with SHA256 hash `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`, confirming correctness.

### Trial 1: [first_run/summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/first_run/summary.json) (Full Schema Validation Enabled)
* **Existing Plain Writer Route** ([first_run/section57_overlay.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/first_run/section57_overlay.json)):
  * Total Elapsed: `6.764782s`
  * Writer Phase (`output_chain_write_sec`): `2.049810s`
* **Generic Materializer Wiring Route** ([first_run/section57_overlay_numba_materializer.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/first_run/section57_overlay_numba_materializer.json)):
  * Total Elapsed: `8.294726s`
  * Writer Phase (`output_chain_write_sec`): `4.688221s` (with `generic_output_assembly_sec` at `2.633837s`)
  * Performance: **Missed gate** (writer is 2.29x slower; overall run is 1.23x slower).

### Trial 2: [rerun1/summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/rerun1/summary.json) (Redundant Group Descriptor Validation Disabled)
* **Existing Plain Writer Route** ([rerun1/section57_overlay.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/rerun1/section57_overlay.json)):
  * Total Elapsed: `6.121220s`
  * Writer Phase (`output_chain_write_sec`): `2.537364s`
* **Generic Materializer Wiring Route** ([rerun1/section57_overlay_numba_materializer.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/rerun1/section57_overlay_numba_materializer.json)):
  * Total Elapsed: `6.653871s`
  * Writer Phase (`output_chain_write_sec`): `3.067069s` (with `generic_output_assembly_sec` reduced to `1.037157s`)
  * Performance: **Missed gate** (writer is 1.21x slower; overall run is 1.09x slower).

### Writer Phase Breakdown (`rerun1` Materializer Route)
* `chain_loop_map0_sec`: `0.930846s`
* `chain_loop_map1_sec`: `0.791196s`
* `generic_output_assembly_sec`: `1.037157s`
* `bulk_writelines_sec`: `0.064876s`
* `skip_plan_sec`: `0.064433s`
* `group_xsects_map0_sec`: `0.006953s`
* `group_xsects_map1_sec`: `0.080330s`
* **Total Writer Phase**: `3.067069s`

***

## Detailed Answers to Review Questions

### 1. Does the evidence prove the materializer-wired route remained byte-for-byte correct on the RayJoin public sample?
Yes. The execution summary artifacts ([first_run/summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/first_run/summary.json) and [rerun1/summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/rerun1/summary.json)) as well as the overlay result files ([first_run/section57_overlay.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/first_run/section57_overlay.json) and [rerun1/section57_overlay_numba_materializer.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_pod_artifacts/rerun1/section57_overlay_numba_materializer.json)) confirm that both runs achieved `"byte_equal_to_author": true` and produced the correct answer file hash `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` on the Section 5.7 public sample.

### 2. Does the evidence prove the materializer-wired route missed the writer performance gate?
Yes. The performance gate required the materializer-wired writer to execute faster than the existing plain writer on the same execution run. The evidence clearly demonstrates this was not achieved:
* In `first_run`, the materializer writer phase (`4.688221s`) was slower than the baseline plain writer (`2.049810s`).
* In `rerun1`, even after disabling redundant descriptor validation in the adapter (reducing generic assembly from `2.633837s` to `1.037157s`), the materializer writer phase (`3.067069s`) was still slower than the baseline plain writer (`2.537364s`).

### 3. Is the interpretation correct that this failed because the materializer was inserted after the app chain-loop work, so it added a generic assembly pass instead of replacing structure assembly?
Yes, this interpretation is structurally and numerically correct. In the baseline plain writer path, the app processes custom chain loops to build the output structures. In the experimental path, the app still had to execute those same chain loop passes (measured in `rerun1` as `chain_loop_map0_sec` at `0.930846s` and `chain_loop_map1_sec` at `0.791196s`), but then also paid the additional overhead of formatting and running the [materialize_grouped_output_row_buffer](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L252) call (`generic_output_assembly_sec` at `1.037157s`). Because the materializer was added downstream of the existing custom structure assembly phase rather than replacing it, it introduced a new serialization/generic data structure conversion layer without saving any custom app-layer processing.

### 4. Is it correct that no RayJoin speedup claim is authorized from Goal4937?
Yes, it is correct. Since the experimental path was slower than the baseline on all trials, no RayJoin speedup claims are authorized.

### 5. Is it correct to revert the experimental app code and retain only the report/artifacts?
Yes, this is correct and represents proper repository governance. Edits to the experimental app runner [section57_overlay_numba.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py) were reverted, ensuring that only the completion report [goal4937_rayjoin_public_sample_materializer_wiring_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4937_rayjoin_public_sample_materializer_wiring_2026-07-03.md), the raw JSON execution logs, and this review document are retained.

### 6. Should the next Layer 3 attempt move the generic boundary earlier, so generic code owns grouping/descriptor/item structure directly instead of materializing after RayJoin-specific chain loops?
Yes. The next Layer 3 attempt must move the generic boundary upstream. Instead of passing fully structured chains to the writer and wrapping them afterwards, the inputs to the generic writer layer must be primitive row buffers or minimally structured row arrays. The generic RTDL module should directly own the grouping, descriptor building, and item materialization phases (using [GroupedOutputRowBufferSchema](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L65)), and the RayJoin app should only handle the final text-formatting/adapter wrapper. If the next iteration cannot bypass the custom application-layer chain-loop phase, it will suffer from the same structural performance regression.

***

## Non-Authorization Boundaries (Enforced)

The following boundaries must be strictly observed and enforced:
1. **No public speedup claims** are authorized from Goal4937.
2. **No retention of the slower RayJoin app path** in the default source tree is authorized.
3. **No RayJoin-specific output semantics** may be introduced into the RTDL core (folders `src/rtdsl/**` or `src/native/**`). RTDL core must remain generic.
4. **No further micro-patching** is authorized unless a new design fundamentally removes the app-layer chain-loop phase.
