# Goal1885 Claude Review: Goal1881 Measured Reusable Fixed-Radius Outputs

Date: 2026-05-13

Reviewer: Claude (claude-sonnet-4-6)

Reviewed commit: afd5cb9b (main)

Verdict: **accept-with-boundary**

---

## Scope

Goal1881 adds partner-owned reusable output columns for prepared fixed-radius v2.0 OptiX partner-device calls. The review covers the five questions in the handoff: architecture boundary, API safety, performance-claim scope, timing runner UX, and correctness of interpreted results.

---

## Q1: Architecture Boundary

**Pass.**

The native ABI is unchanged. `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns` still calls `prepared.write_device_count_threshold_columns(...)` with the same `generic_fixed_radius_count_threshold_2d_device_columns` contract. No new native symbol is introduced. The new `allocate_fixed_radius_count_threshold_2d_partner_device_output_columns` function is purely Python-side tensor allocation via the partner module. App semantics (coverage-gap inversion, hotspot threshold offset) remain in Python/PyTorch/CuPy exactly as before. The `v2_0_release_authorized: false` flag propagates correctly through all adapter metadata dictionaries.

---

## Q2: Reusable-Output API Safety

**Pass with one noted delegation.**

**Allocator** (`partner_adapters.py:772`): allocates `query_ids`, `neighbor_counts`, and `threshold_flags` as zero-filled uint32 tensors of the requested size. The `query_count < 0` guard rejects bad input before any partner call.

**Length guard** (`_require_fixed_radius_output_column_lengths`, line 789): checks key presence and length match for all three columns before the native call, using `_column_length` which handles both shape-based and len-based tensors correctly.

**Pass-through in prepared adapter** (`fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`, line 797): if `output_columns` is supplied it is validated; if None, the allocator is called. The `output_reuse_authorized` flag records which path was taken and is written to `metadata["output_columns_reused"]`.

**App adapters**: `service_coverage_gap_flags_optix_prepared_partner_device_columns` and `event_hotspot_flags_optix_prepared_partner_device_columns` accept `fixed_radius_output_columns: dict[str, object] | None = None` and forward to the core prepared adapter correctly.

**Delegation noted (not a defect):** The length guard does not validate dtype or device. Per the handoff, shape/device/dtype validation is delegated to the existing OptiX runtime direct-device handoff validation. This is the correct layering decision; adding redundant Python-side dtype checks would be premature.

**Empty-input path note:** The prepared adapter does not have an explicit `query_count == 0` shortcut (unlike the unprepared path). Empty inputs flow into the native call, which is acceptable for a prepared scene. If this ever becomes a performance concern it is easy to add, but it is not a correctness issue now.

---

## Q3: Performance Claim Scope

**Pass.**

The report status is `measured-with-boundary`. The pod JSON records `v2_0_release_authorized: false`, `whole_app_speedup_claim_authorized: false`, and `broad_rt_core_speedup_claim_authorized: false` in every result row. The report explicitly lists the authorization boundary (allowed vs. not allowed bullets) and the goal is described as a narrow overhead-reduction change for the repeated prepared fixed-radius subpath.

No broad RT-core, whole-app, or release-readiness language appears in the report, the adapter metadata, or the timing harness output.

---

## Q4: Timing Runner UX for Long Pod Runs

**Pass.**

The script prints `[goal1878] start case`, `[goal1878] timing ...`, and `[goal1878] done case` with `flush=True` at each timing step, giving continuous progress feedback for long runs. The `--max-reference-pairs` CLI argument is wired correctly: when `service_pairs` or `hotspot_pairs` exceeds the limit, `_skipped(reason)` is emitted instead of running the dense reference call. The skip reason records the exact pair count, which matches what appears in the pod JSON for size 16384.

---

## Q5: Measured Results

**Verified.**

Speedup numbers from the pod JSON cross-check against the report table at size 16384:

| Partner | App | v1.8 reused median | v2.0 reusable median | Computed speedup | Report |
|---|---|---:|---:|---:|---:|
| Torch | service | 0.036172 s | 0.000295 s | 122.6x | 122.8x |
| Torch | hotspot | 0.033576 s | 0.000221 s | 152.0x | 152.0x |
| CuPy | service | 0.033960 s | 0.000266 s | 127.7x | 127.7x |
| CuPy | hotspot | 0.033782 s | 0.000229 s | 147.5x | 147.4x |

All within rounding of the reported values. The dense-reference skip entries at size 16384 correctly record the pair counts (134,217,728 and 268,435,456) and appear in both the JSON and the report text.

**One unaddressed crossover (not a violation):** At sizes 256 and 1024, the dense partner reference path is modestly faster than `goal1879_v2_prepared_native_optix_partner` (e.g., size 256 Torch service: ref median 0.000268 s vs v2.0 0.000286 s). The report does not mention this crossover. This is not a claim violation—the report only makes explicit claims for size 4096 and 16384—but a future documentation pass should acknowledge the crossover point so that callers with very small query batches are not misled into expecting a speedup at all sizes.

---

## Naming Ambiguity (Informational)

The pod JSON key `goal1879_v2_prepared_native_optix_partner` labels the measured prepared-reusable path, but the implementation being measured at commit `afd5cb9b` includes the Goal1881 output-reuse improvement. The key name is unchanged from Goal1879 for JSON schema continuity. The report text makes this clear. No action required, but reviewers reading the JSON in isolation may not realize the measured timings reflect the Goal1881-improved path.

---

## Summary

| Check | Result |
|---|---|
| Native ABI unchanged | Pass |
| Generic contract preserved | Pass |
| App semantics remain in Python/partner | Pass |
| Allocator API safe | Pass |
| Length guard correct | Pass |
| Dtype/device validation delegated to runtime | Noted, acceptable |
| Claim boundaries enforced | Pass |
| Progress logging in runner | Pass |
| `--max-reference-pairs` works | Pass |
| Speedup numbers verified | Pass |
| Dense-reference skip entries correct | Pass |
| Small-size crossover not addressed | Minor documentation gap |

**Verdict: accept-with-boundary.**

This review authorizes the exact measured subpath: prepared fixed-radius v2.0 partner-device calls with reusable output buffers, at sizes 4096 and 16384 on RTX 3090 (pod commit `cf0c41a4`). It does not authorize v2.0 release readiness, whole-app speedup claims, or broad RT-core speedup wording.
