# Goal1057 RTX A5000 Cloud Execution Log

Date: 2026-04-28

## Boundary

This report records one RunPod RTX A5000 artifact collection session for the
post-Goal1048 RTX readiness batch. It is evidence for same-semantics review.
It does not authorize release, public speedup wording, or broad whole-app RTX
claims.

## Environment

| Item | Value |
| --- | --- |
| Remote host | `194.68.245.156:22153` |
| Remote workspace | `/workspace/rtdl_python_only` |
| Source commit | `21fa036881bf9a0c806f69c15727d87b482ccfcf` |
| GPU | `NVIDIA RTX A5000` |
| Driver | `565.57.01` |
| GPU memory | `24564 MiB` |
| CUDA toolkit | `/usr/local/cuda-12.4`, `nvcc V12.4.131` |
| OptiX headers | `/workspace/vendor/optix-dev-8.0.0` |
| Built native library | `build/librtdl_optix.so` |

The first remote staging attempt in the prior session used a generic tar copy
and produced an incomplete tree. This run replaced it with a tracked-only
`git archive` tarball before executing claim-sensitive commands.

## Commands

The remote tree was staged from a local tracked-only archive:

```bash
git archive --format=tar.gz -o /tmp/rtdl_goal1053_21fa036.tar.gz HEAD
scp -P 22153 -i ~/.ssh/id_ed25519_rtdl_codex \
  /tmp/rtdl_goal1053_21fa036.tar.gz \
  root@194.68.245.156:/workspace/rtdl_goal1053_21fa036.tar.gz
```

The pod tree was rebuilt and verified:

```bash
rm -rf /workspace/rtdl_python_only
mkdir -p /workspace/rtdl_python_only
tar -xzf /workspace/rtdl_goal1053_21fa036.tar.gz -C /workspace/rtdl_python_only
cd /workspace/rtdl_python_only
printf "%s\n" "21fa036881bf9a0c806f69c15727d87b482ccfcf" > .rtdl_source_commit
find tests -maxdepth 1 -type f | wc -l
```

Verification result: `472` top-level test files, Goal760 test present, Goal1053
runner present.

The OptiX library was built and the Goal1053 batch was started:

```bash
export PYTHONPATH=src:.
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_SOURCE_COMMIT=$(cat .rtdl_source_commit)
make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX" NVCC="$NVCC"
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
bash scripts/goal1053_post_goal1048_cloud_batch_runner.sh
```

The first batch pass stopped at the graph gate because the pod image did not
include GEOS development libraries needed by the native CPU/oracle build:

```text
/usr/bin/ld: cannot find -lgeos_c: No such file or directory
```

The pod was remediated with:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config
```

After remediation, commands 5 through 11 were resumed individually. All resumed
steps returned `rc=0`; the exact resume status is saved in
`docs/reports/goal1052_post_goal1048_cloud_batch/manual_resume_status.txt`.

## Artifact Results

| Artifact | Status | Key Result |
| --- | --- | --- |
| `goal763_rtx_cloud_bootstrap_check.json` | `ok` | OptiX built; focused native OptiX tests ran `34` tests and passed. |
| `coverage_threshold_prepared.json` | present | Facility coverage threshold matched oracle; median OptiX query `0.00121 s`. |
| `prepared_pose_flags.json` | validated | Robot pose flags matched oracle; median warm query `0.00299 s`; oracle validation dominated total time. |
| `prepared_db_session_sales_risk.json` | candidate | DB compact-summary session `ok`; median warm query `0.1017 s`; native DB traversal total `0.0827 s`. |
| `prepared_db_session_regional_dashboard.json` | candidate | DB compact-summary session `ok`; median warm query `0.1384 s`; native DB traversal total `0.1190 s`. |
| `graph_visibility_edges_gate.json` | candidate | Strict pass after GEOS install; visibility any-hit, native graph-ray BFS, and native graph-ray triangle count all matched analytic summaries. |
| `prepared_count_summary.json` | candidate | Event hotspot scalar summary produced OptiX result with `120000` events and `99999` hotspots. |
| `road_hazard_native_summary_gate.json` | candidate | Strict pass for prepared segment/polygon OptiX summary gate. |
| `polygon_pair_overlap_optix_native_assisted_phase_gate.json` | candidate | Pass; OptiX candidate discovery `2.407 s`, native exact continuation `1.770 s`. |
| `polygon_set_jaccard_optix_native_assisted_phase_gate.json` | candidate | Pass; OptiX candidate discovery `2.614 s`, native exact continuation `3.177 s`. |
| `directed_threshold_prepared.json` | candidate | Hausdorff threshold matched oracle; median OptiX query `0.00392 s`. |
| `node_coverage_prepared.json` | candidate | Barnes-Hut node coverage matched oracle; median OptiX query `0.00178 s`. |

## Local Intake

Artifacts were copied back to:

```text
docs/reports/goal1052_post_goal1048_cloud_batch/
```

The local intake command passed:

```bash
PYTHONPATH=src:. python3 scripts/goal1056_post_goal1048_artifact_intake.py
```

Result:

```text
overall_status: ready_for_same_semantics_review
expected artifacts: 11
present artifacts: 11
missing artifacts: 0
diagnostic validated: 2
blocked rows: 0
public speedup claims authorized: 0
```

Focused local validation also passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1056_post_goal1048_artifact_intake_test \
  tests.goal1053_post_goal1048_cloud_batch_runner_test \
  tests.goal1052_post_goal1048_cloud_batch_manifest_test
```

Result: `14` tests passed.

## Review Status

This run moved the Goal1052 artifact set from "needs cloud run" to
`ready_for_same_semantics_review`. The next required step is a bounded
same-semantics review of the nine candidate artifacts, followed by the required
2+ AI consensus record before any goal closure.
