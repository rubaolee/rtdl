# Goal3593 - RayJoin Public-CDB CuPy Same-Contract Probe

Date: 2026-06-06

Status: internal evidence only

## Purpose

Goal3593 extends the Goal3589 same-contract pressure test from authored square/tiled fixtures to bounded public CDB slices. The question is deliberately narrow:

> On small public RayJoin-style CDB inputs, how does the current RTDL/OptiX hot route compare with a direct CuPy RawKernel CUDA-core baseline for the same output contract?

This is not a RayJoin paper reproduction and not release evidence. It is a diagnostic probe for choosing explicit v2.8 reference routes.

## Runner

Script:

- `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`

Artifact:

- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_a5000/summary.json`

The runner reuses the Goal3589 CuPy and RTDL/OptiX same-contract helpers, but points them at public CDB slices that were already present on the A5000 pod:

- `br_county_start256_count512.cdb`
- `br_soil_start256_count512.cdb`

The runner also hardened the Goal3589 CuPy LSI baseline to accept RTDL's generic `SegmentColumns2D` input layout. That was needed because public CDB LSI loading uses columnar segment inputs rather than iterable segment records.

## Pod Configuration

GPU:

- NVIDIA RTX A5000

Command shape:

```bash
cd /root/rtdl_goal3556_current
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/root/rtdl_goal3556_current/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_embree.so
python3 scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py \
  --data-dir /root/rtdl_goal3293/data/rayjoin_public_cdb \
  --cases all \
  --repeat 5 \
  --warmup 1 \
  --output /tmp/goal3593_public_cdb_summary.json
```

Pod commit:

- `9432ee19a25fa5c3509c039e95541642db6b7bf3`

## Results

| Case | Contract | CuPy CUDA-Core Median Sec | RTDL/OptiX Median Sec | RTDL/OptiX vs CuPy | Count | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `pip_county512` | point-to-shape positive hit count | 0.000450083 | 0.002804101 | 0.161x | 1417 | CuPy faster |
| `lsi_county512_soil512` | segment-segment intersection count | 0.024092625 | 0.000462214 | 52.124x | 269 | RTDL/OptiX faster |
| `overlay_county512_soil512` | overlay active pair dependency count | 0.049257061 | 0.000594303 | 82.882x | 174 | RTDL/OptiX faster |

Summary:

- All counts matched.
- Minimum RTDL/OptiX-vs-CuPy ratio: `0.1605x`.
- Geomean RTDL/OptiX-vs-CuPy ratio across the three bounded public-CDB rows: `8.8512x`.

## Interpretation

The public-CDB probe changes the RayJoin story in an important way:

- PIP remains a case where a simple dense CuPy count baseline is faster than the current prepared RTDL/OptiX path at this bounded size.
- LSI strongly favors RTDL/OptiX on public CDB segment columns because the CUDA-core dense all-pairs segment-intersection kernel is much heavier than the prepared OptiX route.
- Overlay active-pair dependency count also strongly favors RTDL/OptiX on these public slices.

This supports an explicit mixed-route recommendation for the RayJoin reference app:

- choose CuPy for simple PIP count at this size,
- choose RTDL/OptiX for public-CDB LSI,
- choose RTDL/OptiX for public-CDB overlay active-pair dependency count.

This is still a user-visible route choice, not automatic dispatch.

## Boundary

Goal3593 does not authorize:

- RTDL beats RayJoin paper claims,
- broad RT-core speedup claims,
- whole-app RayJoin speedup claims,
- release claims,
- true zero-copy claims,
- automatic partner/backend selection claims.

The result is useful internal evidence that RTDL/OptiX has real strength on public-data LSI and overlay contracts, while also preserving the negative PIP finding from Goal3589.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test tests.goal3589_rayjoin_cupy_same_contract_baseline_test
Ran 7 tests in 2.344s
OK (skipped=1)
```

After the A5000 artifact was copied into the repository, the Goal3593 artifact-aware test passed:

```text
py -3 -m unittest tests.goal3593_rayjoin_public_cdb_cupy_same_contract_probe_test
```

The initial pod launch failed once because PowerShell expanded `$PWD` into a Windows path inside the SSH command. The clean rerun used explicit pod paths for `RTDL_OPTIX_LIB` and `RTDL_OPTIX_LIBRARY`.
