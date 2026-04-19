# Goal601 External Review: Apple RT Full-Surface Performance Characterization

Date: 2026-04-19

Reviewer: Claude (claude-sonnet-4-6)

Artifacts reviewed:
- `docs/reports/goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.md`
- `docs/reports/goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.json`
- `scripts/goal601_apple_rt_full_surface_perf.py`
- `docs/release_reports/v0_9_2/release_statement.md`
- `docs/release_reports/v0_9_2/support_matrix.md`

---

## Verdict: ACCEPT

---

## Review Findings

### 1. Native vs. compatibility separation — PASS

The report makes an unambiguous, repeated distinction between `native_mps_rt` and `cpu_reference_compat` rows.

- `native_mps_rt` rows: 3 (segment_intersection_2d, ray_triangle_hit_count_3d, ray_triangle_closest_hit_3d)
- `cpu_reference_compat` rows: 16

The methodology section, the results table column, the JSON `methodology.warning` field, and the interpretation section all state explicitly that `cpu_reference_compat` rows are **not** Apple hardware-backed execution. This separation is correct against the v0.9.2 support matrix, which lists exactly the same three native predicates.

No compat row is presented as evidence of Apple RT hardware performance. The report actively warns against that reading.

### 2. Numerical accuracy — PASS

Recomputed ratios from raw JSON sample arrays for all three native rows:

| Row | JSON Apple median | JSON Embree median | Expected ratio | Reported ratio |
| --- | ---: | ---: | ---: | ---: |
| `segment_intersection_2d` | 0.001051750 s | 0.000013729 s | 76.608x | 76.608x |
| `ray_triangle_hit_count_3d` | 0.021272083 s | 0.000115396 s | 184.339x | 184.339x |
| `ray_triangle_closest_hit_3d` | 0.000618355 s | 0.000020334 s | 30.411x | 30.411x |

All match. Spot-checked compat rows (point_in_polygon 0.846x, conjunctive_scan 0.299x, grouped_count 0.305x) — all correct. The MD is a faithful rendering of the JSON.

### 3. Stability flags — PASS

The `Stable` column is the logical AND of `embree.stable` and `apple_rt.stable`. Verified against all seven `False` rows in the MD:

- `segment_intersection_2d`: both backends unstable (CV 0.788 and 1.397) → False ✓
- `ray_triangle_closest_hit_3d`: Apple unstable (CV 1.628) → False ✓
- `fixed_radius_neighbors`: Embree unstable (CV 0.361) → False ✓
- `bounded_knn_rows`: Embree unstable (CV 0.407) → False ✓
- `triangle_match`: Embree unstable (CV 0.350) → False ✓
- `grouped_sum`: Apple unstable (CV 0.796) → False ✓

No stability flag is falsified. The CV threshold (0.3) is declared in the methodology and the JSON payload.

### 4. Parity reporting — PASS

All 19 rows show `matches_cpu_reference: true` for both backends in the JSON. The MD table shows `True` for all 19 Parity entries. Internally consistent.

### 5. Input size transparency — PASS

The tiny input sizes for native rows (1 ray × 1 triangle for closest-hit; 32 rays × 64 triangles for hit-count; 2×2 segments for segment-intersection) are recorded in the JSON and acknowledged in the interpretation section: *"The tiny native rows in this full-surface table are overhead-characterization fixtures."* The report correctly directs performance readers to Goal600 for scaled evidence. The Goal600 numbers cited (closest-hit 0.547x Embree at 256×256) match `release_statement.md` and `support_matrix.md` exactly.

### 6. Script-to-artifact consistency — PASS

The script was invoked with `--warmups 5 --repeats 20 --cv-threshold 0.3` (non-default flags). The JSON payload records exactly those values under `methodology`. The MD renders them faithfully. The script calls `rt.run_apple_rt` for all Apple RT measurements — no backend substitution occurs.

### 7. Release docs consistency — PASS

The v0.9.2 support matrix lists the same three native predicates and links to this artifact. The release statement performance language is consistent with Goal600 evidence and does not draw on the tiny Goal601 native numbers as speed claims. No public wording contradiction found.

### 8. Row count — PASS

19 measured rows for 18 predicates: `ray_triangle_hit_count` accounts for both a 2D compat row and a 3D native row. Correctly explained in the MD and consistent with the 19-entry JSON `cases` array and 19 entries in `_cases()` in the script.

---

## Summary

The characterization is accurate, fair, and honest. Native Apple RT dispatch is correctly separated from CPU-reference compatibility dispatch throughout — in methodology, results table, and interpretation. Numbers in the markdown are a faithful render of the JSON raw samples. Stability, parity, and ratio values are all correct. The tiny input sizes for native rows are disclosed, and readers are directed to Goal600 for scaled performance conclusions. No misleading claims are present.

**ACCEPT.**
