# Goal4451 / V3.0 M55 RayJoin PIP Graph Fail-Closed

## Outcome

M55 closes the RayJoin PIP prepared-points CUDA graph replay debt by making the
unsafe path fail closed in the Python runtime. The batch executor remains the
recommended repeated-PIP path.

Summary: batch executor remains the recommended repeated-PIP path; unvalidated graph replay now fails closed before native prepare.

This is not a performance win. It is a correctness and route-guidance cleanup:
the runtime must not silently expose a graph object that can replay zero counts
or fail native OptiX/CUDA graph capture after prior launches.

## What Changed

- `PreparedOptixPointClosedShapeBatchCountGraph2D` now rejects unvalidated graph
  prepare by default unless
  `RTDL_OPTIX_ALLOW_UNVALIDATED_PREPARED_POINTS_BATCH_GRAPH=1` is set for a
  diagnostic negative probe.
- Native graph prepare failures are re-raised with a quarantine message that
  points users to `prepare_device_filtered_prepared_points_batch_executor(...)`.
- Validation mismatch still closes the graph handle and now reports the same
  quarantine boundary.
- The reusable batch executor is not quarantined and remains the repeated-PIP
  correctness path.

## Pod Probe

The live pod probe used a minimal square polygon with three points. Two points
are inside, so all trusted count lanes must return `2`.

| Lane | Result |
| --- | --- |
| Single prepared count | `2` |
| Prepared batch count | `[2, 2, 2]` |
| Prepared batch executor | `[2, 2, 2]` |
| Unvalidated graph replay | fails closed before native prepare |
| Validated graph replay | fails closed with quarantine after native prepare/validation failure |

RELAXED capture did not fix the failure during investigation. The native source
therefore remains on the original `CU_STREAM_CAPTURE_MODE_GLOBAL` path; M55 does
not promote a speculative native capture-mode change.

## Route Implication

For Spatial RayJoin repeated PIP:

- Use the prepared point/closed-shape batch executor.
- Do not use prepared-points CUDA graph replay as a correctness or performance
  path.
- Revisit graph replay only after OptiX/CUDA capture passes hardware validation
  and replay returns nonzero counts under the same prepared-points contract.

## Claim Boundary

This work does not authorize a performance claim, a RayJoin paper-reproduction
claim, a public speedup claim, true-zero-copy wording, or automatic partner
selection. It only closes an unsafe API route and updates current guidance.
