# V4 Goal4740 Robot Collision Boundary Recheck

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`robot_wrapper_boundary_repaired_but_not_v4_speed_win__keep_no_go_for_formal_hp`

## Purpose

Goal4726 closed `robot_collision` as a partial/no-go row because the grouped
any-hit gate showed a strong native traversal win but failed a coarse
wrapper-wall floor.

Goal4740 rechecks that conclusion after Goal4738 taught the important lesson:
some rows were blocked by timing-boundary mistakes rather than by the generic
runtime mechanism itself.

The question here is narrow:

Can `robot_collision` become a formal V4-over-V2.14 benchmark-app performance
row through a generic V4 repair?

## Answer

No, not for V4 formal high-performance evidence.

The wrapper-boundary diagnosis is real: when measured without huge stdout/run
details/group metadata, the OptiX grouped any-hit flags route is clearly faster
than Embree for the same contract.

But V2.14 already had the same relevant prepared OptiX grouped-segment any-hit
flags and scalar-count primitives. Therefore this repair corrects the internal
Robot evidence boundary, but it does not create a new V4-over-V2.14 speed win.

## Evidence

POD evidence directory:

`future/v4/evidence/v4_goal4740_robot_boundary_20260626/`

Command shape:

- dataset: `scaled`
- poses: `8192`
- obstacles: `2048`
- links: `2`
- repeats: `51`
- warmup: `5`
- lowering mode: `numpy_arrays`
- run details: suppressed
- group metadata: skipped
- probe reference: disabled for timing

Measured rows:

| Route | Tail hot seconds | Notes |
|---|---:|---|
| OptiX flags | 0.002313694 | native prepared device query/output buffers |
| OptiX count-only | 0.000153990 | scalar flagged-group count only |
| Embree flags | 0.011689998 | prepared host-buffer route |

Ratios:

- Embree flags / OptiX flags: `5.053x`
- OptiX flags / OptiX count-only: `15.025x`

This proves the old wrapper-wall failure was not a good characterization of the
native route's performance when stdout/run-detail noise is removed.

## V2.14 Boundary

Goal4672's V2.14 primitive audit already recorded:

`robot_collision` V2.14 primary route:

`prepared RTDL/OptiX any-hit flag primitive`

V2.14 primitive contract:

`prepared any-hit collision flag and scalar count`

`git show v2.14` also confirms that the relevant current-app surfaces already
existed in V2.14:

- `optix_prepared_device_buffers`
- `optix_prepared_device_count`
- `summary_only_runs`
- `PreparedOptixGroupedSegmentQuery3D`
- `run_native_prepared_grouped_segment_any_hit_flags`
- `run_native_prepared_grouped_segment_any_hit_count`

So the corrected Robot boundary is product/usefulness evidence for the generic
primitive, not a new V4 performance mechanism versus V2.14.

## Matrix Classification

`robot_collision` remains:

`closed_same_primitive_boundary_repaired_no_v4_over_v2_speed_credit`

It is better than Goal4726's wording in one respect: the internal grouped
any-hit route should not be described as wrapper-wall failed after summary-only
recheck. But it remains a formal high-performance no-go because V2.14 already
had the same primitive family.

## Implication For The Next Goal

Do not spend more POD time on Robot unless a genuinely new generic V4 primitive
or a frozen V2.14-vs-current same-primitive improvement hypothesis is written
before running.

The next blocker should be `spatial_rayjoin` only if a real relation-topology
route exists, or else the work should move to final release framing with the
current bounded high-performance evidence.

## Claim Boundary

Goal4740 authorizes the internal statement:

Robot's grouped any-hit primitive is fast under a clean hot-path boundary, but
it does not count as a V4-over-V2.14 benchmark-app speed win because V2.14
already exposed the same primitive family.

Goal4740 does not authorize:

- final V4 tag;
- Robot speedup claim versus V2.14;
- all-benchmark speedup claim;
- broad V4-over-V2.14 speedup wording;
- measured catalog promotion from Robot;
- app-specific native kernels;
- arbitrary callbacks;
- raw OptiX callbacks;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?

Partly yes in the process, not in the final decision. I wasted time on nested
SSH shell quoting while trying to summarize already-generated JSON.

2. What action made the decision foolish?

I used a remote shell loop with an unescaped `$f`, causing a hung `grep`.
The correction was to stop that command and read fixed filenames directly.

3. Was there another path?

Yes. I should have pulled the JSON files first, then parsed locally with
PowerShell. That is the better pattern for future POD evidence reads.

4. Can I now try a different path that actually solves the problem?

Yes. The technical conclusion is now clear: do not chase Robot as a V4 speed
row. Move to either a real `spatial_rayjoin` route decision or bounded-release
convergence.

## Non-Authorization

Goal4740 authorizes no final V4 tag, no public Robot speedup wording, no
all-benchmark claim, no app-specific native kernel, no arbitrary callback
support, and no true-zero-copy wording.
