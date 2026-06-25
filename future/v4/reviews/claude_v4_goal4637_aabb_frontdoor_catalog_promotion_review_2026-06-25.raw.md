I now have sufficient material to render the review. Here is my verdict:

---

## Critical Review: V4 Goal4637 AABB Front-Door Catalog Promotion

**Verdict: `approve_goal4637_aabb_frontdoor_catalog_promotion`**

With notable observations that do not block approval but must remain visible in review debt.

---

### Q1 — Is the surface legitimate and generic, or does it leak LibRTS identity?

The API surface (`v4_aabb_index_query_2d_all_ops_count_prepared_runner`) is generically named, and the primitive constant `AABB_INDEX_QUERY_2D` has no app-identity in it. The planner correctly lists `librts_spatial_index` in `V4_APP_IDENTITY_KERNEL_NAMES` (catalog line 222), ensuring any direct planner request using that name is **rejected**, not routed.

**One provenance flag**: The evidence artifact `m30_all_ops.json` carries two V3-origin fields:
```json
"goal": "Goal4427 V3.0 M30 LibRTS prepared AABB all-ops refresh",
"version": "rtdl.v3_0.librts_prepared_all_ops_refresh.m30"
```
These are in the raw evidence file only, not in the front-door code or claim boundary. The non-authorization chain is correctly enforced in code and docs. This is a provenance observation, not a blocking issue.

**Conclusion**: The surface does not leak app identity into the API. Pass.

---

### Q2 — Is `rtdl_native` the correct partner scope label?

Yes. The M30 gate used RTDL's own native prepared-runner infrastructure — no Torch tensor, no CuPy array, no Numba kernel on the user side. The catalog entry correctly sets `direct_device_input_columns: False` and `direct_device_output_columns: False`, which accurately describes the Python-iterable-in, count-scalar-out contract.

**Weaker-front-door observation**: Unlike the six Torch CUDA surfaces, this AABB surface does not exercise V4's stated device-array interop proposition ("accept caller-owned Torch CUDA arrays…"). This is not a new problem — Goal4635 also accepted a Numba-scoped non-device-array path — and `rtdl_native_prepared_runner` is already included in `V4_0_INCLUDED_CAPABILITIES` in `v4_scope.py` line 25. The README correctly discloses: "The AABB surface is measured in RTDL's native prepared-runner path, not Torch, CuPy, or Numba." The `V4_FRONT_DOOR_MEASURED_PARTNER` string in `v4.py` line 51 is already updated to `"mixed_torch_numba_and_rtdl_native"`.

This is pre-authorized scope, not overclaim. But the review record should note that AABB does not demonstrate device-array interop, which weakens its contribution to V4's primary value proposition compared to the Torch surfaces.

**Conclusion**: `rtdl_native` is correct and adequately disclosed. Pass.

---

### Q3 — Is the catalog promotion justified by the 264.822x / 115.007x ratios?

The numbers comfortably exceed the 10x floor. The fixture is serious (1M boxes × 1K queries, 240 repeats each). Count parity holds across backends. The contract distinction is worth naming explicitly:

- The comparison is `same_contract_family`, not strict `same_contract`: Embree uses `generic_prepared_aabb_index_query_2d_count`; OptiX uses `generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count`. The OptiX path benefits from prepared query handles in the setup phase, not only RT-core acceleration.

However, the evidence JSON shows `query_prepare_sec: {"prepared_query_handles_in_runner_prepare_phase": 0.0}` for OptiX — the prepare-phase handle cost is not loaded into the query timing. The hot-path query timing comparison is therefore defensible. The catalog entry uses `comparison_class: "same_contract_family_embree_control"` (not `same_contract`), which is honest.

**Conclusion**: Promotion is justified. Pass.

---

### Q4 — Is the `librts_spatial_index` coverage promotion to `strong_measured` justified without whole-app or paper claims?

The `V4BenchmarkCoverageRow` dataclass enforces all six non-authorization flags as hard errors in `__post_init__`. The `release_gap` field reads:
> "This is not a LibRTS paper reproduction, authors-code comparison, or whole-app speedup claim."

The `validate_v4_goal4627_coverage_audit` function hardcodes the 10-app list and passes with 4 strong / 4 partial / 0 candidate / 2 deferred. Coverage summary's `latest_refresh_goal` is correctly set to `"Goal4637_after_aabb_index_frontdoor_catalog"`.

