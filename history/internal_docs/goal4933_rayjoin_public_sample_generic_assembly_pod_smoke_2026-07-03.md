# Goal4933: RayJoin Public-Sample Generic Assembly POD Smoke

Date: 2026-07-03

Verdict requested: `complete_correct_but_not_faster__generic_assembly_wired`

## Purpose

Goal4933 tested whether the new generic host-columnar grouped-sequence assembly layer from Goal4932 can be wired into the RayJoin Section 5.7 public-sample app without changing correctness.

This goal was not allowed to claim a broad RayJoin speedup. The only valid outcomes were:

- byte-equal correctness preserved, and the generic layer is actually used;
- or correctness fails, and the app wiring is rejected;
- plus an honest timing readout.

## Environment

POD:

- Host: `ce489c3fad22`
- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- Worktree: `/root/rtdl_goal4933`
- OptiX headers: `/root/vendor/optix-dev`, tag `v9.0.0`
- CUDA prefix: `/usr/local/cuda`
- NVCC: `/usr/local/cuda/bin/nvcc`

Public sample inputs fetched by `Paper-reproduction-apps/rayjoin-paper/scripts/fetch_public_sample.py`:

- `br_county_clean_25_odyssey_final.txt`, SHA256 `cee9...a0e7`
- `br_soil_ascii_odyssey_final.txt`, SHA256 `525a...0d9f`
- `br_countyXbr_soil_answer.txt`, SHA256 `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

Artifacts copied back to:

`history/internal_docs/goal4933_pod_artifacts/`

## Code Under Test

Generic core API:

- `src/rtdsl/output_assembly.py`
- exported from `src/rtdsl/__init__.py`
- tested by `tests/goal4932_generic_output_assembly_test.py`

RayJoin app wiring:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`

The app now routes final point-line grouping through:

```python
GroupedSequenceAssemblyPlan
assemble_grouped_sequences
```

Final author-compatible text formatting remains app-owned.

## Local And POD Validation

Local:

```text
py -m py_compile src/rtdsl/output_assembly.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py
PYTHONPATH=src py -m unittest tests.goal4932_generic_output_assembly_test
PYTHONPATH=src py -m unittest tests.goal4913_planar_map_workspace_api_test tests.goal4932_generic_output_assembly_test
```

Result:

- `tests.goal4932_generic_output_assembly_test`: 7 tests passed.
- Combined workspace/API test subset: 11 tests passed.

POD:

```text
python3 -m py_compile src/rtdsl/output_assembly.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py
python3 -m unittest tests.goal4932_generic_output_assembly_test
```

Result:

- 7 tests passed on Linux/POD.

POD run:

```text
RAYJOIN_OUT_DIR=Paper-reproduction-apps/rayjoin-paper/_runs/goal4933/rtdl \
OPTIX_PREFIX=/root/vendor/optix-dev \
CUDA_PREFIX=/usr/local/cuda \
NVCC=/usr/local/cuda/bin/nvcc \
bash Paper-reproduction-apps/rayjoin-paper/scripts/run_rtdl_public_sample.sh
```

## Correctness Result

Both Section 5.7 routes remained byte-equal to the public sample answer:

| Route | Byte Equal | Output SHA256 |
|---|---:|---|
| Plain Section 5.7 route | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| Numba/generic-assembly route | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

The Numba/generic route reports:

```json
{
  "generic_output_assembly": {
    "enabled": true,
    "schema": "rtdl.paper_reproduction.rayjoin.generic_output_assembly.v1",
    "input_rows": 673371,
    "valid_rows": 673371,
    "item_rows": 673371,
    "group_count": 64459,
    "group_policy": "skip_empty",
    "dedupe_enabled": false,
    "output_shape": "descriptors_and_items"
  }
}
```

This proves the generic assembly layer is actually on the Section 5.7 app path.

## Timing Result

The timing result is mixed and must not be overclaimed.

| Route | Total elapsed | `output_chain_write_sec` | Byte Equal |
|---|---:|---:|---:|
| Plain Section 5.7 route | 6.901 s | 2.069 s | true |
| Numba/generic-assembly route | 6.612 s | 2.982 s | true |

The total elapsed comparison is not a clean speedup claim, because the two runs used different cache states in the same script. The plain route paid `load_pack_left_sec=0.745s` and `load_pack_right_sec=0.473s`; the Numba/generic route reused the packed cache and paid only `0.006s` and `0.004s`.

The clean writer comparison is worse after current generic wiring:

- Plain writer: `2.069s`
- Numba/generic writer: `2.982s`

Breakdown for the Numba/generic writer:

| Phase | Seconds |
|---|---:|
| `generic_output_assembly_sec` | 0.331 |
| `chain_loop_map0_sec` | 1.266 |
| `chain_loop_map1_sec` | 1.046 |
| `skip_plan_sec` | 0.066 |
| `group_xsects_map0_sec` | 0.007 |
| `group_xsects_map1_sec` | 0.079 |
| `bulk_writelines_sec` | 0.074 |

Interpretation:

- The generic layer itself costs `0.331s`.
- The dominant remaining cost is still app-side Python chain-loop text-line generation: `1.266s + 1.046s`.
- Therefore Goal4933 proves a clean generic boundary, not a performance win.

## Claim Boundary

Authorized:

- A generic host-columnar grouped-sequence assembly API exists.
- It is exported from the public RTDL Python surface.
- It can preserve RayJoin Section 5.7 public-sample byte equality when wired into the app.
- The generic layer is actually used on the app path.

Not authorized:

- No broad RayJoin speedup claim.
- No claim that generic assembly beats the old writer.
- No claim that this closes the RayJoin hot-path gap.
- No full eight-pair Section 5.7 claim.
- No claim about author-program performance.
- No V3/V4 claim.

## What This Teaches

The current generic layer is correct but still too high in the stack to speed up the writer. It groups rows generically, but the expensive RayJoin-specific text-line generation still runs in Python loops.

The next possible step, if authorized, is not more wrapping. It is one of:

1. Stop here and record Goal4933 as `correct_but_not_faster`.
2. Measure whether a generic compiled output backend can own the repeated line-materialization loop without knowing RayJoin semantics.
3. If that backend must know author output-chain semantics, classify it as app-specific and do not put it in RTDL core.

## Exit Label

Recommended label:

`complete_correct_but_not_faster__generic_assembly_wired`
