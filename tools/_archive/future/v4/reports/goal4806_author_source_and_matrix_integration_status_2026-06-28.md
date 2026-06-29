# Goal4806 RayJoin Section 5.7 Author Source And Matrix Integration Status

Date: 2026-06-28

## Status

Goal4806 is not complete as a full paper-reproduction result. The current
progress is that the V4+Numba auto-primitive planner is now wired into the
Section 5.7 matrix runner, so the same evidence surface can report:

1. `author_rt`
2. `rtdl_optix`
3. `rtdl_embree`
4. `v4_numba`

The remaining blocker is external execution state: the real Section 5.7 CDB
inputs, RayJoin author binaries, Numba CUDA, and an RT-core NVIDIA machine must
be present for correctness and performance comparison. The V4+Numba route also
requires Section 5.7 device-resident candidate/refinement columns. Static source
inspection now finds the required segment-pair, closed-shape relation-status,
and Numba continuation components, but the end-to-end Section 5.7 composition
still needs POD validation before any performance claim.

## Author Code Source

Author repository:

```text
https://github.com/pwrliang/RayJoin
```

Local Linux source probe:

```text
machine: 192.168.1.20
clone path: /tmp/RayJoin_goal4806_src
author commit: 02bf6220d6d20b04af77ee20364eced75cc029c9
```

The author README states that release builds generate:

```text
query_exec
polyover_exec
```

under the build directory's `bin` path. Those are the required author-code
performance and correctness baseline binaries for Section 5.7.

## Dataset Source

The author README points to the RayJoin preprocessed dataset share:

```text
https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA
```

Probe result from local Linux on 2026-06-28:

```text
HTTP 404 for the share URL
```

This means the project cannot honestly claim full Section 5.7 reproduction from
that link alone. The exact CDB files must be supplied separately or regenerated
from the same source datasets under an explicitly labeled
`same_source_regenerated_cdb` provenance.

## Local Linux Build Probe

Probe command was run on `192.168.1.20` after cloning the author repository.

Environment:

```text
GPU: NVIDIA GeForce GTX 1070
CUDA compiler: /usr/bin/nvcc, CUDA 12.0
cmake: present
```

Build result:

```text
RayJoin source cloned successfully.
CMake found CUDA.
CMake failed before producing query_exec/polyover_exec.
Missing: OptiX headers, glog, gflags.
Hardware: GTX 1070, not an RT-core GPU.
```

Conclusion: local Linux is useful for source/build-contract probing, but it is
not a valid final RT-core performance machine for Goal4806.

## Matrix Integration Evidence

New matrix evidence directory:

```text
tools/_archive/future/v4/evidence/goal4806_section57_matrix_with_v4_numba_2026-06-28
```

Generated files:

```text
run_v4_numba.json
summary_v4_numba.json
summary_v4_numba.md
section57_overlay_<pair>_v4_numba.json
```

The focused matrix run used:

```bash
py -3 examples\paper_reproduction\rayjoin.py --section57-run \
  --allow-missing-inputs \
  --implementations v4_numba \
  --dataset-root data\rayjoin_section57_cdb \
  --output-dir tools\_archive\future\v4\evidence\goal4806_section57_matrix_with_v4_numba_2026-06-28 \
  --query-exec C:\workspace\RayJoin_fresh\release\bin\query_exec \
  --polyover-exec C:\workspace\RayJoin_fresh\release\bin\polyover_exec \
  --run-json tools\_archive\future\v4\evidence\goal4806_section57_matrix_with_v4_numba_2026-06-28\run_v4_numba.json \
  --summary-json tools\_archive\future\v4\evidence\goal4806_section57_matrix_with_v4_numba_2026-06-28\summary_v4_numba.json \
  --summary-md tools\_archive\future\v4\evidence\goal4806_section57_matrix_with_v4_numba_2026-06-28\summary_v4_numba.md \
  --v4-numba-skip-runtime-probe
```

Observed result:

```text
attempts: 8
implementations: v4_numba
attempt status: completed
overlay pairs complete: 0/8
V4+Numba status: blocked_missing_inputs
```

This is correct for the current workspace because the exact Section 5.7 inputs
are not present. It is not a performance result.

## Preflight Evidence

New setup artifact:

```text
tools/_archive/future/v4/evidence/goal4806_section57_pod_setup_2026-06-28.json
```

New preflight artifact:

```text
tools/_archive/future/v4/evidence/goal4806_section57_preflight_2026-06-28.json
```

