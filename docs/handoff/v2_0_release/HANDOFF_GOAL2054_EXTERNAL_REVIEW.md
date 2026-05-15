# Handoff: Goal2054 Segment/Polygon Hitcount Prepared Scaling Review

Please perform a read-only independent review of Goal2054.

Context:

- Goal2054 builds on Goal2052.
- The runner now has `--skip-one-shot-baseline` so large prepared-only scaling rows do not waste pod time on a one-shot baseline that Goal2052 already measured.
- NVIDIA L4 pod runs at count 8192 with `--output-capacity 262144`, count 16384 with `--output-capacity 1048576`, count 32768 with `--output-capacity 4194304`, and count 65536 with `--output-capacity 16777216`, `--iterations 3`, and `--partners cupy` passed with strict parity.
- The relevant comparison is v2 prepared partner-owned CuPy device count columns vs v1.8 prepared native OptiX hitcount rows.

Review these artifacts:

- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`
- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_8192_prepared_capacity262144.json`
- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_16384_prepared_capacity1048576.json`
- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_32768_prepared_capacity4194304.json`
- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_65536_prepared_capacity16777216.json`
- `docs/reports/goal2054_segment_polygon_hitcount_prepared_scaling_l4_2026-05-15.md`
- `tests/goal2054_segment_polygon_hitcount_prepared_scaling_l4_test.py`

Requested checks:

1. Confirm the skip flag is appropriate and does not pretend a one-shot baseline was measured.
2. Confirm the 8192, 16384, 32768, and 65536 L4 artifacts support bounded prepared same-contract timing rows.
3. Confirm strict parity and prepared scene/output-column reuse are present.
4. Confirm the report blocks overclaims: no v2.0 release readiness, no broad all-app speedup, no broad RT-core speedup, no exact polygon overlay/Jaccard or exact Hausdorff bridge claim.
5. Confirm whether the verdict should be `accept-with-boundary`.

Please write the review to:

- `docs/reviews/goal2055_gemini_review_goal2054_prepared_scaling_l4_2026-05-15.md`
