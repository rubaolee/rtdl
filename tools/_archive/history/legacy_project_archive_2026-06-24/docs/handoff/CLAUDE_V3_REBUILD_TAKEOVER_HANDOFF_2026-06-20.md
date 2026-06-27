# Claude V3 Rebuild Takeover Handoff

Date: 2026-06-20.

Audience: Claude or any replacement primary agent taking over V3.

Status: V3-only repair-pass handoff. Do not resume V4.

Superseded current entrypoint:

`docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`

Use the superseding handoff first. This file is preserved for repair-pass
history and pod/setup context.

## Read This First

The user lost trust because V3/V4 were over-promoted before fresh evidence
proved the release surface. Do not defend the old release surface. Do not talk
about V4. The current job is V3 only.

Current authority:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_design_intent_and_v2x_problem_statement_2026-06-20.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json`
- `docs/rebuild/v3/v3_gpu_environment_gate_2026-06-20.md`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`

Current decision:

```text
V3 should continue. V3 is not release-authorized yet.
```

The repaired benchmark evidence is strong enough to rebuild the public V3 user
surface, but public docs/tutorials/setup instructions are not finished.

## User Mandate

The user wants V3 to answer:

```text
Why does V3 exist, what v2.x user problem does it solve, and does current V3
actually solve it with serious pod evidence?
```

If the evidence says V3 does not solve the problem, do not polish language.
Recommend repair or rebuild.

Non-negotiable constraints:

- V3 only. Do not drift into V4.
- Performance and usability are first-class release requirements.
- Do not use vague language to hide failed or missing evidence.
- Do not let old docs mislead users.
- Do not leave long silent gaps while testing.
- For goal-level decisions, answer the four-question audit:
  1. Did I make a foolish decision?
  2. If yes, what actions made it foolish?
  3. Was there another path that avoided getting stuck?
  4. Can I now try a different path that truly solves the problem?

## What V3 Must Prove

V3 exists to turn RTDL from a capable research line into a usable Python-hosted
language release.

The V2.x problems V3 must fix:

1. Fragmented language story.
2. Unclear current truth because old reports/tutorials were too close to users.
3. Backend and partner uncertainty.
4. Evidence not tied tightly enough to claims.
5. Too much app-author burden for serious workloads.

V3 is acceptable only if a serious user can:

1. read one front door and know what RTDL solves;
2. run one current tutorial without history archaeology;
3. choose supported backends/partners without guessing;
4. inspect release-candidate benchmark rows;
5. reproduce evidence behind any performance wording;
6. know what is not ready.

## Current Repository State

Old V3/V4 user-facing material has been depublished from current front doors
and preserved under:

```text
docs/history/quarantine_v3_v4_reset_2026-06-20/
```

Important active files:

- `README.md`: reset to V3 rebuild only.
- `docs/README.md`: reset to V3 rebuild only.
- `tutorials/README.md`: reset; no current tutorial release claim.
- `examples/README.md`: reset; examples are rebuild inventory only.
- `docs/public_documentation_map.md`: current docs map reset.
- `docs/learn/current_claim_boundaries.md`: current claim boundary.
- `docs/rebuild/v3/README.md`: main V3 rebuild control.
- `docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md`:
  current repair-pass evidence report.
- `docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json`:
  machine-readable app classification.
- `docs/rebuild/v3/v3_gpu_environment_gate_2026-06-20.md`:
  GPU Python dependency gate.
- `tests/v3_rebuild_evidence_classification_test.py`: guards current repaired
  evidence counts and claim blocks.
- `tests/v3_rebuild_reset_test.py`: guards reset state.
- `tests/v3_rebuild_spatial_rayjoin_route_test.py`: guards the Spatial RayJoin
  route repair.
- `scripts/run_test_matrix.py`: has `v3_rebuild` group.
- `scripts/rtdl_source_tree_doctor.py`: V3 rebuild doctor.
- `VERSION`: `v3-rebuild-2026-06-20`.

Do not restore old V3/V4 release wording unless fresh evidence and review
justify a new current user surface.

## Local Gates Passed

From Windows workspace
`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`:

```powershell
py -3 scripts\run_test_matrix.py --group v3_rebuild
py -3 scripts\rtdl_source_tree_doctor.py --json --run-smoke
```

Latest result:

- `v3_rebuild`: 14 tests OK.
- source tree doctor: required checks OK.
- Windows warnings are optional local CUDA/OptiX/CuPy/Numba warnings only.

## Pod Access

Use the existing project key. Do not waste time looking for another key.

```powershell
ssh -o BatchMode=yes -o StrictHostKeyChecking=no `
  -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod `
  -p 11592 root@213.173.108.14
```

Pod facts:

- host: `213.173.108.14:11592`
- GPU: NVIDIA RTX 4000 Ada Generation, 20475 MiB
- driver: `550.127.05`
- NVIDIA-SMI CUDA capability: `12.4`
- Python: 3.12.3
- OptiX SDK headers: `/workspace/vendor/optix-dev-8.0.0/include/optix.h`

Pod workspace:

```text
/root/rtdl_v3_rebuild_20260620
```

Subtrees:

- `current`: uploaded current V3 rebuild worktree.
- `v2_14`: local bundle clone checked out at tag `v2.14`, commit
  `8384a38376567fe518d89721453eb4433de08312`.
- `.venv`: benchmark Python environment.

Native libraries built successfully for both trees:

