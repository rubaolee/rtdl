# Goal1177 Live Pod Goal1176/Goal1170 Recovery Intake Report

Date: 2026-04-30

## Verdict

Engineering verdict: `ACCEPT_FOR_EXTERNAL_REVIEW_INPUT`.

Public wording verdict: `NOT_AUTHORIZED`.

The live RTX A5000 pod produced all eight Goal1170 artifacts and the local intake accepted them. The run is not silently treated as a perfect first-pass executor run: the first Goal1176 executor attempt failed because the staged archive intentionally excluded generated Goal1170 manifest files. The source tree was then remediated on the same extracted clean archive by regenerating the manifest and rerunning `scripts/goal1170_clean_source_rtx_batch_runner.sh`. The local Goal1176 executor has been patched and tested so future pod runs regenerate the manifest before the OptiX build and batch runner.

## Pod And Source Evidence

| Item | Value |
| --- | --- |
| Pod SSH endpoint used | `root@69.30.85.195 -p 22020` |
| Pod hostname | `7fca3a74fa7c` |
| GPU | `NVIDIA RTX A5000`, 24564 MiB VRAM |
| Driver / CUDA | NVIDIA driver `580.126.09`, CUDA `13.0` |
| Staged archive SHA256 | `e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37` |
| Synthetic git commit inside pod | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |
| Runtime source marker | `goal1175-archive-e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37` |
| Result archive | `docs/reports/goal1176_live_pod_2026-04-30/goal1176_goal1170_results_after_manifest_rerun.tgz` |
| Result archive SHA256 | `40a579346bddb3b1c848a48e8b740ea5d7cf6f6f28c3b3347028c3cd91686828` |
| Local extracted artifact directory | `docs/reports/goal1176_live_pod_2026-04-30/extracted/docs/reports/goal1170_clean_source_rtx_claim_grade_batch/` |
| Local intake | `valid: true`, `artifact_count: 8` |

## Failure And Recovery Timeline

1. Uploaded the reviewed Goal1175 staged source archive and Goal1176 executor to the RTX A5000 pod.
2. Executor verified archive SHA256, extracted the source, initialized a synthetic clean git repository, installed prerequisites, and built `librtdl_optix.so`.
3. First runner path failed at Goal1171 preflight because `docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.json` was absent from the staged archive. This is expected after the archive excludes generated reports, but the executor had not regenerated that file yet.
4. On the same extracted clean archive, generated the manifest with `PYTHONPATH=src:. python3 scripts/goal1170_clean_source_rtx_batch_manifest.py`.
5. Reran `bash scripts/goal1170_clean_source_rtx_batch_runner.sh`, which completed all eight rows.
6. Packaged the recovered result directory as `/tmp/goal1176_goal1170_results_after_manifest_rerun.tgz`, copied it back, extracted it locally, and ran Goal1170 intake successfully.
7. Patched `scripts/goal1176_pod_archive_batch_executor.sh` so future runs generate the manifest before `make build-optix`; focused test `tests/goal1176_pod_archive_batch_executor_test.py` passes.

## Artifact Matrix

