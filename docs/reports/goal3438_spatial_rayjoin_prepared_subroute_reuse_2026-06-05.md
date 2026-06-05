# Goal3438 Spatial RayJoin Prepared Subroute Reuse

**Date:** 2026-06-05  
**Status:** implemented; pod artifact pending  
**Scope:** app-facing prepared/repeated handles for the three Spatial RayJoin subroutes

## Purpose

Goal3435 made the exact PIP continuation usable through a prepared Python handle:
generic OptiX candidate columns plus a prepared CuPy exact refiner. The LSI
count path already had prepared grouped/dense count handles. The remaining
prepared/repeated usability gap was overlay-seed scalar summaries: users could
call the generic prepared shape-pair active count through the one-shot prepared
route, but not through the same explicit reusable-handle shape.

Goal3438 adds that missing sibling and a single pod probe covering the
prepared/repeated shape across all three subroutes:

- PIP: prepared OptiX candidate columns plus prepared CuPy exact refinement.
- LSI: prepared OptiX segment-pair dense left-id count.
- Overlay-seed: prepared OptiX generic shape-pair active-count.

This keeps the engine app-agnostic. The native side still sees generic
point/closed-shape, segment-pair, and shape-pair primitives.

## What Changed

| File | Operation |
| --- | --- |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Added `PreparedRayJoinOptixShapePairActiveCount`, `prepare_rayjoin_optix_shape_pair_active_count(...)`, `pack_rayjoin_optix_shape_pair_active_count_left_shapes(...)`, and CLI route `prepared_optix_shape_pair_active_count`. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Added the overlay-seed active-count prepared-handle usage pattern. |
| `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py` | Added a visible-progress pod probe for PIP, LSI dense-count, and overlay-seed active-count repeated runs. |
| `src/rtdsl/v2_8_benchmark_runtime_gap.py` | Refreshed the Spatial RayJoin row to record reusable prepared handles across PIP, LSI, and overlay-seed scalar summaries. |
| `tests/goal3438_spatial_rayjoin_prepared_subroute_reuse_test.py` | Added regression coverage for the app surface, README, v2.8 gap row, probe schema, report, and optional pod artifact. |

## Design

The new overlay handle is:

```python
prepare_rayjoin_optix_shape_pair_active_count(right_shapes)
```

It prepares the right-side closed-shape scene once using the existing generic
OptiX shape-pair relation primitive. Callers can run either:

```python
payload = prepared.run(left_shapes)
```

or prepack the left side once:

```python
packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
payload = prepared.run_packed_left(packed_left)
```

The route returns an active pair-dependency count:

```text
overlay_active_pair_dependency_count
```

It does not materialize full overlay relation rows, and it does not implement a
general polygon overlay engine. Full overlay row continuation remains unsolved
for this goal.

## Boundaries

The new route records:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `full_rayjoin_reproduction: False`
- `paper_scale_perf_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`

This goal improves the reference implementation shape and benchmark
repeatability. It does not authorize public RayJoin paper-comparison claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3438_spatial_rayjoin_prepared_subroute_reuse_test tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Expected result:

```text
OK
```

Pod command, once a clean checkout is ready:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py \
  --iterations 4 \
  --candidate-max-rows 60000 \
  --county-cdb data/rayjoin_public_cdb/br_county.cdb \
  --soil-cdb data/rayjoin_public_cdb/br_soil.cdb \
  --output docs/reports/goal3438_spatial_rayjoin_prepared_subroute_reuse_pod_2026-06-05.json
```

The probe prints progress lines for each subroute:

- `[goal3438:pip]`
- `[goal3438:lsi]`
- `[goal3438:overlay]`

## Next

The next harder Spatial RayJoin work is still device-resident full relation-row
continuation: keeping row streams resident when the app needs more than scalar
counts, including parity/count grouping over resident rows and boundary-witness
ownership at serious scale.
