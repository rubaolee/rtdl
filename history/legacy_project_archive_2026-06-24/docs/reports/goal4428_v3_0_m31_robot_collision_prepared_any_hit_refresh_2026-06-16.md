# Goal4428 V3.0 M31 Robot Collision Prepared Any-Hit Refresh

Date: 2026-06-16

Evidence:

`docs/reports/goal4428_v3_0_m31_robot_collision_prepared_any_hit_refresh_xlarge_2026-06-16.json`

Status: complete. M31 refreshes the robot-collision row as a primitive-first benchmark over the same generic prepared grouped-segment any-hit contract. It intentionally does not mix the OptiX-only native device-buffer/count paths into the Embree-vs-OptiX table.

Update: Goal4446/M50 keeps the same contract and replaces the Python-heavy query lowering with a NumPy vectorized lowering path, cutting prepared query descriptor construction by about 113x on the xlarge fixture. Use Goal4446 for current cold/setup wording.

## Contract

Both backends run:

`PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1`

The benchmark lowers sampled robot link poses into vertical finite 3D segment probes, tests those probes against a prepared static triangle scene, and returns compact group any-hit flags. The native engine sees generic grouped finite segments and triangles, not robot-specific callbacks or collision-planner logic.

## Dataset

The run uses the xlarge scaled fixture:

- 262,144 poses
- 8,192 obstacles
- 4 links
- 1,048,576 groups
- 9,437,184 query segments
- 16,384 static obstacle triangles
- warmup 1
- repeat 5 on both Embree and OptiX
- Python-owned host query/output buffer reuse on both backends

CPU probe reference is skipped at this size. Correctness is gated by cross-backend agreement of compact flag signatures and flagged-group counts.

## Results

| Backend | Total run median sec | Total run window sec | Traversal median sec | Output clear median sec | Output postprocess median sec | Flagged groups | Signature hash prefix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Embree CPU | 1.167794 | 4.666501 | 0.427348 | 0.084145 | 0.125743 | 345,374 | `72074ff2a580` |
| OptiX RT cores | 0.630469 | 2.507200 | 0.063238 | 0.085387 | 0.131911 | 345,374 | `72074ff2a580` |

## Same-Contract Ratios

| Metric | Embree sec | OptiX sec | Embree / OptiX | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Traversal median | 0.427348 | 0.063238 | 6.76x | RT cores strongly accelerate the generic grouped-segment any-hit traversal. |
| Total prepared-buffer run median | 1.167794 | 0.630469 | 1.85x | Shared output clear/postprocess and host-buffer handling compress the end-to-end hot prepared-run gain. |
| Total measured window | 4.666501 | 2.507200 | not a speedup metric | Same repeat count, but this row reports median speedup; the window confirms the measurement is not a tiny one-shot. |

## Cold Setup Boundary

The evidence also records large setup metadata:

- Embree app lowering: 17.795s
- OptiX app lowering: 14.261s
- prepared query descriptor build metadata: about 46-48s per row

These values are not summed into the prepared-buffer hot run median above. They are real engineering debt for cold end-to-end use, but they are not the primitive traversal comparison. M31 therefore supports a prepared-run statement, not a cold whole-application statement.

## Validation

The evidence records:

- `comparison.all_same_contract=true`
- `comparison.all_signature_hashes_match_cross_backend=true`
- `comparison.all_flagged_group_counts_match_cross_backend=true`
- `comparison.all_host_buffer_reuse_same_contract=true`
- `comparison.public_speedup_claim_authorized=false`
- both rows use host query/output buffer reuse
- neither row claims native device-buffer reuse or true zero-copy

## Closeout

M31 closes the V3 robot-collision prepared any-hit refresh. Internal wording may say that, for the same xlarge sampled grouped-segment contract, OptiX/RT cores are 6.76x faster than Embree in traversal and 1.85x faster in total prepared-buffer run median, with identical compact flag signatures.

This does not authorize continuous collision detection, exact solid collision, robot-planner acceleration, paper reproduction, true zero-copy, or whole-application speedup wording.
