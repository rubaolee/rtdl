# Goal5108 - RT-DBSCAN UCI 3DRoad Author-Directional Gate And PTX Blocker

Date: 2026-07-07

## Verdict

```text
author_directional_app_gate_matches_1k_author_payload__rtdl_optix_numba_still_ptx_blocked
```

Goal5108 turns the Goal5107 author contract diagnosis into an executable app
gate and narrows the remaining RTDL OptiX+Numba blocker.

## What Changed

The RT-DBSCAN app runner now supports:

```text
--backend author_directional_cpu_reference
```

Implemented in:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
```

This backend is app-owned. It is not exported from `rtdsl`, not added to RTDL
core, and not described as conventional DBSCAN. Its purpose is to match the
pinned AuthorOfficial call-2 behavior diagnosed in Goal5107:

```text
callNum == 2 && xID > primID
```

## 1K UCI 3DRoad Gate Result

Command:

```text
py Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py \
  --input Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/uci_3droad_1k_author_2d_zero_z.csv \
  --epsilon 0.05 \
  --min-points 100 \
  --backend author_directional_cpu_reference \
  --author-payload Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl \
  --summary Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_directional_gate_summary.json
```

Result:

```text
matched=true
signature_matched=true
component_partition_matched=true
core_flags_matched=true
rtdl_signature={core_count=329, component_count=3, component_sizes=[90,168,181], noise_count=561}
author_signature={core_count=329, component_count=3, component_sizes=[90,168,181], noise_count=561}
```

The same clean author payload still mismatches the conventional CPU reference:

```text
conventional_cpu_signature={core_count=329, component_count=3, component_sizes=[102,168,181], noise_count=549}
author_signature={core_count=329, component_count=3, component_sizes=[90,168,181], noise_count=561}
```

This makes the comparator distinction executable:

```text
conventional DBSCAN reference != pinned AuthorOfficial contract
author_directional_cpu_reference == pinned AuthorOfficial contract on 1K UCI 3DRoad
```

## RTDL Core Boundary

The author-directional backend is intentionally app-owned:

```text
native_engine_row_contract=not_called_app_side_author_contract_reference_only
component_partition_contract=app_side_author_directional_border_assignment_reference_3d
border_assignment_policy=author_call2_xid_greater_than_primid_only
rt_core_accelerated=false
```

No new RTDL core primitive or public `rtdsl` export was added for this author
contract. That is deliberate: `xID > primID` is a pinned-author comparator
detail, not a generic RTDL spatial language semantic.

## POD RTDL OptiX+Numba Blocker

Goal5106 reported:

```text
CUDA_ERROR_UNSUPPORTED_PTX_VERSION
ptxas application ptx input ... Unsupported .version 8.7; current version is '8.4'
```

Goal5108 narrowed the blocker with minimal POD probes.

POD environment:

```text
python=3.12.3
numba=0.66.0
llvmlite=0.48.0
gpu=NVIDIA RTX 4000 Ada Generation
driver=550.127.05
driver CUDA version=12.4
/usr/bin/ptxas=CUDA 12.0, supports PTX 8.4
/usr/local/cuda-12.8/bin/ptxas=CUDA 12.8
/usr/local/cuda/nvvm=CUDA 12.8 NVVM
```

Probes:

- A minimal Numba CUDA kernel fails with `CUDA_ERROR_UNSUPPORTED_PTX_VERSION`.
- Setting `PATH`, `CUDA_HOME`, and `LD_LIBRARY_PATH` to CUDA 12.8 does not fix
  it, because the CUDA driver linker still rejects PTX 8.7.
- `NUMBA_FORCE_CUDA_CC=8.9` does not fix it.
- `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1` fails because the required
  `ptxcompiler` / `cubinlinker` modules are not available in this environment.
- An isolated venv with `numba==0.61.2` still emits PTX 8.7 because the active
  NVVM path is CUDA 12.8.
- Installing `cuda-python==12.8.0` in that venv does not satisfy Numba's missing
  `ptxcompiler` / `cubinlinker` requirement.
- CuPy is not installed on the POD, so the existing CuPy alternatives are not
  currently available as a drop-in route.

Conclusion:

```text
The RTDL OptiX+Numba 3DRoad run is blocked by a POD CUDA/Numba/PTX toolchain
mismatch, not by the author-directional comparator itself.
```

## Tests

Command:

```text
py -m unittest tests.goal5108_rt_dbscan_author_directional_gate_test tests.goal5107_rt_dbscan_uci_3droad_contract_analysis_test tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test tests.goal5101_component_partition_helpers_test tests.goal5104_rt_dbscan_author_warm_loop_runner_test
```

Result:

```text
Ran 16 tests in 1.125s
OK
```

Test coverage:

- conventional CPU reference still mismatches the clean 1K author payload;
- author-directional app backend matches the clean 1K author payload;
- author-directional backend is not exported from RTDL core;
- prior Goal5107 contract analysis and bounded partition helpers remain green.

## What This Proves

Proved:

- The 1K UCI 3DRoad same-source clean AuthorOfficial payload now has an
  executable app-side comparator gate.
- The app-side author-directional comparator matches author partition,
  signature, and core flags exactly.
- The conventional CPU DBSCAN reference is not the right comparator for this
  pinned author binary on this input.
- The RTDL OptiX+Numba failure is a reproducible toolchain blocker on the
  current POD.

Not proved:

- RTDL OptiX+Numba correctness on UCI 3DRoad;
- exact paper input reproduction;
- paper performance or author parity;
- a generic RTDL author-directional DBSCAN primitive;
- conventional DBSCAN equivalence.

## Authorized Claim

Allowed:

```text
Goal5108 added an app-owned author-directional comparator backend and matched
the clean 1K UCI 3DRoad AuthorOfficial payload exactly. The RTDL OptiX+Numba
route remains blocked on the current POD by a CUDA/PTX toolchain mismatch.
```

Forbidden:

```text
RTDL matches AuthorOfficial on UCI 3DRoad.
RTDL reproduces the exact RT-DBSCAN paper datasets.
The author-directional backend is a generic RTDL primitive.
The PTX blocker is a correctness failure.
Performance has been measured or improved.
```

## Next Recommended Goal

Goal5109 should choose one concrete RTDL execution route:

1. Fix the POD CUDA/Numba toolchain so a minimal Numba CUDA kernel succeeds,
   then run `optix_numba_component_signature` on the 1K UCI 3DRoad candidate
   against the author-directional comparator.
2. Install and validate CuPy on the POD, then attempt an existing
   OptiX+CuPy/partition route if it can produce point labels compatible with
   the same comparator.
3. If neither GPU partner route is feasible on this POD, close the exact-source
   line at "author comparator ready / RTDL route environment-blocked" and move
   to a POD image with CUDA driver/toolchain alignment.

Any Goal5109 success must report:

```text
same_source_public_candidate=true
exact_paper_input=false
author_directional_comparator=true
rtdl_optix_or_gpu_partner_matched=true/false
```
