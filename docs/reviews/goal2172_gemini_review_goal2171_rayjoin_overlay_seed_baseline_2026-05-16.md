# Gemini Review for Goal2171 RayJoin Overlay Seed Baseline

## Verdict

`accept`

## Independent Review Statement

This is an independent Gemini review, distinct from the authoring process. This review confirms the findings and stated boundaries of Goal2171 but does not, by itself, authorize a v2.0 release.

## Review Questions and Answers

### 1. Verify that the artifact-backed numbers in the report match the JSON.

**Answer:** Passed.

The numerical data in `docs/reports/goal2171_rayjoin_overlay_seed_baseline_2026-05-16.md` matches the values in `docs/reports/goal2171_rayjoin_overlay_seed_baseline_pod_2026-05-16.json`.

- CPU median: `0.152511` in the report, `0.15251125488430262` in the JSON.
- Embree median: `0.022165` in the report, `0.02216548379510641` in the JSON.
- OptiX median: `0.025159` in the report, `0.025159044191241264` in the JSON.
- Rows: `14,036` in the report, `14036` in the JSON.
- Commit: `7e4f440425b8e19caed147097945504b47aa9b81` in both the report and JSON.

### 2. Verify that the interpretation is bounded.

**Answer:** Passed.

The report's interpretation is appropriately bounded and consistent with the evidence. It states that both RTDL backends accelerate the overlay seed path by about 6x over the measured CPU reference, while also acknowledging that OptiX is RT-core-accelerated but still slower than Embree on this slice. The claim-boundary section and the JSON artifact explicitly block full RayJoin paper reproduction, broad RT-core speedup claims, and v2.0 release authorization.

### 3. Check whether the proposed next engineering target is technically reasonable.

**Answer:** Passed.

The proposed next engineering target - adding a prepared/reused generic OptiX shape-pair relation surface, analogous to the prepared LSI surface from Goal2163 - is technically reasonable and well justified. The report argues that the current OptiX path's performance limitation is due to setup and output shape rather than raw traversal capability. Reusing pre-built acceleration structures is a standard optimization strategy, and the successful Goal2163 LSI pattern provides precedent.

### 4. Check whether the test meaningfully protects the artifact, claim boundary, and next-step interpretation.

**Answer:** Passed.

The test `tests/goal2171_rayjoin_overlay_seed_baseline_test.py` meaningfully protects the evidence. It checks the report's boundary wording, validates the artifact commit, workload, row counts, parity flags, RT-core flag, and bounded speedups, and directly asserts that the JSON claim-boundary flags block unauthorized broader claims.

## Conclusion

Goal2171 successfully records a bounded overlay-seed baseline. It demonstrates RTDL acceleration over the CPU Python reference while maintaining parity, keeps claims narrow, and identifies a technically reasonable next optimization target.
