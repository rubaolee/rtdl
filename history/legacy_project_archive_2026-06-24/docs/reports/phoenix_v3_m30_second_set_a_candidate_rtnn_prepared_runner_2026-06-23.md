# Phoenix V3 M30 Second Set-A Candidate: RTNN Prepared Runner

Date: 2026-06-23

Status: `m30_second_set_a_candidate_pending_claude_review_not_release`

```text
release_authorized: false
all_app_pod_spend_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_work_authorized: false
```

## Decision Candidate

M30 selects the RTNN prepared-execution repeat50 runner as the candidate second
true Set-A runtime-trunk family after the M28/M29 Barnes-Hut freeze.

The exact family is:

```text
generic fixed_radius_ranked_summary_3d prepared-execution runner
```

The pressure app is RTNN, but the claimed V3 mechanism is the productized
prepared-execution runner for fixed-radius ranked summary. This is not a whole
RTNN paper claim and not an app-specific native shortcut claim.

## Post-M22 Context

This packet must be read with the existing Phoenix chronology, not as a fresh
release authorization path by itself.

Earlier M20/M22/M27 records already show:

- M20 recorded `focused_productized_material_probe_count_verified: 3` under an
  older probe ledger and authorized all-app protocol preparation only.
- M22 then ran the serious same-RT-hardware V2.14/current all-app comparison
  and did not clear the release bar.
- M22/M23/M24/M27 left concrete blockers visible, including Set-A aggregate
  weakness, Barnes-Hut severe-regression repair work, RayJoin correctness
  repair, and LibRTS/AABB Set-B stability watch rows.
- M27 explicitly says LibRTS/AABB is Set-B/control work and must not be counted
  as Set-A.

Therefore M30 cannot override the M22 non-release result. Its narrow purpose is
to ask whether RTNN is valid as a current productized-runner Set-A family under
the M28/M29 reframing. If accepted, it is a focused runtime-trunk fact, not an
all-app or release decision.

## Why This Candidate

The current candidate evidence already satisfies the shape M30 needs:

- same RTX 4000 Ada POD evidence;
- serious scale: `1,048,576` points;
- repeated prepared session: `repeat=50`, `warmups=3`;
- productized path: `prepared_execution_session_runner`;
- runtime trunk executes end to end;
- internal RTDL device residency between RTDL phases is reported;
- runner output matches both the legacy OptiX app-front-door route and a CuPy
  uniform-grid CUDA-core reference;
- release, all-app, public-speedup, and broad V3-over-V2 flags remain false.

Evidence path:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/
```

Primary report:

```text
docs/rebuild/v3/phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md
```

## Timing Record

The M30 controlling timings are the 2026-06-22 productized-runner evidence, not
the older 2026-06-21 CuPy-only amortization row.

| Comparison | Speedup |
| --- | ---: |
| runner vs legacy hot query | `0.988781x` |
| runner vs legacy cold-plus-query wall | `1.358329x` |
| runner vs legacy runner wall | `1.370176x` |
| runner over CuPy uniform-grid CUDA-core hot query | `7.786920x` |
| runner over CuPy uniform-grid CUDA-core cold-plus-query wall | `1.130421x` |
| runner over CuPy uniform-grid CUDA-core runner wall | `3.196372x` |

Interpretation:

- The material Set-A signal is the repeat50 prepared-session runner wall and
  cold-plus-query improvement versus the legacy app-front-door route.
- The hot query is not faster than legacy (`0.988781x`), so M30 must not claim
  the productized runner is uniformly faster than the legacy route.
- The CuPy comparison is a CUDA-core uniform-grid reference, not the RTNN paper
  implementation and not a general nearest-neighbor baseline.

## Correctness Record

Runner vs legacy OptiX app-front-door:

```text
row_count_delta: 0
bounded_neighbor_count_delta: 0
nearest_id_checksum_delta: 0
kth_id_checksum_delta: 0
sum_distance_relative_error: 2.160265046994547e-16
signature_match: true
```

Runner vs CuPy uniform-grid CUDA-core reference:

```text
row_count_delta: 0
bounded_neighbor_count_delta: 0
nearest_id_checksum_delta: 0
kth_id_checksum_delta: 0
sum_distance_relative_error: 3.071810486130005e-11
signature_match: true
```

## Candidate Comparison

| Candidate | M30 classification |
| --- | --- |
| RTNN prepared repeat50 runner | best second Set-A candidate; material runner-wall/cold-plus-query evidence exists |
| RTDBSCAN M3.4 repeated runner | parity only; runner vs legacy geomean `0.997558x`; stop as immediate material probe |
| Hausdorff M6.1 runner | positive focused evidence, but runner vs legacy wrapper wall only `1.054105x`; not strict Set-A |
| AABB / LibRTS | Set-B/control/stability work after M27; not valid second Set-A |
| Triangle | handled by older M19/M20 third-probe sequence; not the M30 second-family candidate |

Note: older M19/M20 records later closed Triangle under that older sequence.
M30 does not reopen or erase that record. It only asks whether RTNN should be
accepted in the current M28/M29 Set-A family chain.

## Required Boundaries

If Claude accepts RTNN as the second Set-A family, the acceptance is scoped to:

- repeat50 prepared-session amortization only;
- one RTX 4000 Ada POD evidence packet;
- productized `prepared_execution_session_runner` runtime-trunk evidence;
- fixed-radius ranked-summary behavior at the recorded scale, radius, and `k`;
- internal RTDL residency only, not external zero-copy.

The acceptance must not be rewritten into:

- V3 release readiness;
- all-app authorization;
- reversal of the M22 all-app non-release result;
- broad V3-over-V2 speedup;
- single-shot or cold-start RTNN speedup;
- whole RTNN paper reproduction;
- general nearest-neighbor speedup;
- RT-core speedup for all workloads;
- true zero-copy or embedding work.

## Resource Decision

M30 does not request immediate new POD time. The existing 2026-06-22 focused
POD packet is recent, same-hardware, serious-scale, and already has runner,
legacy, and CuPy reference rows.

If Claude rejects the existing packet because of provenance or scope, the next
bounded fallback is a focused RTNN rerun only. Estimated POD cost:

```text
focused rerun: 30-90 minutes
expanded provenance rerun with source manifest: 1-2 hours
all-app run: still forbidden
```

## Goal-Level Decision Audit

Decision: select RTNN prepared repeat50 runner as the M30 candidate for the
second true Set-A runtime-trunk family, pending Claude review.

1. Was I foolish?
   No. The candidate has productized-runner evidence, serious scale, parity
   checks, and a material repeat50 runner-wall/cold-plus-query signal.

2. If yes, what actions made the decision foolish?
   The foolish action would be to quote only the largest CuPy hot-query number
   or to present repeat50 amortization as single-shot RTNN speedup.

3. Was there another path?
   Yes. RTDBSCAN could be re-tuned, Hausdorff could be over-counted, or Triangle
   could be counted before runner wiring. Those paths repeat the earlier error
   of forcing weak or not-yet-productized evidence into the Set-A slot.

4. Can I now try a different path that truly solves the problem?
   Yes. Ask Claude to review the exact RTNN productized-runner packet under the
   current M28/M29 bar; accept it only if the repeat50 and non-release
   boundaries are explicit.

## Non-Authorization

This M30 candidate report authorizes no Phoenix V3 release, no all-app run, no
public speedup claim, no broad V3-over-V2 claim, no RT-core speedup claim, no
single-shot RTNN claim, no true-zero-copy claim, no automatic partner-selection
claim, no embedding work, and no V4 work.
