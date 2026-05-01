# Goal1195 Goal1194 Live Pod Recovery Report

Date: 2026-04-30

## Scope

This report documents the live recovery work after the Goal1194 pod executor hit
real cloud dependency and benchmark-scale issues. It supersedes the partial
Goal1194 live-pod artifact state, but it does not authorize release or public
RTX speedup wording by itself.

## Pod

- SSH target: `root@69.30.85.32 -p 22175`
- Local working key used by Codex: `~/.ssh/id_ed25519_rtdl_codex`
- GPU observed: NVIDIA RTX A5000, 24564 MiB
- Staged source directory on pod: `/workspace/rtdl_goal1194/rtdl_staged_source`

## Executor Fixes Required On Live Pod

The reviewed Goal1194 packet was technically correct as a batch plan, but the
live pod exposed two missing bootstrap packages:

- CUDA compiler package was missing: `/usr/local/cuda/bin/nvcc` did not exist.
  The executor was patched to install `cuda-nvcc-13-0`.
- Embree headers were missing: native strict baseline compilation failed on
  `embree4/rtcore.h`. The executor was patched to install `libembree-dev`.

These are bootstrap/environment fixes only. They do not change app logic,
benchmark contracts, artifact schemas, or public wording boundaries.

## Failure And Recovery Trail

The first completed batch stopped at 10/12 artifacts because
`polygon_jaccard_safe_chunk_optix.json` failed parity. The partial intake was:

- `docs/reports/goal1194_partial_goal1192_public_wording_evidence_batch_intake_2026-04-30.md`
- Valid schema: `False`
- Review-ready pairs: 4/6
- Blocked apps: `polygon_set_jaccard`, `hausdorff_distance`

The Jaccard failure was not ignored. Targeted probes showed chunk-sensitive or
nondeterministic behavior: small chunk settings passed; the original batch
artifact failed; a later chunk-512 rerun passed with parity. Therefore, Jaccard
is schema-ready after recovery, but it should remain a cautious public-wording
candidate until reviewer accepts the recovery trail.

The first recovery bundle fixed Jaccard and added Hausdorff, but Hausdorff
OptiX was too short for the timing floor:

- `docs/reports/goal1194_goal1192_public_wording_evidence_batch_recovery_intake_2026-04-30.md`
- Valid schema: `True`
- Review-ready pairs: 5/6
- Blocked app: `hausdorff_distance`
- Hausdorff OptiX phase: `0.00018493132665753365` seconds, below the `0.1`
  second floor.

The final recovery reran only Hausdorff OptiX at a larger prepared-query scale
and copied back a complete final bundle:

- Bundle: `docs/reports/goal1194_live_pod_2026-04-30/goal1194_goal1192_public_wording_evidence_batch_final.tgz`
- Bundle SHA256: `620607286c7f50e5b162de1ada6c5f18b522b662e95e83b91e31fded0752e6e5`
- Final intake JSON:
  `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json`
- Final intake MD:
  `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.md`

## Final Intake Result

Final intake result: `valid=true`, `artifact_count=12`,
`public_wording_review_ready_pair_count=6`.

| App | Embree phase sec | OptiX phase sec | Raw Embree/OptiX ratio | Intake ready |
| --- | ---: | ---: | ---: | --- |
| `database_analytics` | `0.11934712203219533` | `0.15072045754641294` | `0.791844` | `true` |
| `graph_analytics` | `1.0002804789692163` | `2.000505495816469` | `0.500014` | `true` |
| `road_hazard_screening` | `0.41562127228826284` | `0.10353890899568796` | `4.01416` | `true` |
| `polygon_pair_overlap_area_rows` | `2.89659671112895` | `3.4523619720712304` | `0.839019` | `true` |
| `polygon_set_jaccard` | `0.8894528830423951` | `1.6208405895158648` | `0.54876` | `true` |
| `hausdorff_distance` | `1.6802135026082397` | `0.12238904647529125` | `13.7285` | `true` |

## Interpretation Boundary

This result means all six app pairs now have schema-valid, parity-valid,
timing-floor-cleared evidence suitable for external public-wording review.

It does not mean all six have public speedup claims. Three raw ratios are below
1.0, meaning OptiX was slower than Embree on those measured phases:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Only `road_hazard_screening` and `hausdorff_distance` show raw OptiX-over-Embree
advantage in this final intake. Even for those two, any public wording must stay
limited to the measured prepared/native RT sub-path and must not imply whole-app
speedup, default-mode speedup, or universal RTX acceleration.

## Release Gate Status

Goal1195 status before external review: `needs_2_ai_review`.

Required next action:

- Send the Goal1195 review request to Gemini or Claude.
- If accepted, write a two-AI consensus report.
- Only after that should public status/docs be updated from this evidence.
