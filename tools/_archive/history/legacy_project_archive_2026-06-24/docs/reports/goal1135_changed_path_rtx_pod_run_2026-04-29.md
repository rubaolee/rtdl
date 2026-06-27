# Goal1135 Changed-Path RTX Pod Run

Date: 2026-04-29

This report records one consolidated RunPod RTX session for the changed-path
Goal1135 app artifacts. It does not authorize public RTX speedup wording,
release, or broad whole-app acceleration claims.

## Environment

- Pod: `root@69.30.85.182 -p 22044`
- Hostname: `1802b89682fb`
- GPU: NVIDIA RTX A5000, 24564 MiB
- Driver: `580.126.09`
- CUDA toolkit used for build: `/usr/local/cuda-12.8`, `nvcc 12.8.93`
- OptiX headers: NVIDIA `optix-dev` tag `v9.0.0` at `/workspace/vendor/optix-dev-9.0.0`
- Source snapshot marker: `21fa036881bf9a0c806f69c15727d87b482ccfcf`
- Runtime env:
  - `PYTHONPATH=src:.`
  - `RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so`
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc`

## Bootstrap

Bootstrap artifact:

- `docs/reports/goal1135_changed_path_rtx_pod/bootstrap_goal1135.json`

Result:

- `make build-optix`: OK
- Focused native OptiX tests: 34 tests OK
- Notes: CUDA 12.8 emitted only the expected deprecated pre-SM75 offline
  compilation warning.

## Results

| Artifact | Scale | Result | Notes |
| --- | ---: | --- | --- |
| `database_analytics_compact_summary.json` | 20,000 copies, 5 iterations | PASS | Prepared compact-summary DB path completed. Warm query median `0.26575445383787155` s; one-shot total `3.7903162809088826` s; native DB counters exported with `0` row-materializing operations. |
| `graph_visibility_edges_gate.json` | 20,000 copies | PASS after dependency repair | First strict run failed because `libgeos_c` was missing for the native CPU/oracle reference build. After installing `libgeos-dev pkg-config`, rerun passed with `strict_pass: true`. |
| `road_hazard_native_summary_count.json` | 20,000 copies | PASS | Native OptiX summary-count gate passed with `strict_pass: true`. |
| `polygon_pair_overlap_phase_gate.json` | 20,000 copies, chunk 20 | PASS | OptiX phase profiler passed in summary mode with analytic-summary validation. |
| `polygon_set_jaccard_phase_gate.json` | 20,000 copies, chunk 20 | PASS | OptiX Jaccard phase profiler passed in summary mode with analytic-summary validation. |
| `hausdorff_threshold_phase_gate.json` | 20,000 copies, 5 iterations | PASS as capability evidence | Oracle parity passed for threshold decision; median OptiX query `0.011092765256762505` s, prepare `1.3375593619421124` s. This remains capability/phase evidence only because the current public speedup path is still blocked by the analytic tiled oracle baseline boundary. |

## Replay Log Files

- `docs/reports/goal1135_changed_path_rtx_pod/logs/database_analytics_compact_summary.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/graph_visibility_edges_gate.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/graph_visibility_edges_gate_rerun.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/road_hazard_native_summary_count.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/polygon_pair_overlap_phase_gate.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/polygon_set_jaccard_phase_gate.log`
- `docs/reports/goal1135_changed_path_rtx_pod/logs/hausdorff_threshold_phase_gate.log`

## Operational Notes

- The user-provided key path `~/.ssh/id_ed25519` was not present in the local
  Codex environment. The session used `~/.ssh/id_ed25519_rtdl_codex`.
- The first `rsync` attempt accidentally included a local virtualenv and tried
  to preserve owners on the pod filesystem. It was stopped, the partial pod
  tree was removed, and the clean sync excluded `.venv*` with `--no-owner
  --no-group`.
- The pod image already had CUDA 12.8, but no OptiX headers. The compatible
  public `optix-dev` tag `v9.0.0` was cloned once under `/workspace/vendor`.
- GEOS was required only for strict reference/oracle builds in the graph gate;
  after installing `libgeos-dev` and `pkg-config`, the same planned graph scale
  passed.

## Boundary

These artifacts are changed-path RTX engineering evidence. Public claims still
require artifact intake, comparable same-semantics baselines where applicable,
phase interpretation, and 2-AI consensus with Codex plus Claude or Gemini.
