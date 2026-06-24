I have read all required files. Here is the follow-up external review.

---

# V4.0 Release-Candidate Follow-Up External Review

**Date:** 2026-06-24  
**Reviewer:** Claude Sonnet 4.6  
**Branch:** `codex/v4-tier2-section8`  
**Runtime commit under review:** `c9586813b5769d9bff32d7974063b594c04a8997`

---

## Verdict

**`approve_amendments_closed_not_release_authorized`**

All five required amendments from the prior review are substantively closed. Two pre-existing release blockers explicitly identified in the prior review remain open and are not created by this amendment pass. This verdict does not authorize V4 release in any form.

---

## Per-Amendment Closure Status

### Amendment 1 — `v4_review_debt_open` enumerated and resolvable

**Status: CLOSED**

`future/v4/reviews/review_debt_v4_0_release_candidate_2026-06-24.md` exists and contains a complete D1–D8 tracker table with ID, status, and explicit close/waive condition per row. Each debt item is traceable to a file or condition. The waiver definition at the end of the file is non-implicit and correctly requires the release decision record to name the debt ID, state the reason, and preserve non-authorization boundaries.

One open debt item (D2: Antigravity non-interactive reviewer unavailable, status `tool_unavailable`) remains unwaived, but the tracker's own close condition identifies this correctly: "Waived only if the release decision record explicitly states…" This is a pre-existing gate, not a new gap introduced here.

---

### Amendment 2 — Clean-commit rerun protocol

**Status: CLOSED**

`future/v4/release_rerun_protocol_2026-06-24.md` exists with three discrete rerun paths:
- **Local no-CUDA gate**: precise `py -3 -m unittest` command, 15 modules, 55 tests expected OK.
- **Scope gate**: full command with `--json-out` and expected `passed`/`release_authorized: false` result.
- **POD GPU gate**: full worktree setup steps, serious-size command (`--copies 32768 --ray-count 32768`), and smoke-size command. Expected results are enumerated for all authorization flags.

The protocol is self-contained and sufficient for a clean-commit reproducibility path. The non-authorization footer is present.

The local test sweep (`v4_local_full_test_sweep_2026-06-24.md`) confirms the 15-module, 55-test, OK result was obtained against the amendment commit with the documented working-tree delta (evidence JSON files and candidate packet).

---

### Amendment 3 — Closest-hit grouped-argmin true-zero-copy boundary documented for users

**Status: CLOSED**

`future/v4/ray_triangle_device_array_frontdoor.md` contains explicit wording (lines 136–142):

> "Grouped argmin does not carry a public `true_zero_copy_authorized` claim in V4.0. It is still a measured device-array surface: inputs and grouped outputs stay in caller-owned Torch CUDA columns for the hot path, but the prepared grouped inputs and OptiX traversal use internal device-side staging that is disclosed in the evidence instead of hidden behind stronger zero-copy wording."

`future/v4/README.md` contains matching scope language. GPU evidence (`v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`) confirms the runtime reflects this correctly: `transfer_metadata.true_zero_copy_authorized: false` and `claim_boundary.true_zero_copy: false` in the closest-hit grouped-argmin payload.

---

### Amendment 4 — `partner="cupy"` no longer exposes a V4.0 `api_surface`

**Status: CLOSED**

`src/rtdsl/v4_operator_catalog.py` lines 129–145: when `partner` is in `declared_unmeasured_partners` (cupy appears in all three operator surfaces), the planner sets `measured = False`, `status = "tier2_declared_unmeasured_partner"`, and returns `api_surface=None` with guidance text "This operator is measured for Torch only. No V4.0 API surface is exposed for {partner}; treat this partner as V4.x deferred."

`tests/v4_operator_catalog_test.py` `test_cupy_tier2_partner_is_declared_but_unmeasured` verifies `assertIsNone(plan.api_surface)`, `assertIn("No V4.0 API surface", plan.guidance)`, and `assertFalse(plan.cupy_performance_claim_authorized)` — all passing in the local sweep.

The planner also validates `partner` is one of `{"torch", "cupy"}` (line 124) and raises `ValueError` otherwise, confirmed by `test_invalid_partner_is_rejected`.

---

### Amendment 5 — Catalog regression gate checks per-example forbidden claim flags

**Status: CLOSED — with one documented low-severity gap**