Observed local blockers:

```text
missing_author_source
missing_exact_section57_cdb_inputs
missing_rayjoin_author_binaries
rt_core_gpu_not_detected
numba_cuda_unavailable
```

Observed device-column status:

```text
static_components_declared: true
end_to_end_composition_status: components_present_pod_validation_required
performance_evidence_status: not_measured
```

This means the current local stop point is not a missing tutorial or wrapper. It
is the need for a real RT-core POD with exact Section 5.7 inputs, author
binaries, and Numba CUDA to validate the route and measure performance.

## Code Changes

The Section 5.7 matrix runner now recognizes `v4_numba`:

```text
scripts/rayjoin_section57_overlay_matrix.py
```

The public paper-reproduction wrapper forwards it by default:

```text
examples/paper_reproduction/rayjoin.py
```

The V4+Numba semantic planner remains here:

```text
src/rtdsl/rayjoin_numba_auto_planner.py
```

The POD runbook now wraps the full preflight/plan/run sequence:

```text
scripts/rayjoin_section57_pod_setup.py
scripts/rayjoin_section57_pod_runbook.py
```

The setup script reports author-source build dependencies, exact input coverage,
author binary presence, and the next runbook command. The runbook writes:

```text
section57_pod_runbook.json
section57_preflight.json
section57_overlay_plan.json
section57_overlay_run.json
section57_overlay_summary.json
section57_overlay_summary.md
```

The runbook refuses a real performance run when preflight is blocked. It can
still be used with `--preflight-only` or `--dry-run` for non-POD validation.

The planner now refuses to mark candidates as measurable unless exact inputs,
Numba CUDA, and a Section 5.7 device-column route are all present. With inputs
and Numba available but without the device-column route, candidates are labeled:

```text
blocked_missing_section57_device_columns
```

The status note now documents the unified four-column matrix:

```text
docs/research/rayjoin/rayjoin_section57_polygon_overlay_v4_workload_status.md
```

## Verification

Tests run:

```bash
py -3 -m unittest \
tests.v4_goal4806_rayjoin_section57_pod_runbook_test \
tests.v4_goal4806_rayjoin_section57_pod_setup_test \
tests.goal4374_rayjoin_exact_paper_suite_test \
tests.v4_rayjoin_section57_public_entry_test \
tests.v4_goal4806_rayjoin_numba_auto_planner_test
```

Result:

```text
Ran 15 focused setup/runbook/planner tests in 24.281s
OK
```

## Decision Audit

1. Was the matrix-integration decision foolish?

   No. Keeping V4+Numba in a separate evidence file would preserve a split
   surface and make author/V2/V4 comparison weaker.

2. What action would have made it foolish?

   Treating a standalone planner JSON as a paper-reproduction comparison, or
   claiming performance while the exact inputs and author binaries are absent.

3. Was there another path?

   Yes: wait for the pod and only run the old three-column matrix. That would
   delay useful integration and still leave V4+Numba outside the main evidence
   table.

4. Can we solve the real problem by taking a different path?

   Yes. The real path is now: provide exact CDB inputs and author binaries on an
   RT-core pod, run the four-column matrix, then compare correctness and timing.

## Next Required Execution

On an RT-core pod with exact inputs and author binaries:

```bash
python3 scripts/rayjoin_section57_pod_setup.py \
  --author-root /workspace/RayJoin_fresh \
  --dataset-root /path/to/rayjoin_section57_cdb \
  --output-dir /path/to/goal4806_section57_full_run \
  --output-json /path/to/goal4806_section57_full_run/section57_pod_setup.json

python3 scripts/rayjoin_section57_pod_runbook.py \
  --dataset-root /path/to/rayjoin_section57_cdb \
  --query-exec /path/to/query_exec \
  --polyover-exec /path/to/polyover_exec \
  --output-dir /path/to/goal4806_section57_full_run \
  --author-warmup 5 --author-repeat 5 \
  --rtdl-warmup 1 --rtdl-repeat 3
```

The result is release-usable only if:

- all eight overlay pairs are present;
- author code runs locally;
- V2.14 exact-suite route and V4+Numba route use the same pair selection;
- V4+Numba consumes Section 5.7 candidate/refinement device columns rather than
  host-materialized overlay rows;
- correctness is topology/geometry-aware, not row-count-only;
- timings are recorded for author code, V2.14 exact-suite route, and V4+Numba;
- any missing item remains explicitly blocked rather than converted into a
  claim.
