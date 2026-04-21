# Goal 711 Embree App Coverage Gate — Claude Review

Date: 2026-04-21  
Reviewer: Claude (claude-sonnet-4-6)  
Verdict: **ACCEPT**

Re-reviewed: 2026-04-21 after exit-code fix.

---

## Summary

The gate covers the correct app set, uses a sound semantic-comparison method,
and makes no false performance claims. The previously blocking exit-code defect
has been corrected: `payload["valid"]` now incorporates both `commands_valid`
and `canonical_payloads_match`, and the script exits nonzero when either
condition fails. The regenerated macOS JSON confirms all 14 apps pass both
checks. The gate is accepted as a sound CI artifact.

---

## Coverage Completeness: PASS

The support matrix lists exactly 14 apps with `direct_cli_native` Embree status.
The gate covers all 14. Non-Embree app rows are correctly excluded:

- `rtdl_apple_rt_demo_app.py` — `apple_specific` for Embree, excluded.
- `rtdl_polygon_pair_overlap_area_rows.py` — `not_exposed_by_app_cli`, excluded.
- `rtdl_polygon_set_jaccard.py` — `not_exposed_by_app_cli`, excluded.
- `rtdl_hiprt_ray_triangle_hitcount.py` — `not_exposed_by_app_cli`, excluded.

The exclusions are consistent with the matrix. No app advertised as
`direct_cli_native` is missing from the gate.

---

## Semantic Comparison Method: PASS WITH NOTES

`_canonical_payload` strips `backend`, `requested_backend`, `data_flow`, and
`prepared_dataset` before hashing. This is appropriate: those keys are
execution metadata, not application results. Float rounding to 12 decimal places
is a reasonable tolerance for process-startup-scale smoke fixtures where the same
algorithm runs on both backends. List canonicalization by JSON string sort is
sound for row-order-independent correctness.

**Notes (not blocking):**

- `segment_polygon_hitcount` and `segment_polygon_anyhit_rows` emit
  `payload_app: null` in their JSON output. The apps do not self-identify by
  name. The gate does not rely on `payload_app` for pass/fail, so this does not
  change results, but it is an inconsistency with the other 12 apps.

- `segment_polygon_anyhit_rows` is tested only with `--output-mode
  segment_counts`. The default mode and any other output mode are not covered.

- `robot_collision_screening` is tested only with `--output-mode hit_count`. The
  default row-output mode is not covered.

These partial-mode gaps do not invalidate the current gate run, but they leave
semantic correctness of other modes unverified.

---

## Gate Pass/Fail Logic: **PASS** (fixed)

The previously blocking defect has been resolved. In the current
`scripts/goal711_embree_app_coverage_gate.py` (line 135):

```python
payload["valid"] = bool(payload["commands_valid"] and payload["canonical_payloads_match"])
```

and line 140:

```python
return 0 if payload["valid"] else 1
```

`payload["valid"]` now requires both `commands_valid` (all runs exit 0 with
valid JSON) and `canonical_payloads_match` (all 14 per-app SHA-256 hashes
agree). The gate will return exit code 1 if any Embree app diverges from the
CPU/Python oracle, which is exactly the required CI behavior.

The regenerated macOS JSON confirms: `"valid": true`, `"commands_valid": true`,
`"canonical_payloads_match": true`, all 14 apps with `canonical_payload_match:
true`.

---

## Performance Claims: PASS

The gate document is explicit and accurate on this point:

- All 28 smoke-scale runs complete in 0.10–0.15 s, dominated by Python process
  startup and JSON production.
- No whole-app Embree speedup is claimed from these numbers.
- Embree runs are often slightly slower than CPU at this scale (ratios 1.05–1.12
  for most apps), which is expected when BVH construction cost is not amortized
  by a large traversal workload. The gate document acknowledges this.
- The one notable outlier — `graph_analytics` at 0.71x ratio — is in Embree's
  favor and within the noise of process-startup-dominated measurements.
- Kernel-level performance evidence is correctly deferred to Goal 710, which
  records a 5.43x speedup for `knn_rows` at scale.

The performance boundary section in the gate report is honest.

---

## Honesty Boundary: PASS

The gate document correctly states what it proves and what it does not:

- Proves: the 14 `direct_cli_native` Embree CLI paths are runnable and
  semantically consistent with the CPU/Python oracle on the checked fixtures.
- Does not prove: Embree is faster for every whole app; large-scale Windows or
  Linux multicore performance; multithreading parity beyond point-query kernels.

The app JSON payloads include `honesty_boundary` and `optix_performance` fields
consistent with the support matrix and OptiX performance classification table.
No app overstates its acceleration class.

---

## Outstanding Non-Blocking Notes

The following were noted in the initial review and remain open but do not block
acceptance:

1. **Optional**: `segment_polygon_anyhit_rows` is tested only with
   `--output-mode segment_counts`; `robot_collision_screening` is tested only
   with `--output-mode hit_count`. Other output modes are not covered. Add them
   or document the scope explicitly at a future gate revision.

2. **Cosmetic**: `segment_polygon_hitcount` and `segment_polygon_anyhit_rows`
   emit `payload_app: null` (no `app` self-identification field). Not a gate
   failure, but inconsistent with the other 12 apps.

---

## Verdict

**ACCEPT**. The exit-code defect identified in the initial review is fixed.
The gate now enforces semantic correctness (`canonical_payloads_match`) as part
of its pass/fail condition. The regenerated macOS run confirms 14/14 apps
pass all checks. Performance claims are bounded and honest.
