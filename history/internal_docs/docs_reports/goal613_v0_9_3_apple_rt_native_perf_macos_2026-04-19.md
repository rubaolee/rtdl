# Goal613: v0.9.3 Apple RT Native Performance Characterization

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Methodology

- Warmups before sample window: `2`
- Measured repeats: `7`
- Stability threshold: coefficient of variation <= `0.3`
- Apple RT runs use `native_only=True`.
- Embree is the mature local RTDL baseline.
- CPU reference is used only for parity.
- Native-assisted means Apple MPS RT performs candidate or flag discovery; CPU refinement/materialization may still be used as documented in Goals 608-612.

## Host

```json
{
  "platform": "macOS-26.3-arm64-arm-64bit-Mach-O",
  "machine": "arm64",
  "processor": "arm"
}
```

## Versions

```json
{
  "apple_rt": [
    0,
    9,
    3
  ],
  "apple_rt_context": "Apple M4",
  "embree": [
    4,
    4,
    0
  ]
}
```

## Results

| Workload | Predicate | Inputs | Rows | Embree median | Apple RT median | Apple/Embree | Embree parity | Apple parity | Stable |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `ray_triangle_closest_hit_3d` | `ray_triangle_closest_hit` | `{'rays': 128, 'triangles': 128}` | 128 | 0.000793958 s | 0.000980958 s | 1.236x | True | True | False |
| `ray_triangle_hit_count_3d` | `ray_triangle_hit_count` | `{'rays': 96, 'triangles': 256}` | 96 | 0.001006792 s | 0.102206042 s | 101.517x | True | True | True |
| `ray_triangle_hit_count_2d` | `ray_triangle_hit_count` | `{'rays': 64, 'triangles': 64}` | 64 | 0.000132459 s | 0.034088500 s | 257.351x | False | True | True |
| `segment_intersection` | `segment_intersection` | `{'left': 64, 'right': 64}` | 4096 | 0.002580958 s | 0.033217750 s | 12.870x | True | True | True |
| `point_in_polygon_full_matrix` | `point_in_polygon` | `{'points': 64, 'polygons': 16}` | 1024 | 0.000497917 s | 0.001199166 s | 2.408x | True | True | False |
| `point_in_polygon_positive_hits` | `point_in_polygon` | `{'points': 64, 'polygons': 16}` | 64 | 0.000060916 s | 0.001324541 s | 21.744x | True | True | False |
| `segment_polygon_hitcount` | `segment_polygon_hitcount` | `{'segments': 64, 'polygons': 16}` | 64 | 0.000035041 s | 0.010640458 s | 303.657x | True | True | False |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows` | `{'segments': 64, 'polygons': 16}` | 120 | 0.000051792 s | 0.010210375 s | 197.142x | True | True | False |
| `point_nearest_segment` | `point_nearest_segment` | `{'points': 64, 'segments': 64}` | 64 | 0.000045500 s | 0.040341750 s | 886.632x | False | True | True |
| `fixed_radius_neighbors` | `fixed_radius_neighbors` | `{'queries': 32, 'points': 128}` | 64 | 0.000137209 s | 0.034762958 s | 253.358x | True | True | True |
| `knn_rows` | `knn_rows` | `{'queries': 32, 'points': 128}` | 64 | 0.000197416 s | 0.063304875 s | 320.667x | True | True | False |
| `bounded_knn_rows` | `bounded_knn_rows` | `{'queries': 32, 'points': 128}` | 64 | 0.000278625 s | 0.050769792 s | 182.215x | True | True | True |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_area_rows` | `{'left': 2, 'right': 2}` | 2 | 0.000020000 s | 0.012634750 s | 631.736x | True | True | False |
| `polygon_set_jaccard` | `polygon_set_jaccard` | `{'left': 2, 'right': 2}` | 1 | 0.000022375 s | 0.010813958 s | 483.305x | True | True | False |
| `overlay_compose` | `overlay_compose` | `{'left': 2, 'right': 2}` | 4 | 0.000019250 s | 0.003692250 s | 191.805x | False | True | False |

## Major Conclusion

- Best correctness-valid Apple-vs-Embree median ratio in this run: `ray_triangle_closest_hit_3d` at `1.236x`.
- Worst correctness-valid Apple-vs-Embree median ratio in this run: `polygon_pair_overlap_area_rows` at `631.736x`.
- The current Apple RT backend is correctness-broad for geometry/nearest-neighbor native/native-assisted rows, but it is not broadly performance-leading versus Embree on this Mac-local harness.
- This report should be treated as engineering evidence for optimization planning, not public speedup wording.

## Correctness-Validity Notes

The following Apple/Embree timing ratios are not correctness-valid comparisons because at least one backend did not match the CPU reference on that fixture:

- `ray_triangle_hit_count_2d`
- `point_nearest_segment`
- `overlay_compose`

## External Review

Gemini 2.5 Flash reviewed the harness, JSON, and Markdown report in `/Users/rl2025/rtdl_python_only/docs/reports/goal613_gemini_perf_review_2026-04-19.md`.

Verdict: ACCEPT.

Gemini found no blockers and specifically accepted that the report separates Apple parity from Embree parity, flags invalid Apple/Embree ratios, and avoids public speedup wording.
