# Goal2932: CuPy Presegmented Vector-Sum Partner Preview

Date: 2026-06-01
Status: pod runtime smoke passed

## Purpose

Goal2932 responds to the Barnes-Hut v2.5 weak spot: the RT membership/frontier
phase is strong, but the generic grouped 2D vector-sum continuation had been
measured only as Torch versus Triton, with Triton remaining slower.

This goal adds and measures a generic CuPy partner route for
`grouped_vector_sum_f64x2`:

- app-neutral input contract: `group_ids`, optional `row_offsets`, `values_x`,
  `values_y`, and `group_count`;
- generic CuPy RawKernel path for presegmented row-offset inputs;
- existing CuPy by-key route remains available for non-offset inputs;
- no native RT engine customization and no Barnes-Hut force law in the engine.

## Pod Evidence

Pod:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- source commit: `f60c4e789fc8dfaa9c6603b0b645e31b6389896d`
- source dirty: `[]`
- Python: `3.12.3`
- CuPy: `14.1.0`
- Torch: `2.8.0+cu128`
- Triton: `3.4.0`

Artifacts:

- `docs/reports/goal2932_cupy_presegmented_vector_sum_pod/goal2932_cupy_vector_sum_8192x16.json`
- `docs/reports/goal2932_cupy_presegmented_vector_sum_pod/goal2932_cupy_vector_sum_65536x16.json`

Command shape:

```text
python3 scripts/goal2932_cupy_presegmented_vector_sum_tuning.py \
  --group-count 8192 --rows-per-group 16 --repeats 9 --warmups 3 \
  --output /tmp/goal2932_cupy_vector_sum/goal2932_cupy_vector_sum_8192x16.json

python3 scripts/goal2932_cupy_presegmented_vector_sum_tuning.py \
  --group-count 65536 --rows-per-group 16 --repeats 9 --warmups 3 \
  --output /tmp/goal2932_cupy_vector_sum/goal2932_cupy_vector_sum_65536x16.json
```

## Results

All measured routes matched the Torch same-contract reference on both shapes.

| Shape | Torch scatter-add median | Triton offsets median | CuPy offsets RawKernel median | CuPy add.at median | Fastest |
| --- | ---: | ---: | ---: | ---: | --- |
| `8192 x 16` | `0.000874647s` | `0.004378239s` | `0.000800442s` | `0.000677782s` | CuPy add.at |
| `65536 x 16` | `0.006323243s` | `0.010033897s` | `0.004308179s` | `0.004144579s` | CuPy add.at |

Interpretation:

- The generic CuPy RawKernel path is correct and beats Torch on the measured
  large shape (`0.681x` CuPy-offsets-over-Torch) while also beating Triton
  offsets on both measured shapes.
- The existing CuPy by-key route is still the fastest route for these dense
  fixed-rows-per-group shapes.
- This supports the v2.5 partner-choice rule: the user/app should be able to
  choose CuPy for this continuation, while Triton remains visible and
  unpromoted when it loses same-contract timing.

## Design Effect

Goal2932 changes the partner support/conformance position for
`grouped_vector_sum_f64x2`:

- Triton remains a preview, not a promoted performance path.
- CuPy is now also an explicit preview for this operation, backed by pod runtime
  evidence.
- The support matrix now permits overlapping partner previews for the same
  generic operation, because user-selectable partner choice is a core v2.5
  principle.

This does not weaken RTDL's app-agnostic engine boundary. The native engine
still produces generic membership/frontier/row contracts; partner code performs
generic vector reduction over partner-owned columns.

## Boundary

Goal2932 does not authorize v2.5 release, public speedup wording, broad RT-core
claims, whole-app speedup claims, true zero-copy claims, package-install claims,
automatic Triton selection, automatic CuPy selection, paper-reproduction claims,
or app-specific native engine logic.

The immediate next engineering action is to let the Barnes-Hut consolidated
harness consider CuPy as an explicit measured partner for the generic
vector-sum continuation, while preserving the claim boundary above.
