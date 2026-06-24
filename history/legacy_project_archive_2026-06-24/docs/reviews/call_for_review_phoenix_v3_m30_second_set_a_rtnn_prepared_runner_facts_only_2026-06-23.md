# Facts-Only Call For Review: Phoenix V3 M30 RTNN Second Set-A Candidate

Date: 2026-06-23

Use this only if the file-reading M30 review stalls. Return a critical review
from the facts below only.

## Requested Verdict Labels

Use exactly one:

- `accept_m30_rtnn_as_second_set_a`
- `accept_with_amendments`
- `blocked_needs_focused_rerun`
- `reject_not_second_set_a`

## Facts

M30 candidate:

- family: generic `fixed_radius_ranked_summary_3d` prepared-execution runner
- pressure app: RTNN
- productized path: `prepared_execution_session_runner`
- status before review:
  `m30_second_set_a_candidate_pending_claude_review_not_release`
- M30 report:
  `docs/reports/phoenix_v3_m30_second_set_a_candidate_rtnn_prepared_runner_2026-06-23.md`

M28/M29 current first-family chain:

- M28 froze Barnes-Hut aggregate-tree fused weighted-vector sum 2D as a current
  Set-A runtime-trunk family candidate under Codex+Claude consensus.
- M29 classified v2.14 Barnes-Hut as
  `v2_14_has_cpu_fused_or_typed_stream_only`.
- M29 conclusion: current Barnes-Hut runner surface is a V3
  surface/capability addition, not a same-contract V3-over-v2.14 speedup.
- M29 status: `approve_with_amendments_applied` / `classified_not_release`.

RTNN 2026-06-22 evidence:

- evidence path:
  `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/`
- hardware: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`,
  compute capability `8.9`
- scale: `1,048,576` points
- distribution: uniform
- radius: `0.02`
- `k`: `50`
- repeat: `50`
- warmups: `3`
- variants:
  - `productized_prepared_execution_runner`
  - `legacy_app_front_door_prepared_optix`
  - `cupy_grid_reference`
- runner metadata:
  - `runtime_trunk_executes_end_to_end: true`
  - `internal_device_residency_between_rtdl_phases: true`
  - `repeat50_material_probe_candidate: true`
  - `runtime_sourced_material_gain_candidate: true`

RTNN correctness:

- runner vs legacy:
  - row-count delta `0`
  - bounded-neighbor-count delta `0`
  - nearest-id checksum delta `0`
  - kth-id checksum delta `0`
  - sum-distance relative error `2.160265046994547e-16`
  - signature match `true`
- runner vs CuPy uniform-grid CUDA-core:
  - row-count delta `0`
  - bounded-neighbor-count delta `0`
  - nearest-id checksum delta `0`
  - kth-id checksum delta `0`
  - sum-distance relative error `3.071810486130005e-11`
  - signature match `true`

RTNN timing:

- runner vs legacy hot query: `0.988781x`
- runner vs legacy cold-plus-query wall: `1.358329x`
- runner vs legacy runner wall: `1.370176x`
- runner over CuPy uniform-grid CUDA-core hot query: `7.786920x`
- runner over CuPy uniform-grid CUDA-core cold-plus-query wall: `1.130421x`
- runner over CuPy uniform-grid CUDA-core runner wall: `3.196372x`

Known RTNN boundaries:

- Material signal is repeat50 prepared-session runner wall and cold-plus-query
  improvement versus the legacy app-front-door route.
- Hot query is not faster than legacy (`0.988781x`).
- CuPy comparison is a CUDA-core uniform-grid reference, not the RTNN paper
  implementation and not a general nearest-neighbor baseline.
- No single-shot RTNN speedup claim is authorized.
- No public speedup or broad V3-over-V2 claim is authorized.
- Current evidence has weak git provenance because the remote current tree was
  not a git checkout; this mirrors the M28/M29 provenance caveat.

Prior reviews:

- Kepler result review on 2026-06-22:
  `accept_as_second_set_a_material_probe`, no release/all-app authorization.
- Claude 2026-06-21 repeat50 wording review:
  `APPROVE_WITH_CONDITIONS`; conditions were repeat50 disclosure, no
  single-shot wording, no selective timing number, CuPy grid baseline naming,
  float32/float64 precision disclosure, and provenance disclosure.

Post-M22 context:

- M20 under an older sequence recorded
  `focused_productized_material_probe_count_verified: 3` and authorized
  all-app protocol preparation only.
- M22 then ran a serious same-RT-hardware V2.14/current all-app comparison.
- M22 verdict: `approve_blocked_not_release`.
- M22 controlling facts:
  - overall geomean V3 vs V2.14: `1.049x`
  - Set-A geomean: `1.013x`
  - Set-B geomean: `1.210x`
  - apps above `1.05x`: `4/10`, required `8/10`
  - Barnes-Hut app geomean: `0.831x`
  - release/public/broad speedup authorization: false
- M23 closed the current V3 RayJoin `point_order_mode` correctness defect.
- M24 closed the focused Barnes-Hut blocker with boundary:
  - fixed current vs V2.14 four-row geomean: `15.811x`
  - repeated-query value only; single-query current remains slower at tested sizes.
- M27 accepted a LibRTS/AABB runner-output fix with boundary, but left:
  - OptiX cold watch row status `improved_not_closed`
  - Embree 32768 status `stability_watch_blocker`
- M27 explicitly says LibRTS/AABB single-shot is Set-B/control and must not be
  counted as Set-A.

## Questions

1. Does the 2026-06-22 RTNN productized runner repeat50 evidence qualify as a
   valid focused Set-A runtime-trunk family under the M28/M29 framing?
2. Is it correct to use the productized-runner evidence as controlling M30
   evidence rather than the older 2026-06-21 CuPy-only amortization row?
3. Are the material numbers interpreted correctly?
4. Are repeat50, CuPy-reference, provenance, no-single-shot, and no-release
   boundaries strong enough?
5. Should M30 accept the existing same-hardware evidence without new POD time,
   or require a focused rerun?
6. Does accepting RTNN, if accepted, leave the M22 non-release result and all
   remaining blockers intact?
7. Does this review authorize any all-app run, release, public speedup, broad
   V3-over-V2, true-zero-copy, automatic partner-selection, or V4 work?

## Required Output

Save your review to:

`docs/reviews/claude_phoenix_v3_m30_second_set_a_rtnn_prepared_runner_review_2026-06-23.raw.md`

Include:

- one verdict label;
- blocking findings, if any;
- required amendments, if any;
- explicit answers to the seven questions;
- explicit non-authorization block.