The conceptual tension — `librts_spatial_index` appears in both `V4_APP_IDENTITY_KERNEL_NAMES` (rejects planner requests) and as a coverage audit row (maps the operator class) — is not a contradiction. These are two different registries with two different purposes.

**Conclusion**: The promotion is justified and the non-authorization language is complete. Pass.

---

### Q5 — Are the claim boundaries complete and sufficiently conservative?

The claim boundary in `v4_aabb_index.py` carries all ten required False flags. The `validate_v4_goal4637_aabb_frontdoor_catalog_decision` function in `v4_goal4637_aabb_frontdoor_catalog_decision.py` programmatically checks every non-authorization flag by iterating over named keys. The catalog regression gate (`v4_catalog_regression_gate.py`) scans all nested JSON output for any `FORBIDDEN_CLAIM_FLAGS` set to non-False.

One precision note: the `"all_benchmark_speedup_claim_authorized"` flag appears in `v4_goal4637_aabb_frontdoor_catalog_decision.py` but is not one of the standard front-door claim boundary keys carried by `aabb_index_query_2d_all_ops_count_claim_boundary_v4`. That is not a failure — the decision-level document is more detailed than the runtime boundary dict — but the runtime boundary lacks that specific key. It is not needed for enforcement since `broad_v4_speedup_claim_authorized: False` covers the concept.

**Conclusion**: Claim boundaries are complete. Pass.

---

### Q6 — Are docs, quickstart, scope gate, catalog gate, and release decision internally consistent?

| Artifact | Measurement | Status |
|---|---|---|
| README surface count | 8 | ✓ matches catalog |
| README measured partners | numba, rtdl_native, torch | ✓ matches `claim_boundary_v4()` |
| `v4_scope.py` includes AABB surface | yes, line 17 | ✓ |
| `v4_scope.py` includes `rtdl_native_prepared_runner` | yes, line 25 | ✓ |
| `v4_frontdoor_test.py` checks 8 surfaces + AABB | yes, lines 29+49 | ✓ |
| `v4_operator_catalog_test.py` checks 8 rows | yes, line 92 | ✓ |
| Catalog regression gate test includes `aabb_index_all_ops_count` | yes, line 62 | ✓ |
| Release decision chains `v4_goal4637_aabb_frontdoor_catalog_decision()` | yes, `v4_release_decision.py` line 47 | ✓ |
| Quickstart exercises `aabb-index-query` alias | yes, via `replace("-", "_")` normalization | ✓ |

**Conclusion**: Internally consistent. No gaps found. Pass.

---

### Q7 — Does this move V4 forward or is it process churn?

Substantive: Goal4637 adds a genuinely new generic primitive class (`AABB_INDEX_QUERY_2D`) with strong hardware evidence, promotes a deferred coverage row, and extends the measured-partner set to include `rtdl_native`. The gate numbers (264x median) are the strongest of any V4 gate to date. This is not churn — it is legitimate operator coverage breadth expansion.

The counterpoint is that this surface does not demonstrate device-array interop, which is V4's primary architectural claim. That point is disclosed and pre-authorized, but reviewers considering V4's overall readiness should weight the AABB contribution as **operator class coverage**, not as evidence that the device-array pipeline is production-ready.

---

### Summary of Notable Observations (Review Debt)

1. **Evidence artifact carries V3 labels** (`m30_all_ops.json`: `"goal": "Goal4427 V3.0 M30 LibRTS..."`, `"version": "rtdl.v3_0.librts_prepared_all_ops_refresh.m30"`). Not blocking; claim boundaries prevent promotion. Record this as provenance debt.

2. **AABB surface is not a device-array front-door**. Python iterables in, count scalars out. This is pre-authorized via `rtdl_native_prepared_runner` in scope, but weakens the AABB surface as evidence for V4's GPU-array value proposition compared to the six Torch surfaces.

3. **Comparison is same-contract-family, not strict same-contract**. Correctly labeled in the catalog and docs, but external readers of the 264x figure should understand it includes prepared-query-handle overhead differences, not only RT-core vs. BVH traversal.

None of these require amendments to the implementation or documentation. The claim boundaries are mechanically enforced, the non-authorizations are complete, the tests cover the critical paths, and the internal consistency is sound.

**Final verdict: `approve_goal4637_aabb_frontdoor_catalog_promotion`**
