# Goal1169 Clean-Source RTX Claim-Grade Batch Plan

Date: 2026-04-30

## Purpose

Goal1166 produced useful RTX A5000 engineering evidence, but it is not
claim-grade because the pod source was copied from a dirty local working tree.
Goal1169 defines the next pod session as a clean-source, batched run rather than
another ad hoc live test.

This plan does not authorize public wording. It defines what evidence to collect
next so later review can decide whether wording may be promoted.

## Source Policy

The next pod run must use one of these source modes:

- clean git checkout of a pushed commit; or
- staged source archive with a manifest, exact digest, and no untracked/dirty
  ambiguity.

The runner must record:

- git commit or archive digest;
- `git status --short` or staged-manifest status;
- GPU model, driver, CUDA version, OptiX header version, and native build log;
- exact command lines and output artifact paths.

If the source is dirty or manually patched on the pod, the run is engineering
evidence only and must not be used for public speedup wording.

## Priority Rows

| Priority | App/path | Current public wording state | Required clean-source evidence |
| ---: | --- | --- | --- |
| 1 | `database_analytics / compact_summary` | `public_wording_not_reviewed` | Same-semantics compact-summary RTX run, correctness parity, and baseline phase timing that excludes row materialization. |
| 2 | `graph_analytics / visibility_edges` | `public_wording_not_reviewed` | Visibility-edge RTX any-hit row plus graph native-summary row, with explicit boundary that BFS orchestration and triangle set-intersection are not whole-app claims. |
| 3 | `road_hazard_screening / native compact summary` | `public_wording_not_reviewed` | Prepared native segment/polygon road-hazard summary with correctness parity and phase-clean timing. |
| 4 | `polygon_pair_overlap_area_rows / candidate discovery` | `public_wording_not_reviewed` | OptiX LSI/PIP candidate discovery timing, CPU/native exact continuation timing, and parity for the selected bounded scale. |
| 5 | `polygon_set_jaccard / candidate discovery` | `public_wording_not_reviewed` | Safe chunk-size validation, diagnostic chunk boundaries, and candidate-discovery versus exact-continuation split. |
| 6 | `hausdorff_distance / directed_threshold_prepared` | `public_wording_not_reviewed` | Prepared threshold decision parity and phase timing; exact distance and witness IDs remain outside the claim. |
| 7 | `ann_candidate_search / candidate_threshold_prepared` | `public_wording_reviewed` | Clean-source replacement for the dirty Goal1166 large-timing artifact; large row may remain timing-only but must be paired with a correctness row. |
| 8 | `robot_collision_screening / prepared pose-count` | `public_wording_reviewed` | Clean-source replacement for the dirty Goal1166 robot validation and large timing artifacts; keep normalized per-pose wording boundary. |

## Non-Goals

- Do not promote whole-app speedup wording.
- Do not use `--backend optix` as evidence by itself.
- Do not compare timing-only rows against correctness baselines.
- Do not claim polygon exact area/Jaccard refinement is fully RT-core native.
- Do not claim graph BFS, triangle counting, or shortest path as whole-app RT
  acceleration when only bounded graph-ray candidate generation is measured.

## Pod Efficiency Rule

Before starting a pod, local work must produce:

- a single runner script or manifest for all rows;
- expected output filenames;
- per-row timeout and validation policy;
- an intake script that can reject dirty-source or missing-artifact runs.

Once a pod is started, run all rows in the batch, copy back all artifacts/logs,
and only then decide whether a second pod session is needed.