| Artifact | App | Status | Scale | RT sub-path measured | Key metric | Source field |
| --- | --- | --- | --- | --- | --- | --- |
| `database_compact_summary.json` | `database_analytics` | accepted | `copies=20000`, `iterations=10` | compact-summary DB traversal/filter/group native continuation | `row_materializing_operation_count=0`; `compact_summary_operation_count=3`; traversal seconds per compact summary op `[0.029816, 0.029818, 0.030183]` | not emitted |
| `graph_visibility_edges.json` | `graph_analytics` | pass | `copies=20000` | visibility any-hit plus native graph-ray BFS/triangle candidate generation | visibility any-hit `1.411108s`; native BFS `6.310048s`; native triangle count `1.126617s`; all parity checks true | not emitted |
| `road_hazard_native_summary.json` | `road_hazard_screening` | pass | `copies=20000` | prepared custom-AABB segment/polygon traversal | query median `0.094769s`; `strict_pass=true`; `matches_oracle=true` | not emitted |
| `polygon_pair_candidate_discovery.json` | `polygon_pair_overlap_area_rows` | pass | `copies=20000`, `chunks=200` | OptiX LSI/PIP candidate discovery; exact area remains native CPU continuation | candidate discovery `3.060624s`; exact continuation `2.161356s`; parity true; candidate-count equality false | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |
| `polygon_jaccard_safe_chunk.json` | `polygon_set_jaccard` | pass | `copies=8192`, `chunks=16` | OptiX LSI/PIP candidate discovery; exact Jaccard remains native CPU continuation | candidate discovery `1.834486s`; exact continuation `1.752743s`; parity true; candidate-count equality false | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |
| `hausdorff_threshold_prepared.json` | `hausdorff_distance` | accepted | `A=80000`, `B=80000` | prepared fixed-radius threshold traversal | query median `0.001214s`; `matches_oracle=true`; `within_threshold=true` | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |
| `ann_candidate_65536_timing.json` | `ann_candidate_search` | timing-only accepted | `queries=196608`, `build=196608` | prepared fixed-radius candidate coverage traversal | query median `0.001055s`; `threshold_reached_count=196608`; oracle not included | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |
| `robot_pose_count_262144_timing.json` | `robot_collision_screening` | timing-only accepted | `poses=262144`, `edge_rays=1048576` | prepared ray/triangle any-hit compact pose count | query median `0.000447s`; total `1.646808s`; `validated=false`; `matches_oracle=null` | `5c61d4e2b5a432cdc9ef18e1ffbc5eef5e47b2b7` |

## Intake Result

Local intake command accepted all eight artifacts:

```bash
PYTHONPATH=src:. python3 scripts/goal1170_clean_source_rtx_batch_intake.py \
  --input-dir docs/reports/goal1176_live_pod_2026-04-30/extracted/docs/reports/goal1170_clean_source_rtx_claim_grade_batch \
  --output-json docs/reports/goal1176_live_pod_2026-04-30/goal1176_goal1170_intake_2026-04-30.json \
  --output-md docs/reports/goal1176_live_pod_2026-04-30/goal1176_goal1170_intake_2026-04-30.md
```

Result: `valid: true`, eight artifacts accepted, no intake findings.

## Boundaries

- This report does not authorize public RTX speedup wording.
- The run is clean-source staged-archive evidence, not a direct dirty worktree run.
- Some profilers do not emit `source_commit`; source provenance for those artifacts is established by the executor environment log, archive SHA, synthetic git commit, and successful Goal1171 preflight rather than by a uniform per-artifact field.
- `ann_candidate_65536_timing.json` and `robot_pose_count_262144_timing.json` are timing-only replacements; they are not correctness-validation artifacts by themselves.
- Polygon pair and Jaccard artifacts validate parity for final summaries, but their candidate-count diagnostic does not match the CPU candidate count. This is acceptable for the current bounded summary claim only if external review agrees that final parity, not raw candidate-count equality, is the correct acceptance criterion.
- The first failed executor attempt and the manifest-generation recovery are part of the official evidence trail and must remain visible.

## Local Follow-Up Already Applied

`Goal1176` executor now regenerates the Goal1170 manifest inside the extracted archive before the build and runner steps. Focused verification:

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1176_pod_archive_batch_executor_test.py
```

Result: `OK`, 2 tests.

## Requested External Review Questions

1. Is the recovered live pod batch acceptable as clean-source RTX evidence for external review input, given the transparent first-failure/recovery history?
2. Is the patched Goal1176 executor sufficient to prevent the missing-manifest failure in the next pod run?
3. Should artifacts lacking per-file `source_commit` be accepted when source provenance is established by archive SHA, synthetic git commit, environment log, and preflight?
4. Which of the eight artifacts remain blocked from public wording, and why?
