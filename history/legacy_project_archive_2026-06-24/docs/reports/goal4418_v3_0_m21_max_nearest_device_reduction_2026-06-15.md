# Goal4418 / V3.0 M21 max-nearest device-reduction bridge

Status: `accept-with-boundary`

This milestone closes a concrete V3 bridge debt from the M20 benchmark-app audit: the generic point-group nearest-witness producer could already emit device output columns, but its query side still used host-packed query points. M21 adds an app-agnostic route where caller-owned CUDA query columns feed the prepared native OptiX point-group nearest-witness path, and the result stays in device columns for a partner-side global max reduction.

This is not a public speedup claim. It is internal bridge evidence for a common max-nearest-distance pattern used by Hausdorff/XHD-style apps.

## What Changed

| Piece | Result |
|---|---|
| Native RT producer | Prepared OptiX point-group nearest-witness now accepts caller-owned device query columns: `ids`, `x`, `y`. |
| Device output | Native writes `query_ids`, `neighbor_ids`, and `distances` directly into caller-owned CUDA output columns. |
| Device handoff | Runtime exposes `write_device_nearest_witness_columns_from_device_query_columns`. |
| Partner reduction | The same hot device rows are reduced by CuPy and by Numba through the generic `global_argmax_u32_f64` contract. |
| Numba hot-window fix | Numba can skip the host-side non-empty validation copy when the caller already controls result materialization after the hot device window. |

## Pod Evidence

Artifact: `docs/reports/goal4418_v3_0_m21_max_nearest_device_reduction_65536_2026-06-15.json`

Hardware: RTX 4000 Ada pod, driver 550 path. Workload: 65,536 2D search/query points, 4,096 point groups from a 64x64 spatial grouping, radius 0.025, 2 warmups, 5 repeats. Query columns and output columns are prepared before the hot window.

Command:

```bash
python scripts/v3_0_m21_max_nearest_device_reduction_measure.py \
  --point-count 65536 \
  --group-axis 64 \
  --radius 0.025 \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4418_v3_0_m21_max_nearest_device_reduction_65536_2026-06-15.json
```

| Partner | Hot device median | Materialize median | Hot transfer counter | Signature |
|---|---:|---:|---|---|
| CuPy | 0.001847s | 0.0000783s | 104 B H2D, 0 B D2H/D2D/unknown; no hidden column copy | matched |
| Numba | 0.002606s | 0.000166s | 104 B H2D, 0 B D2H/D2D/unknown; no hidden column copy | matched |

The prepare window intentionally includes initial search scene build, query-column upload, and output allocation. The hot measured window starts after scene/query/output residency. The hot timer stops only after the producer and partner reduction have synchronized device completion; materialization still happens afterward.

Additional measured preparation context: prepare time was 0.675959s. The matched validation signature was `(query_id=11012, neighbor_id=51502, row_index=11012, distance_ns=6810366, valid_count=65536)`.

## Interpretation

M21 is the right V3 answer to the M20 max-nearest reduction debt: RTDL should not force the app to repack query points on the host when a partner already has query columns on the GPU. The native engine now consumes those columns directly, and both CuPy and Numba can consume the producer output before any host materialization.

The CuPy row is the practical best current partner for this reduction. The Numba row is still valuable because it proves the no-C++/no-CUDA-kernel user path can stay inside the same device-resident contract; it is slower than CuPy here, but it preserves the user-level programming story.

This preserves the current V3 design boundary:

| Boundary | M21 position |
|---|---|
| Generic engine | The public route is named around prepared point-group nearest-witness and global max reduction, not a benchmark app. |
| Rich primitives | The primitive emits typed nearest-witness columns with query id, neighbor id, and distance. |
| Partner logic | CuPy is the practical best partner; Numba is the no-C++/no-CUDA-kernel reference partner. |
| Public claims | Public RT-core speedup, paper parity, and whole-app speedup remain gated until benchmark apps are rerun end to end. |

## Claim Boundary

Allowed internal wording: M21 adds an app-agnostic prepared point-group nearest-witness device-query-column producer and demonstrates CuPy/Numba device-side global max reductions without hot-window host query upload or pre-consumer row materialization.

Forbidden wording: public speedup, whole-app speedup, RT-core efficiency parity, author-code parity, automatic partner selection, or end-to-end true-zero-copy.
