# Phoenix V3 Robot Collision Flag-Stream Boundary

Status: rebuild boundary packet, not a release.

## Verdict

`robot_collision / prepared_collision_flags` is useful Phoenix V3 evidence for
the reusable `collision_flag_stream` capability, but it is not M7-qualified.

```text
status: robot_collision_flag_stream_boundary_not_m7
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
robot_planning_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

The important lesson is narrow: RTDL can express a prepared grouped segment
any-hit collision-flag stream. The current evidence does not prove full robot
planning acceleration, exact solid collision, continuous collision, paper
reproduction, or a broad V3-over-V2 speedup.

## Evidence

Source artifacts:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/paired_v2_v3_summary.json
```

Current-side row:

| Metric | Embree | OptiX | OptiX / Embree reading |
| --- | ---: | ---: | ---: |
| Hot tail total run | 0.011322040 s | 0.002191603 s | 5.166x |
| Native traversal phase | 0.005855341 s | 0.0000837625 s | 69.904x |
| Wall median | 188.933612384 s | 189.563679762 s | 0.997x |
| Probe reference | 187.059307300 s | 187.217812918 s | parity |

Measurement protocol:

| Field | Value |
| --- | ---: |
| warmup rows | 1 |
| recorded repeats | 5 |
| measured tail rows | 4 |
| run-level probe-reference matches | true |

Wall ratios below 1.0 mean OptiX is slower on the current full wall path. Here
the hot collision-flag stream is fast, but the CPU probe-reference work
dominates wall timing.

The all-app summary row carries `matches_cpu_reference: null`, so it cannot be
treated as a generic CPU-reference certification field. The run-level robot
payloads do report `matches_probe_reference: true` for every recorded Embree and
OptiX run. This improves the correctness boundary, but it does not promote the
row: M7 remains blocked by wall timing, reference/setup dominance, and sampled
probe contract scope.

Shape:

| Field | Value |
| --- | ---: |
| poses | 8,192 |
| links | 2 |
| groups | 16,384 |
| probe points per group | 9 |
| segments | 147,456 |
| static obstacle triangles | 2,048 |

V2.14 paired context:

| Backend | Standard-row V3 speedup versus V2.14 |
| --- | ---: |
| Embree | 1.003x |
| OptiX | 1.028x |

The paired rows are standard `goal2626` rows. They do not authorize a broad
V3-over-V2 robot-collision speedup claim.

## Claim Boundary

Allowed rebuild wording:

- RTDL has a reusable `collision_flag_stream` boundary.
- The current hot prepared collision-flag tail metric is 5.166x OptiX over Embree.
- The current native traversal phase is 69.904x OptiX over Embree.
- The current wall path is not faster: Wall OptiX / Embree is 0.997x.
- This is discrete sampled probe evidence.

Forbidden public wording:

- Do not claim Robot Collision V3 is 5.166x faster end to end.
- Do not claim RTDL accelerates full robot planning.
- Do not claim RTDL supports exact solid or continuous collision for this row.
- Do not claim `collision_flag_stream` is M7-qualified.
- Do not claim V3 is broadly faster than V2 for robot collision.

## M7 Blockers

- Wall timing is parity or slightly slower for OptiX.
- The probe-reference pass dominates wall timing.
- The row is a discrete sampled probe contract only.
- Exact solid and continuous collision claims are false.
- The all-app row does not carry a `matches_cpu_reference: true` field, even
  though run-level probe-reference matches are true.
- Standard paired V2.14 rows show parity, not large V3 speedup.
- Fresh external review is required before any promotion.

Current review blockage target:

```text
docs/reviews/external_review_blocked_phoenix_v3_robot_collision_flag_stream_boundary_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: keep robot collision as a rebuild boundary lesson, not as an M7 row.

1. Was I foolish?

   No. The hot signal is real, but wall timing and contract scope block release
   wording.

2. If yes, what actions made the decision foolish?

   It would be foolish to publish the 5.166x or 69.904x numbers without the
   0.997x wall ratio and sampled-probe boundary beside them.

3. Was there another path?

   Yes: tune the probe-reference/setup path first. That may become useful later,
   but it is not current evidence.

4. Can I now try a different path that actually solves the problem?

   Yes. Teach the reusable flag-stream contract honestly, keep M7 at zero, and
   promote only after wall/setup/reference evidence and external review close.