- `current/build/librtdl_embree.so`
- `current/build/librtdl_optix.so`
- `v2_14/build/librtdl_embree.so`
- `v2_14/build/librtdl_optix.so`

Required build flag:

```bash
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
```

## Repaired Pod Evidence

Initial V2.14 comparison:

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207
local:  docs/rebuild/v3/evidence/v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207
```

Repair Pass 1 current-side artifacts:

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal2626_clean_env_20260620_055523
local:  docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal2636_full_clean_20260620_060726
local:  docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal3828_full_clean_20260620_060412
local:  docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_20260620_061058
local:  docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_script_20260620_062113
local:  docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113
```

Clean current-side results:

| Suite | Result |
| --- | ---: |
| `goal2626_standard_all_rows` | 22 ok / 0 failed |
| `goal2636_standard_all_rows` | 28 ok / 0 failed |
| `goal3828_full_clean` | 10 pass / 0 fail |
| GPU Python environment gate | pass |

The initial comparison still matters: V3 does not broadly prove raw speed over
V2.14 on every shared successful row. The strongest V3-over-V2.14 point is
route health and runability, especially triangle-counting OptiX rows that pass
in current V3 where matching v2.14 rows fail.

## Repairs Already Made

Spatial RayJoin:

- `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `run_rayjoin_suite` now prepares the left-id count payload for the LSI count
  route when the prepared OptiX all-workload route needs it.
- The previously failing prepared all-workload row now completes.
- The standard all-workload row is still not an OptiX speedup claim.

RayDB:

- PyTorch CUDA installed in the pod venv: `torch==2.6.0+cu124`.
- RayDB partner-resident count/sum rows now pass.

Numba:

- `nvidia-cuda-nvcc-cu12==12.4.131` installed.
- Required environment:

```bash
export NUMBA_CUDA_PREFIX=/root/rtdl_v3_rebuild_20260620/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

CuPy:

- `cupy-cuda12x==14.1.1`.
- `nvidia-cuda-nvrtc-cu12==12.9.86`.
- `nvidia-cuda-runtime-cu12==12.9.79`.
- This fixed the CuPy/NVRTC compile failure after PyTorch was installed.
- Reusable checker: `PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty`.

Environment caveat:

- `cuda-bindings` still warns that it was built for CUDA major 13 while the
  driver supports CUDA 12. The smoke and benchmark rows pass, but setup docs
  should keep this warning visible until the dependency set is quieter.

## App Classification Summary

Machine-readable source:

```text
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
```

Current summary:

| App | Classification |
| --- | --- |
| `hausdorff_xhd` | release-candidate row set |
| `spatial_rayjoin` | split-route release candidate |
| `rt_dbscan` | release-candidate row set |
| `robot_collision` | release-candidate row set |
| `raydb_style` | release-candidate with dependency gate |
| `barnes_hut` | release-candidate row set |
| `librts_spatial_index` | no OptiX speed claim |
| `rtnn` | mixed release candidate |
| `triangle_counting` | release-candidate row set |
| `contact_manifold` | release-candidate row set |

All `public_claim_allowed_now` flags remain false until the public docs and
tutorials are rebuilt and reviewed.

## Immediate Next Steps

1. Rebuild public V3 docs from the repaired artifacts only.
2. Write a setup page that reproduces the GPU Python environment gate.
3. Create tutorials that teach the passing rows and explicitly mark mixed or
   Embree-better routes.
4. Add a release gate that fails if public docs claim V3 release readiness or
   speedups without exact artifact references.
5. Ask Claude or another reviewer to audit the repaired V3 evidence and public
   docs before any release declaration.

Progress after this handoff was first drafted:

- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md` now exists.
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md` now exists.
- `tutorials/current/` now contains a rebuild learner path guarded by tests.
- `scripts/v3_gpu_python_env_gate.py` now exists and has a pod-passing
  script-backed artifact.
- Second-machine probe for `root@192.168.1.20` was attempted with default SSH
  auth and with `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`; both
  returned `Permission denied (publickey,password)`.

## Things Not To Do

- Do not resume V4.
- Do not cite quarantined old release docs as current truth.
- Do not say V3 is released.
- Do not claim broad V3 speedup over V2.x.
- Do not claim every `examples/current` app is user-ready.
- Do not treat wrapper elapsed time as hot-path performance unless the row
  explicitly supports that interpretation.
- Do not hide environment gates for RayDB, CuPy, Torch, or Numba.
- Do not republish tutorials until rows are classified and user examples are
  rebuilt from passing evidence.

## Suggested Opening Message To The User

```text
I am taking over V3 only. The current benchmark repair pass produced clean
current-side pod evidence: goal2626 is 22/22, goal2636 is 28/28, goal3828 is
10/10, and the GPU Python environment gate passes. I will not call V3 released
until the public docs, setup path, and tutorials are rebuilt from those exact
artifacts and reviewed.
```

## Current Goal-Level Decision Audit

Decision: continue V3 from repaired evidence, not old release wording.

1. Did the previous path include foolish decisions?

   Yes.

2. What made them foolish?

   V3/V4 scope was mixed, old docs were trusted too much, and benchmark evidence
   was not made the first-class release gate early enough.

3. Was there another path?

   Yes. Quarantine old material, reconstruct the V3 user problem, run pod
   evidence, repair failed rows, and only then rebuild release docs.

4. What different path is now available?

   Continue from the repaired artifacts, rebuild the user surface row by row,
   and keep release authorization false until review confirms that public
   claims match the evidence.