`scripts/v4_catalog_regression_gate.py` `_validate_payload` (lines 98–150) now checks `cupy_performance_claim_authorized`, `embedding_c_abi_claim_authorized`, `non_python_host_binding_claim_authorized`, and `app_specific_native_kernel_authorized` per-example payload, in addition to the pre-existing `release_claim_authorized`, `broad_v4_speedup_claim_authorized`, `tier3_callback_claim_authorized`, and `whole_app_speedup_claim_authorized` checks.

GPU evidence confirms all seven examples passed with zero failures, and the planner and quickstart payloads explicitly include these keys at the top level with `false` values.

**Low-severity gap (not a blocker for amendment closure):** The gate uses presence-conditional enforcement: `if "cupy_performance_claim_authorized" in payload and payload.get(...) is not False`. The three measured-operator examples (`fixed_radius`, `closest_hit_grouped_argmin`, `ray_triangle_any_hit_flags`) do not emit `cupy_performance_claim_authorized`, `embedding_c_abi_claim_authorized`, or `non_python_host_binding_claim_authorized` at the top level of their JSON payloads — they carry these fields only in `metadata`. This is consistent with the amendment's wording ("reject payloads that *emit* forbidden-claim flags"), but it means a future measured example that accidentally sets `cupy_performance_claim_authorized: true` inside only a nested `metadata` key would not be caught by the gate.

A complementary gap: `tests/v4_catalog_regression_gate_test.py` has no negative test verifying that a payload with `cupy_performance_claim_authorized: true` causes the gate to fail. The test suite validates the happy path only.

Neither gap invalidates the amendment closure, but both should be documented as V4.x improvements.

---

## Findings by Severity

### CRITICAL — None

No forbidden claims are present in the artifacts. All authorization flags in the GPU evidence, planner output, and gate results are `false` or `null` as expected. No release wording, CuPy performance claims, embedding/C-ABI claims, non-Python host binding claims, Tier-3 callback claims, broad speedup claims, or app-specific kernel claims are exposed by the amended artifacts.

### HIGH — Remaining Release Blockers (pre-existing, not new gaps)

These were explicitly listed as remaining blockers in the prior review record and carry into this follow-up:

1. **D2 not waived: Antigravity reviewer unavailable.** Debt tracker D2 is `tool_unavailable`. The debt tracker correctly gates waiver on a release decision record that explicitly names D2. No such record exists.

2. **Release decision record not obtained.** The candidate packet (`v4_0_release_candidate_packet_2026-06-24.md`, lines 100–103) and the recorded review record both list this as a blocking gap. No release can proceed without it regardless of amendment closure.

### LOW — Technical Gaps (not blocking amendment closure)

- **Gate enforcement is presence-conditional for three forbidden-claim flags** against the measured-operator examples. These examples currently make no such claims, so the absence is correct; however, the gate would silently pass a future measured-example payload that omits the key entirely even if it should carry it.

- **No negative test for forbidden-claim enforcement.** `tests/v4_catalog_regression_gate_test.py` does not include a test that injects a `cupy_performance_claim_authorized: true` payload and confirms gate failure.

- **GPU evidence tied to a specific POD commit** (`c9586813b`) with the candidate-packet and gate-JSON files as uncommitted working-tree additions at the time of the local sweep. The rerun protocol correctly documents this and the local sweep explicitly records the delta. The clean-commit rerun protocol (Amendment 2) addresses this gap going forward.

---

## Amendment Closure Summary

| # | Amendment | Status |
|---|-----------|--------|
| 1 | `v4_review_debt_open` enumerated and resolvable | **CLOSED** |
| 2 | Clean-commit rerun protocol exists | **CLOSED** |
| 3 | Grouped-argmin true-zero-copy boundary documented | **CLOSED** |
| 4 | `partner="cupy"` returns no V4.0 `api_surface` | **CLOSED** |
| 5 | Gate checks per-example forbidden-claim flags | **CLOSED** (with low-severity gap noted) |

---

## Non-Authorization Block

This review does not authorize V4 release, broad V4 speedup wording, whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX callback support, CuPy performance claims, embedding/C-ABI claims, non-Python host binding claims, or app-specific native engine kernels.

Release authorization remains `false`. The two remaining blockers (D2 waiver and release decision record) must be resolved by the user, not by a follow-up amendment pass.
