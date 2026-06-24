# Phoenix V3 M29 Barnes-Hut V2.14 / Current Surface Classification

Date: 2026-06-23
Status: `classified_not_release`

## Result

M29 classifies the v2.14 Barnes-Hut surface as:

`v2_14_has_cpu_fused_or_typed_stream_only`

This means v2.14 has CPU fused force-summary and grouped-vector typed-stream
pieces, but it does not have the current Numba CUDA fused route and does not
have the Phoenix V3 prepared-execution runner route.

M29 therefore authorizes no same-contract V3-over-v2.14 speedup claim for the
current Barnes-Hut Numba CUDA fused runner. There is no equivalent v2.14 current
runner surface to time against.

## Evidence

Local evidence copy:

`docs/rebuild/v3/evidence/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/`

POD evidence path:

`/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/`

Classifier script:

`scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`

POD:

- host: `213.173.108.14`
- port: `11592`
- GPU/driver: `NVIDIA RTX 4000 Ada Generation, 550.127.05`

## Provenance

v2.14 tree:

- path: `/root/rtdl_v3_rebuild_20260620/v2_14`
- git HEAD: `8384a38376567fe518d89721453eb4433de08312`
- VERSION: `v2.14`
- working tree status in evidence: modified
  `scripts/goal2626_benchmark_embree_optix_baseline.py` and untracked `data/`
- relevant-file check: Barnes-Hut app and `src/rtdsl/prepared_execution.py`
  have no diff against the checkout; `git diff -- <relevant files> | wc -c`
  returned `0`

current tree:

- path: `/root/rtdl_v3_rebuild_20260620/current`
- git HEAD: `null`
- VERSION: `v3-rebuild-2026-06-20`
- caveat: current is not a git checkout. This carries forward the M28 caveat
  that the prior evidence remote execution tree records `git_commit: null`.
- M28 local base commit for citation: `8e0f052bffec02507aaf5ed05f75dfe995f39883`

## Surface Matrix

| Surface | v2.14 | Current |
| --- | ---: | ---: |
| `prepared_execution_fused_vector_sum_numba_cuda` | no | yes |
| `fused_frontier_force_sum_bucketized_numba_cuda` | no | yes |
| `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` | no | yes |
| `prepared_aggregate_frontier_weighted_vector_optix` | no | yes |
| `fused_frontier_force_sum_bucketized_cpu` | yes | yes |
| `grouped_vector_sum_typed_stream_plan` | yes | yes |
| `embree_node_coverage_prepared` | yes | yes |
| `optix_node_coverage_prepared` | yes | yes |

## Interpretation

The M28 Barnes-Hut runner/control evidence remains valid as productized V3 trunk
evidence: current runner versus current fused control is parity at `0.999328x`
geomean and the runner preserves internal residency and output equivalence.

M29 adds the v2.14 boundary:

- v2.14 already had useful Barnes-Hut pieces: CPU fused force summary,
  grouped-vector typed stream descriptors, and prepared node-coverage rows.
- v2.14 did not expose the current Numba CUDA fused route.
- v2.14 did not expose the prepared-execution session runner for aggregate-tree
  fused weighted-vector sum.
- Therefore, M29 confirms a V3 surface/capability addition, not a same-contract
  v2.14 speedup.

No fresh timing rows were needed after this classification. Running a v2.14
node-coverage or CPU fused row against the current Numba CUDA runner would mix
different contracts and would create the exact overclaim M28 forbids.

## Carry-Forward Boundaries

The M28 evidence `summary.json` field `runtime_sourced_material_gain: true` is
keyed to historical prepared-OptiX-frontier displacement only. It is not a
current-runner versus current-fused-control material speedup.

The M28 evidence rows use `validation_skipped: true` for serious large
performance rows because per-row CPU/oracle validation is intentionally skipped.
For the M28/M29 freeze, correctness is carried by runner/control contribution
count plus checksum X/Y equivalence at every serious size.

The M28 term "generic" means API-design scope only. It is not a multi-app
coverage claim, and M29 does not broaden it into one.

## Next Step

M30 should select and probe the second Set-A family. The best candidates remain:

- RTDBSCAN resident component/continuation work if the runner overhead and
  component-union path can produce a material runtime-sourced gain;
- RTNN resident graph/partner continuation if it can demonstrate a second
  app-agnostic multi-phase trunk win.

All-app timing remains forbidden until two true Set-A families are accepted.

## Verification

Local:

- `py -3 -m py_compile scripts\v3_phoenix_m29_barnes_hut_surface_classification.py`
- `git diff --check -- scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`
- `py -3 -m unittest tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test`

Result: `43 tests`, `OK`.

POD:

- classifier returned `classified_not_release`
- classifier returned `v2_14_has_cpu_fused_or_typed_stream_only`
- relevant v2.14 tracked files were clean against checkout

## Goal-Level Decision Audit

Decision: stop M29 after surface classification and do not run extra timing
rows.

1. Was I foolish?
   No. The classification proves there is no equivalent v2.14 Numba CUDA fused
   runner surface to time against.

2. If yes, what actions made the decision foolish?
   The foolish action would be to time v2.14 node-coverage or CPU fused rows
   against the current Numba CUDA runner and present that as same-contract
   speedup.

3. Was there another path?
   Yes. Rerun current runner/control timing. That is not needed because M28
   already accepted fresh focused POD evidence and M29 did not find an
   equivalent v2.14 route.

4. Can I now try a different path that truly solves the problem?
   Yes. Move to M30 and seek the second true Set-A runtime-trunk family.

## Non-Authorization

This report authorizes no Phoenix V3 release, no all-app run, no public speedup
claim, no broad V3-over-V2 claim, no RT-core speedup claim, no true-zero-copy
claim, no automatic partner selection, no V4 work, and no embedding work.
