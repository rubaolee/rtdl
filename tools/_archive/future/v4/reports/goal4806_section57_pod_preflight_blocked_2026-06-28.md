# Goal4806 Section 5.7 POD Preflight Blocked Record

Date: 2026-06-28

## Scope

Goal4806 asks for a V4.0 RayJoin Section 5.7 Polygon Overlay paper-reproduction route using Numba as the partner, including comparison against the RayJoin author implementation and the existing V2.14 exact-suite route.

This record captures the RTX POD state after local implementation and validation work. It is not performance evidence and does not complete Goal4806.

## POD

- Host: `root@157.157.221.29 -p 23132`
- Key used: `~/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
- Working tree transferred as a minimal source bundle to `/workspace/rtdl_goal4806_fast_min`

## Completed On POD

1. Verified the POD has RT-core-capable NVIDIA hardware.
2. Ran the Goal4806 Linux/POD test subset after transferring the required source files.
3. Fixed the POD Python-partner environment by creating a local venv in `/tmp/rtdl_goal4806_venv`.
4. Installed and verified:
   - `numba 0.65.1`, `cuda.is_available() == True`
   - `cupy 14.1.1`, device count `1`
5. Re-ran Section 5.7 preflight with the venv; the Numba blocker is cleared.

## Tests

Command:

```bash
cd /workspace/rtdl_goal4806_fast_min
export PYTHONPATH=src:.
python3 -m unittest \
  tests.v4_goal4806_rayjoin_section57_overlay_matrix_digest_test \
  tests.v4_goal4806_rayjoin_numba_candidate_probe_test \
  tests.v4_goal4806_rayjoin_section57_pod_setup_test \
  tests.v4_goal4806_rayjoin_section57_pod_runbook_test \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test
```

Result:

```text
Ran 21 tests in 41.860s
OK
```

## Current Preflight Result

Evidence: `tools/_archive/future/v4/evidence/goal4806_section57_pod_preflight_2026-06-28/section57_preflight_after_numba.json`

Cleared:

- RT-core GPU present.
- Numba CUDA available.
- V4 Section 5.7 device-column components are statically declared.

Remaining blockers:

- `missing_exact_section57_cdb_inputs`
- `missing_rayjoin_author_binaries`

## Author-Code Build Attempt

Author repository:

- `https://github.com/pwrliang/RayJoin`
- commit `02bf6220d6d20b04af77ee20364eced75cc029c9`

Resolved:

- CUDA compiler path: `/usr/local/cuda-12.8/bin/nvcc`
- CUDA architecture: `89`
- `libgflags-dev`
- `libgoogle-glog-dev`

Blocking error:

```text
OptiX headers (optix.h and friends) not found.
OptiX_INCLUDE-NOTFOUND
```

Evidence: `tools/_archive/future/v4/evidence/goal4806_section57_pod_preflight_2026-06-28/rayjoin_author_cmake_cuda_path.log`

Interpretation:

The author-code build cannot produce `query_exec` or `polyover_exec` on this POD without the NVIDIA OptiX SDK headers. This is not a CUDA, gflags, glog, or CMake-path issue; those were cleared.

## Dataset Attempt

The RayJoin README's preprocessed-data Dryad share URL was checked from the POD:

`https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA`

Observed result:

- HTTP 301 to `https://datadryad.org/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA`
- HTTP 302 to `/404`
- HTTP 404 final page

Evidence: `tools/_archive/future/v4/evidence/goal4806_section57_pod_preflight_2026-06-28/rayjoin_dryad_headers.txt`

Interpretation:

The exact Section 5.7 CDB dataset is not currently available from the README share link and is not present on the POD under `/workspace/rayjoin_section57_cdb`.

## Claim Boundary

No Section 5.7 performance result exists yet.

No V4+Numba speedup, correctness, paper-reproduction, or author-code comparison claim is authorized from this record.

## Next Unblockers

To run the serious Section 5.7 matrix, the POD needs:

1. NVIDIA OptiX SDK 8 headers installed or mounted, then rebuild RayJoin author binaries:
   - `query_exec`
   - `polyover_exec`
2. Exact RayJoin Section 5.7 CDB inputs in the expected layout:
   - `/workspace/rayjoin_section57_cdb/point_cdb/...`
3. Then run:

```bash
cd /workspace/rtdl_goal4806_fast_min
export PYTHONPATH=src:.
/tmp/rtdl_goal4806_venv/bin/python examples/paper_reproduction/rayjoin.py \
  --section57-run \
  --implementations author_rt,rtdl_optix,rtdl_embree,v4_numba \
  --dataset-root /workspace/rayjoin_section57_cdb \
  --output-dir artifacts/rayjoin_section57 \
  --query-exec /workspace/RayJoin_fresh/release/bin/query_exec \
  --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec \
  --v4-numba-section57-device-columns-ready \
  --assemble-overlay-output \
  --author-warmup 5 \
  --author-repeat 5 \
  --rtdl-warmup 1 \
  --rtdl-repeat 3
```
