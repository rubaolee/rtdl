# Goal3658 RayJoin PIP Tuned Device Predicate

Date: 2026-06-06

Status: internal v2.9 performance improvement; not release or public speedup
authorization.

## Purpose

Goal3657 left one sharp RayJoin gap: PIP scalar positive-membership count still
recommended the dense CuPy CUDA-core route because the RTDL/OptiX exact route
paid candidate download plus host exact-refine overhead.

Goal3658 tests a smaller generic fix before inventing a new RayJoin-specific
path: make the existing generic point/closed-shape device predicate epsilon an
explicit OptiX specialization knob and run the already fail-closed validated
device-count route with a tighter epsilon.

## What Changed

| Area | Change |
| --- | --- |
| Native OptiX | Added `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS` specialization for generic point/closed-shape device predicates. |
| Runner | Added `--rtdl-pip-device-predicate-eps` and allowed PIP prepared count modes to use `--rtdl-internal-query-repeat`. |
| Validation | The route still validates every measured sample against the exact prepared count and fails closed on mismatch. |

This remains app-agnostic. The native side sees only point ids, closed-shape
refs, a predicate tolerance, and a scalar count. RayJoin/CDB interpretation
stays in the Python benchmark app.

## A5000 Evidence

Artifact:

- `docs/reports/goal3658_rayjoin_pip_tuned_device_predicate_a5000/summary.json`

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- Clean checkout commit `9c85c2a0`
- `source_dirty_recorded: []`

Command shape:

```bash
python3 scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py \
  --workloads pip \
  --rayjoin-query-exec /root/RayJoin/release/bin/query_exec \
  --rayjoin-data-dir /root/rtdl_goal3595_clean/data/rayjoin_public_cdb \
  --rayjoin-pip-poly1 /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rayjoin-pip-poly2 /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rtdl-pip-dataset /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rayjoin-warmup 100 \
  --rayjoin-repeat 30000 \
  --rayjoin-process-repeats 3 \
  --rtdl-repeat 3 \
  --rtdl-internal-warmup 100 \
  --rtdl-internal-query-repeat 30000 \
  --rtdl-pip-count-mode device_filtered_prepared_points_validated \
  --rtdl-pip-boundary-mode inclusive \
  --rtdl-pip-scalar-count-pipeline \
  --rtdl-pip-device-predicate-eps 1e-9
```

## Results

| Route | Count | Median Query ms | Median Total ms | Notes |
| --- | ---: | ---: | ---: | --- |
| RTDL tuned validated device count | 1417 | 0.283574 | 8536.058 | `30000` internal repeats; `eps=1e-9`; exact validation passed. |
| RTDL exact prepared validation in same run | 1417 | 1.949044 | n/a | Used as fail-closed oracle per sample. |
| RayJoin `query_exec` reported PIP query | n/a | 0.191354 | process wall median 6748.267 | Upstream binary does not expose positive-assignment count. |
| Prior Goal3595 CuPy dense baseline | 1417 | 0.437917 | 87.362 over 200 repeats | Prior fastest same-contract public-CDB PIP scalar count. |
| Prior Goal3596 RTDL exact prepared | 1417 | 0.802434 | n/a | Previous best RTDL-only PIP scalar count. |

Ratios:

- Tuned RTDL vs prior CuPy dense: `0.652x` RTDL/CuPy, about `1.53x` faster than the prior CuPy scalar count row.
- Tuned RTDL vs prior RTDL exact prepared: `0.356x`, about `2.81x` faster.
- Tuned RTDL vs same-run exact validation: about `7.96x` faster.
- Tuned RTDL vs RayJoin `query_exec` reported PIP query: `1.482x` slower.

## Interpretation

This changes the RayJoin PIP position:

- The old statement "CuPy wins PIP scalar count" is no longer true for this
  bounded public-CDB slice.
- RTDL/OptiX now has the best current same-contract PIP scalar count among the
  project-owned RTDL/CuPy routes measured here.
- RayJoin's own PIP query remains faster on its reported timing, and the
  upstream binary still does not expose the positive-assignment count, so this
  is not a paper-reproduction or RTDL-beats-RayJoin claim.

The performance gain comes from avoiding candidate row materialization and host
exact refinement in the timed lane. The tuned device predicate counts exact
positive memberships on this validated domain with no candidate download and
no host refine in the hot path.

## Current RayJoin Position After Goal3658

| Contract | Best current RTDL route | Evidence | Status |
| --- | --- | --- | --- |
| PIP positive assignment count | RTDL/OptiX prepared-points validated device count with `eps=1e-9` | Goal3658: `1417` exact count, `0.283574ms`, `8.54s` total median over `30000` repeats | Improved; beats prior CuPy dense baseline, still slower than RayJoin query timing. |
| LSI visible segment-pair count | RTDL/OptiX prepared-left generic segment-pair route | Goal3654: `4977 == 4977`, `0.100411ms`, `10.31s` total median | Strong RTDL-positive evidence. |
| Overlay active pair-dependency count | RTDL/OptiX prepared shape-pair active count | Goal3595: `91.742x` vs CuPy on 512 public-CDB slice | Strong contract evidence, not full polygon overlay materialization. |

## Remaining Target

The next PIP leap is not another hidden tolerance tweak. It is a first-class
generic exact closed-shape membership/count primitive with:

- explicit precision/tolerance policy;
- deterministic boundary ownership semantics;
- device-resident prepared point/shape columns;
- no app-specific RayJoin/CDB language in the native ABI;
- validation across more public-CDB slices and a second GPU.

## Boundary

Goal3658 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- RTDL-beats-RayJoin wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

Pod:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk -j2
```
