# Phoenix V3 Robot Collision Flag-Stream No-Probe Paired RTX Evidence

Status: row-scoped M7 approved after Claude P1 amendments and Codex consensus.

This packet supersedes the old robot-collision boundary only for the blocker
`probe_reference_dominates_wall_time`. It authorizes only the exact row-scoped
M7 wording below after Claude review and Codex consensus. It does not authorize
release, whole-app, robot-planning, exact-collision, continuous-collision,
zero-copy, or broad V3-over-V2 wording.

```text
status: robot_collision_flag_stream_no_probe_paired_rtx_evidence_m7_approved_row_scoped
generic_capability: collision_flag_stream
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
robot_planning_speedup_claim_authorized: false
exact_solid_collision_claim_authorized: false
continuous_collision_claim_authorized: false
paper_reproduction_claim_authorized: false
true_zero_copy_claim_authorized: false
m7_promotion_authorized: true
```

## Evidence Source

Remote RTX pod:

```text
host: root@213.173.108.14 -p 11592
gpu: NVIDIA RTX 4000 Ada Generation
remote artifact: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621
```

Copied local artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621/summary.md
```

Runner:

```text
scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py
```

The row keeps the existing prepared grouped segment any-hit flag-stream
contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

Shape:

| Field | Value |
| --- | ---: |
| poses | 8,192 |
| links | 2 |
| groups | 16,384 |
| probe points per group | 9 |
| segments | 147,456 |
| static obstacles | 2,048 |
| static obstacle triangles | 4,096 |

## Timing Definition

The old boundary mixed CPU oracle cost into wall timing. This packet separates
the two jobs:

- validation rows run the CPU probe-reference oracle and check both backends;
- timed rows use `--no-probe-reference` and therefore exclude the CPU oracle;
- wrapper no-probe time is runner-measured subprocess wall time for the app
  command with `--no-probe-reference`; it includes Python/app process overhead,
  app lowering, backend setup, repeated prepared invocations, and JSON output,
  but excludes the CPU probe-reference oracle;
- tail prepared invocation time is `tail_medians.total_run_seconds` after
  dropping warmup rows;
- total-run window is `run_summary.total_run_seconds.total_sec` across the
  measured no-probe repeated invocation window.

This is not a zero-copy claim. The OptiX path still reports device/native buffer
reuse only inside the existing Python-facing prepared route.

## Validation Result

Validation used repeat=5/warmup=1 and kept the CPU probe-reference enabled.

| Backend | Wrapper sec | Probe-reference sec | Tail prepared invocation sec | Matches probe reference |
| --- | ---: | ---: | ---: | --- |
| Embree | 375.510951 | 373.439564 | 0.011401370 | true |
| OptiX | 376.746723 | 374.380910 | 0.002196420 | true |

The validation rows prove the same sampled flag-stream contract matches the CPU
probe reference, but they also show why the old wall metric was not useful for
performance wording: the CPU oracle dominates the process.

## No-Probe Paired Timing Result

Timed rows used repeat=101/warmup=5, with 96 measured prepared invocations per
sample. Each sample is a paired Embree/OptiX process run with the same contract
and shape.

| Sample | Tail OptiX speedup vs Embree | Total-run window OptiX speedup vs Embree | Wrapper no-probe OptiX speedup vs Embree | Traversal OptiX speedup vs Embree |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 5.047134x | 5.034452x | 1.172573x | 70.835940x |
| 2 | 5.068379x | 5.002143x | 1.082787x | 60.408736x |
| 3 | 5.053303x | 5.036172x | 1.239243x | 69.077886x |
| 4 | 5.131463x | 5.166963x | 1.179725x | 73.271559x |
| 5 | 5.129760x | 5.134057x | 1.179408x | 69.714215x |

Aggregate:

```text
validation_status: pass
timed_status: pass
all_timed_pairs_same_contract_shape_signature_counts: true
timed_rows_probe_reference_disabled: true
all_wrapper_no_probe_pairs_above_1x: true
tail_total_run_optix_speedup_vs_embree_mean: 5.086007905721244
tail_total_run_optix_speedup_vs_embree_min: 5.047133802570298
tail_total_run_optix_speedup_vs_embree_stddev: 0.037072828389912105
total_run_window_optix_speedup_vs_embree_mean: 5.074757302896491
total_run_window_optix_speedup_vs_embree_min: 5.00214272752398
total_run_window_optix_speedup_vs_embree_stddev: 0.06388204698157822
wrapper_no_probe_optix_speedup_vs_embree_mean: 1.1707471638911713
wrapper_no_probe_optix_speedup_vs_embree_min: 1.0827873042297134
wrapper_no_probe_optix_speedup_vs_embree_stddev: 0.05017476956406156
traversal_optix_speedup_vs_embree_mean: 68.66166710798478
traversal_optix_speedup_vs_embree_min: 60.40873603653645
traversal_optix_speedup_vs_embree_stddev: 4.367391238215809
```

## Interpretation

This is useful V3 evidence for a reusable engine capability, not an app-specific
native engine:

- the reusable capability is `collision_flag_stream`;
- the primitive is prepared grouped segment any-hit flags;
- both backends use the same sampled probe contract and shape;
- CPU oracle validation is explicit and separate from performance timing;
- the no-probe prepared invocation window shows a stable roughly 5.08x OptiX
  speedup over Embree;
- even process wrapper timing excluding the CPU oracle is above 1x in all five
  samples, with weakest wrapper speedup 1.083x.

The evidence remains narrow:

- it is a discrete sampled probe contract;
- it is not full robot planning;
- it is not exact solid collision;
- it is not continuous collision;
- it is not broad V3-over-V2 evidence;
- it is not zero-copy evidence;
- it is from one RTX 4000 Ada pod.

## Approved Row Boundary

After Claude's P1 amendments were applied, this exact row-scoped V3 wording is
approved:

```text
RTDL V3 includes a generic collision_flag_stream route where, on the 8,192-pose
/ 147,456-segment discrete sampled probe contract on a single RTX 4000 Ada pod,
prepared OptiX grouped segment any-hit flags beat the same-contract Embree route
across five no-probe paired process samples: tail prepared invocation speedup
mean 5.086x, total-run window speedup mean 5.075x, and no-probe wrapper speedup
mean 1.171x with weakest no-probe wrapper speedup 1.083x. CPU probe-reference
validation was run separately and matched both backends. This is sampled
flag-stream evidence, not full robot planning, exact solid collision, or
continuous collision. The tail and window speedups measure the prepared query
execution phase; the wrapper speedup is the conservative process-level bound
that includes all costs except the CPU probe-reference oracle.
```

If accepted, the wording must remain row-scoped. It must not become:

```text
Robot Collision V3 is 5x faster end to end.
RTDL accelerates full robot planning.
RTDL supports exact solid collision for this row.
RTDL supports continuous collision for this row.
V3 is broadly faster than V2 for robot collision.
This row proves zero-copy.
collision_flag_stream is M7-qualified before external review.
```

## Current Gate Reading

```text
local_evidence_sufficient_for_external_public_row_review: true
current_packet_external_review_status: claude_approved_with_p1_amendments_resolved
current_packet_2ai_consensus_status: claude_codex_consensus_complete
m7_promotion_authorized: true
row_scoped_public_speedup_claim_authorized: true
```

External review:

```text
docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: send the no-probe paired robot collision flag-stream packet for
external row-scoped M7 review instead of promoting it directly.

1. Was I foolish?

   No. The new evidence directly addresses the previous CPU-oracle
   wall-accounting blocker while keeping validation and performance timing
   separate.

2. If yes, what actions made the decision foolish?

   Not applicable. It would be foolish to call the old 5.166x hot-tail number
   end-to-end speedup, or to treat this no-probe packet as release authorization
   before external review.

3. Was there another path?

   Yes. I could close `collision_flag_stream` as a no-go despite the no-probe
   evidence. That is safe but would ignore a same-contract paired run that now
   shows no-oracle wrapper wins in every sample.

4. Can I now try a different path that actually solves the problem?

   Yes. Use this packet only as external review input, then either promote a
   row-scoped M7 claim with Claude/Codex consensus or write a final no-go.
