# Handoff: Goal2052 Segment/Polygon Hitcount CuPy L4 Runner Repair Review

Please perform a read-only independent review of Goal2052.

Context:

- Goal2052 repaired `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`.
- The bug was that OptiX ray columns (`ox`, `oy`, `dx`, `dy`, `tmax`) were created as float64 partner tensors, while the bounded all-witness OptiX ABI requires float32 ray columns.
- The repair changes only those ray columns to float32; triangle coordinate columns remain float64 and AABBs remain float32.
- A NVIDIA L4 pod run at count 2048 succeeded with strict parity.
- A 4096-row default-capacity follow-up reached the v2 partner path and failed closed with witness output overflow, so Goal2052 also adds an explicit `--output-capacity` knob for larger pod runs.
- A 4096-row L4 rerun with `--output-capacity 32768` passed with strict parity and showed the prepared v2 CuPy path faster than the same-contract v1.8 prepared OptiX row.

Review these artifacts:

- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`
- `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_2048.json`
- `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_4096_capacity32768.json`
- `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_runner_repair_2026-05-15.md`
- `tests/goal2052_segment_polygon_hitcount_cupy_l4_runner_repair_test.py`

Requested checks:

1. Confirm the runner repair is technically correct and scoped to the OptiX ray ABI dtype mismatch plus the explicit output-capacity benchmark knob.
2. Confirm the 2048 and explicit-capacity 4096 L4 artifacts support bounded same-contract timing rows: v2 prepared CuPy count columns vs v1.8 prepared OptiX hitcount rows.
3. Confirm the report treats the first v2 unprepared sample as setup/JIT/cache cost rather than hiding it.
4. Confirm the claim boundary is strong: no v2.0 release readiness, no broad RT-core speedup, no whole-app speedup, no package-install claim.
5. Confirm whether the verdict should be `accept-with-boundary`.

Please write the review to:

- `docs/reviews/goal2053_gemini_review_goal2052_segment_polygon_hitcount_cupy_l4_2026-05-15.md`
