All five facts are verifiable in the files. Here is my determination:

---

## ACCEPT

All stated facts check out. The reclassification from `diagnostic_blocked` to `pod_verified_generic` is warranted.

### Fact verification

**1. Active backend scope before v2.1 is Embree + OptiX only.**
Confirmed in both `v1_5_migration_inventory.py:6-7` (`ACTIVE_V1_5_BACKENDS = ("embree", "optix")`) and `generic_polygon_primitives.py:11-12` (`ACTIVE_V1_5_GENERIC_POLYGON_BACKENDS = ("embree", "optix")`), with `vulkan`, `hiprt`, `apple_rt` explicitly frozen.

**2. Native bounded collection is routed and pod-validated.**
Goal1318 pod (host `213.173.99.11`, port `39006`) rebuilt OptiX from `origin/main`, ran 11 focused tests, all OK. Real OptiX app route produced `collection.native_collection=true`, `collection.backend=optix`, `collection.complete_candidate_coverage=true`. Stale-library fallback is preserved; no silent truncation.

**3. Score reduction uses `POLYGON_SET_JACCARD_SCORE_REDUCTION` and backend-neutral ABI `rtdl_native_reduce_polygon_pair_exact_area_summary`.**
- `generic_polygon_primitives.py:161` emits `"primitive": "POLYGON_SET_JACCARD_SCORE_REDUCTION"`.
- `rtdl_oracle_abi.h:338-351` declares `rtdl_native_reduce_polygon_pair_exact_area_summary` with `RtdlPolygonPairAreaSummary* summary_out`.
- `rtdl_polygon_set_jaccard.py:112` routes through `rt.reduce_polygon_pair_exact_area_summary_for_candidates`, not the old app-named `rtdl_oracle_refine_polygon_set_jaccard_for_pairs`.
- Goal1321 test at line 18 asserts `rtdl_native_run_polygon_set_jaccard_fast` does NOT appear in the API — no app-named fast path exists.
- Goal1321 pod evidence shows `exact_score_continuation=backend_neutral_native_polygon_pair_area_summary` in the real OptiX output.

**4. Pod OptiX evidence exists for all three goals.**
- Goal1318: 11 tests, OK; real OptiX run with correct Jaccard output.
- Goal1320: 8 tests, OK; real OptiX run emitting `score_reduction_primitive=POLYGON_SET_JACCARD_SCORE_REDUCTION`.
- Goal1321: 11 tests in 5.141s, OK; real OptiX run showing `native_continuation_backend=native_polygon_pair_area_summary` and `mode=diagnostic_native_candidate_plus_generic_area_summary`.

**5. No public speedup wording; OptiX remains slower/diagnostic.**
All three goal reports carry explicit boundary language. Goal1321 final note: "The path remains diagnostic because the OptiX route is still slower than Embree and public speedup wording is not authorized." The inventory validator (`v1_5_migration_inventory.py:228`) hard-enforces `public_wording_authorized=False` on every row — no policy bypass path exists.

### Authorized reclassification

The sole remaining blocker recorded in the current `diagnostic_blocked` entry — `"native score reduction after complete candidate coverage"` — is resolved by Goals 1320 and 1321. No new app-specific work remains.

The inventory entry for `polygon_set_jaccard / chunked_candidate_scoring` may become:

```python
"status": "pod_verified_generic",
"generic_primitive": "COLLECT_K_BOUNDED",
"summary_primitive": "REDUCE_FLOAT(SUM)",
"backend_scope": ACTIVE_V1_5_BACKENDS,
"remaining_app_specific_work": (),
"public_wording_authorized": False,
"boundary": (
    "diagnostic native candidate-plus-backend-neutral area-summary pipeline; "
    "OptiX route remains slower than Embree; no public speedup wording; "
    "no fused GPU Jaccard kernel claim; Vulkan/HIPRT/Apple RT frozen before v2.1"
),
```

**Public wording:** unauthorized.  
**OptiX speedup wording:** blocked; OptiX-slower reason is recorded in all three goal reports and carries forward into the boundary.
