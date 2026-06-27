I have read all referenced evidence, source files, and the implementation. Here is my verdict.

---

## Review: V4 Point-Group Nearest-Witness Device-Output Candidate

**Verdict: `accept_with_required_amendments_before_catalog_decision`**

---

### What the evidence supports

The POD repeat gate at 32,768 and 131,072 query points passed with 7 repeats and 2 warmups on the RTX A5000. Parity is confirmed for `query_ids`, `neighbor_ids`, and `distances`. The native symbol `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns` is declared in `rtdl_optix_prelude.h:2257` and implemented in `rtdl_optix_api.cpp:7774`. The candidate is correctly isolated from the measured catalog throughout the stack:

- `v4_operator_catalog.py:47-54` lists it under the candidate block, `measured_partners: ()`, status `tier2_candidate_pod_repeat_gate_passed_external_review_required`
- `v4_point_group.py:35` sets `measured_partner: False` and `measured_partners: ()`
- `scripts/v4_catalog_regression_gate.py:126` requires `--include-candidates` to run this example at all
- `tier2_operator_catalog.md:22` places it under the Candidate Surfaces section

All critical claim-boundary flags are code-enforced:
- `release_claim_authorized: False`
- `broad_v4_speedup_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `tier3_callback_claim_authorized: False`
- `true_zero_copy_authorized: False`
- `rt_core_speedup_claim_authorized: False`

CuPy is blocked at runtime with `RuntimeError` in `v4_point_group.py:199` even though it is declared as a potential partner. The RTDL-owned prepared data boundary is correctly documented and code-enforced (no host upload in the hot path).

The candidate correctly does not appear in the measured catalog regression gate (`v4_catalog_regression_gate_dry_run_2026-06-24`), and the include-candidates gate confirms only three examples carry `measured` status.

---

### Required amendments before catalog promotion decision

**Amendment 1 — Resolve the sub-field `true_zero_copy_authorized: true` naming (blocking)**

The emitted metadata contains:

```json
"output_columns_true_zero_copy_authorized": true,
"query_point_columns_true_zero_copy_authorized": true,
```

at the same level as the authoritative boundary:

```json
"true_zero_copy_authorized": false,
```

The packet's non-authorization list explicitly blocks "true-zero-copy public wording", but the metadata emitted by `optix_runtime.py` contains sub-fields named `*_true_zero_copy_authorized: true`. This creates a real external-reader risk: anyone instrumenting the emitted JSON without reading the full packet will encounter a field named `output_columns_true_zero_copy_authorized: true` on a surface the packet says cannot make true-zero-copy claims. Before catalog promotion, either rename these sub-fields (e.g., `output_columns_direct_device_write_confirmed: true`) or add a documented guard that explicitly states these sub-fields are internal column-handoff tracking flags that do not grant any public claim. The sub-field names must not contradict the top-level boundary.

**Amendment 2 — Clarify `partner_support_declared_unmeasured` includes "torch" (required before promotion)**

`v4_point_group.py:37` sets `partner_support_declared_unmeasured: ("torch", "cupy")` even though all POD gate evidence ran on torch. The intent is correct — "torch has been POD-candidate-run but has not been promoted to a measured-release partner" — but the term `declared_unmeasured` applied to a partner that actually ran in the POD gate will confuse external reviewers. Before catalog promotion, add a separate field such as `pod_candidate_partners: ["torch"]` or equivalent that records which partners were actually exercised in the candidate gate, distinct from the release-promotion `measured_partners` list. This is especially important because the current naming erases the POD evidence from the claim boundary metadata.

**Amendment 3 — Expand the correctness fixture before promotion-quality gating**

All parity evidence uses a trivially perfect fixture: every query point `i` is at `(i*2.0, 0.0)`, every search point for group `i` is at `(i*2.0, 0.0)`, so every query matches its exact counterpart at distance 0.0 (`point_group_nearest_witness_torch_device_arrays.py:30-56`). This confirms the functional path but does not exercise:
- Queries with no matching neighbor within the radius
- Queries with nonzero distances
- The overflow path (`fail_closed_overflow` in `segmented_page_failure_mode`)

This amendment is not required before the catalog promotion *decision* can begin, but it is required before the promotion decision can close. A candidate gate that only exercises the distance=0.0 all-match case is not sufficient for a Tier-2 measured surface.

---

### Non-authorization (unchanged and binding regardless of verdict)

This review does not authorize and cannot be used to support:

- V4 release
- Adding `v4_point_group_nearest_witness_2d_device_arrays` to the measured V4.0 catalog (requires amendments above, plus an explicit catalog promotion decision)
- Broad V4 speedup wording
- Whole-application speedup wording
- RT-core POD performance wording
- True-zero-copy public wording (including any reference to the `output_columns_true_zero_copy_authorized: true` sub-field)
- CuPy performance claims
- Tier-3 callback or PTX support
- Embedding, C-ABI, or non-Python host claims
- App-specific native kernels (Hausdorff, collision, domain-specific geometry)

The candidate is well-constructed and the gate evidence is genuine. The two metadata naming issues (Amendments 1 and 2) are the only blocking items before the catalog promotion decision can proceed.
