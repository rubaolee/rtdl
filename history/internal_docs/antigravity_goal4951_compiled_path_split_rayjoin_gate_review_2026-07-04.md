# Goal4951 Compiled Path-Split RayJoin Gate Review

**Date**: 2026-07-04
**Verdict**: `approve_goal4951_correct_but_not_faster_stop`

## Executive Summary

We have reviewed the Goal4951 Compiled Path-Split RayJoin Gate C/D packet as requested in [call_for_review_goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md) and [goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md).

Our inspection confirms that:
1. The adapter in [goal4951_section57_compiled_path_split_adapter.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_section57_compiled_path_split_adapter.py) respects the boundary separation, leaving all app-level formatting and descriptors to the RayJoin app, while leaving only numeric path-split row materialization to the generic compiler core.
2. Correctness (Gate C) is fully proven, achieving exact byte-for-byte equality to the author's reference output across all plain and compiled runs, with matching SHA-256 hashes.
3. The performance comparison (Gate D) was conducted under fair conditions using a uniform POD environment, matching input datasets, and the same cached query sessions.
4. Gate D clearly fails the speedup threshold of `>= 1.10x`, exhibiting a regression of `0.622x` relative to the plain handwritten Python writer.
5. In accordance with the approved kill condition, the route is killed as default and will not be promoted.

Based on these findings, we approve the closure of Goal4951 under the verdict `approve_goal4951_correct_but_not_faster_stop`.

---

## Detailed Responses to Review Questions

### 1. Does the compiled adapter preserve the intended boundary: generic materializer owns only path-split rows, while RayJoin app owns descriptors and final text formatting?

**Yes.**
- The function [_build_path_split_inputs](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_section57_compiled_path_split_adapter.py#L74) acts as the boundary. It translates the application state into the neutral numeric arrays required by the generic materializer contract.
- The compiled core in [goal4951_compiled_path_split_spike.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_compiled_path_split_spike.py) owns only path-split row generation via [assemble_compiled_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_compiled_path_split_spike.py#L38). It does not have any visibility into final text layout, point numbering, or paper-specific polygon/descriptor formatting.
- The RayJoin app layer continues to own the unique point record deduplication cache (`point_records`), output chain ID sequencing, polygon ID generation (`create_polygon`), and final line writing.

### 2. Does the evidence support Gate C passing: byte-for-byte equality to the public answer on the plain, compiled first-run, and compiled rerun outputs?

**Yes.**
- The three generated files in the POD evidence directory:
  - [plain_section57_overlay.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_pod_artifacts/plain_section57_overlay.json)
  - [compiled_section57_overlay_first.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_first.json)
  - [compiled_section57_overlay_rerun.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_rerun.json)
- All report `"byte_equal_to_author": true` relative to the public answer key `br_countyXbr_soil_answer.txt`.
- All three runs produce an output with the exact same size (`16,631,243` bytes) and the exact same line count (`737,830` lines).
- All three runs produce the exact same SHA-256 checksum:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- Gate C correctness requirements are fully met.

### 3. Is the performance comparison fair enough for Gate D: same POD, same data, same cache, same answer, plain writer versus compiled route?

**Yes.**
- The runs were conducted on the same POD environment.
- They used the same input datasets (`br_county_clean_25_odyssey_final.txt` and `br_soil_ascii_odyssey_final.txt`).
- They utilized the same query cache database.
- They compared the exact same plain writer (`section57_overlay.py`) against the adapter route wrapping the compiled core, controlling for external platform differences.

### 4. Does Gate D clearly fail the approved threshold?

**Yes.**
- **Plain writer time**: `2.583328` seconds.
- **Compiled rerun writer time**: `4.155936` seconds.
- **Relative speed**: `2.583328 / 4.155936 = 0.622x`.
- **Required minimum**: `>= 1.10x`.
- Because `0.622x` represents a ~38% slowdown compared to the plain Python baseline, the compiled route fails Gate D by a large margin.

### 5. Should the compiled path-split route be killed as default and retained only as internal experimental evidence?

**Yes.**
- The approved kill condition explicitly dictates: *"If byte-equal but slower, the route is killed and not retained as default."*
- Consequently, this route is killed and will not be promoted or integrated into the default app path. It will remain in the codebase only as internal experimental historical documentation.

### 6. Does the packet avoid overclaiming that all Layer 3 work is impossible, while correctly rejecting this specific CPU/Numba materializer route?

**Yes.**
- The report explicitly notes that this result does not prove all Layer 3 optimization pathways are closed (such as native C++ or device-resident output buffering).
- It isolates the failure to this specific CPU-based Numba adapter implementation.

### 7. Is any further test required before closing Goal4951, or is the kill condition already satisfied?

**No further tests are required.**
- The kill condition has been fully satisfied and validated. Goal4951 is ready to be finalized.

---

## Non-Authorization Boundary Confirmation

We confirm that this approval authorizes **only** the closure of Goal4951 under the verdict `approve_goal4951_correct_but_not_faster_stop`. It does **not** authorize:
- Default route promotion of the compiled path-split adapter.
- Exposure of any new public APIs.
- Release of any performance acceleration claims.
- Future RayJoin performance work without a newly reviewed goal plan.
