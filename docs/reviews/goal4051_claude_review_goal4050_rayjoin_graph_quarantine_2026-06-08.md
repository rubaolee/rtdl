# Goal4051 — Claude Independent Review: Goal4050 RayJoin PIP Graph Replay Quarantine

**Reviewer:** Claude Sonnet 4.6 (independent read-only review)
**Date:** 2026-06-08
**Verdict:** `accept`

---

## Check 1: No Overclaim

**Pass.**

The report (`goal4050_rayjoin_pip_graph_replay_quarantine_2026-06-08.md`) has an
explicit "Claim Boundary" section that prohibits all eight forbidden claim types:
release action, public speedup wording, whole-app RayJoin wording, RayJoin paper
reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, and
automatic partner/backend selection.

The artifact JSON (`goal4050_rayjoin_pip_graph_current_negative_probe_pod.json`)
has a `claim_boundary` object with all six flags set to `false`:

- `public_speedup_claim_authorized: false`
- `rayjoin_paper_reproduction_claim_authorized: false`
- `release_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`

The `batch_executor.metadata` block additionally carries `release_authorized:
false` and `true_zero_copy_claim_authorized: false`. The dataclass guard in
`current_benchmark_route_decisions.py` (`__post_init__`) structurally enforces
that all nine authorization flags remain `False` for any registered
`CurrentBenchmarkRouteDecision`; the same constraint exists in
`v2_9_benchmark_adequacy.py`. No overclaim language appears anywhere in the
reviewed materials.

---

## Check 2: Route Decision Is Technically Sensible

**Pass.**

`current_benchmark_route_decisions.py` — `spatial_rayjoin` entry:

- `rejected_or_unpromoted_candidates` now includes `"prepared-points CUDA graph
  replay after Goal4050 OptiX/CUDA prepare failure"` as its last element.
- `next_runtime_action` reads: "treat prepared-points CUDA graph replay as
  quarantined until a real OptiX-capture fix exists."
- `evidence_refs` includes `"Goal4050"`.
- The `primary_route` remains the mixed explicit route from Goal4039; the batch
  executor (repeated PIP) and scalar-count executor (exact scalar counts) are
  the active RTDL/OptiX legs.

`v2_9_benchmark_adequacy.py` — `spatial_rayjoin` row:

- `next_generic_runtime_action` explicitly says "keep the prepared-points CUDA
  graph replay path blocked until the zero-count replay failure and Goal4050
  OptiX/CUDA prepare failure are fixed."
- `evidence_refs` includes `"Goal4050"`.

The failure mode reported is an upgrade from Goal3312's zero-count replay: the
graph handle now raises `RuntimeError: OptiX error: CUDA error` during
`PreparedOptixPointClosedShapeBatchCountGraph2D.__init__` (i.e., at prepare
time), before any replay result is exposed. The Python wrapper's
`failed_closed` status confirms the guard works as designed. Both outcomes are
consistent in routing conclusion: graph replay is not a usable performance lane
on current main.

The batch executor (`reusable_launch_executor: true`) and the single prepared
count path are left undisturbed as the recommended lanes. This is the correct
outcome.

---

## Check 3: Artifact Is Internally Consistent

**Pass.**

Working non-graph lanes all return `6` / `[6, 6, 6, 6, 6]`:

| Field | Value |
|---|---|
| `single.count` | `6` |
| `batch.counts` | `[6, 6, 6, 6, 6]` |
| `batch_executor.counts` | `[6, 6, 6, 6, 6]` |

Failed graph lanes report the correct failure statuses and error text:

| Field | Value |
|---|---|
| `graph_validated.status` | `"failed_closed"` |
| `graph_validated.error` | `"OptiX error: CUDA error"` |
| `graph_raw.status` | `"prepare_or_replay_failed"` |
| `graph_raw.error` | `"OptiX error: CUDA error"` |

All six `claim_boundary` flags are `false`. The `batch_executor` metadata is
consistent with the batch executor contract: `schema` is
`rtdl.optix.prepared_point_closed_shape_batch_count_executor_2d.v1`,
`request_count` is `5`, `reusable_launch_executor` is `true`, and the mode
string is `prepared_points_device_filtered_batch_executor_run`.

**One minor observation (non-blocking):** The `graph_raw.timings` and
`graph_validated.timings` blocks show identical values to the batch executor's
timings (including `mode: "prepared_points_device_filtered_batch_executor_run"`
and `candidate_count_pass: 9.0704e-05`). This is because the graph preparation
fails before any graph-specific timing can be captured; the probe script
evidently pre-populates the timing dict from the last batch executor run and
then records the failure. This is not a misrepresentation — the `status` and
`error` fields are unambiguous — but a reader could wonder why a graph field
reports a batch executor mode string. No fix is required for route-guidance
purposes; it is worth a short comment in the probe script if it is ever
revisited.

---

## Check 4: Tests Cover the Regression Boundary Appropriately

**Pass.**

**Test 1 (`test_pod_artifact_records_working_non_graph_lanes_and_failed_graph_lane`):**
Reads the checked-in JSON artifact and verifies goal number, working-lane
counts, both graph failure statuses, the CUDA error string, and that all
claim-boundary flags are false. Pure static JSON read — no native engine or app
logic involved. Covers the core regression boundary: correct counts in
non-graph lanes co-existing with confirmed graph failure.

**Test 2 (`test_current_rayjoin_guidance_quarantines_prepared_points_graph_replay`):**
Calls `rt.explain_current_benchmark_route("spatial_rayjoin")` and
`rt.current_benchmark_adequacy()` — both are Python module calls over static
registry data, not app execution. Checks that `"Goal4050"` appears in both
`evidence_refs`, that the CUDA graph replay candidate appears in
`rejected_or_unpromoted_candidates[-1]`, that "quarantined" appears in
`next_runtime_action`, that `"OptiX/CUDA prepare failure"` appears in
`next_generic_runtime_action`, and that both authorization flags checked are
`False`. The `-1` index on `rejected_or_unpromoted_candidates` is slightly
fragile (depends on the candidate order remaining stable), but is correct
against the current registry and does not introduce hidden semantics.

**Test 3 (`test_report_documents_quarantine_and_non_authorization`):**
Reads the markdown report and asserts six key phrases are present, including
the `failed_closed` and `prepare_or_replay_failed` status strings and the
"does not authorize" boundary statement. Pure string search — no app logic.

All three tests are artifact-reads or static-registry calls. None require a
live GPU, native library, or hidden application semantics. They correctly pin
the regression boundary: the artifact must show working non-graph counts, both
graph lanes must be closed, and the route registry must carry the quarantine
wording.

---

## Check 5: Continuity With Prior Negative Evidence

Goal3312 (2026-06-04) established the original failure mode: graph replay
returned `[0, 0, 0, 0, 0]` instead of the correct counts, and the Python
wrapper failed closed. Goal3842 (2026-06-08) confirmed that failure still held
on current main in a separate refresh.

Goal4050 records a slightly different — and arguably worse — failure mode on
commit `15c91c6d`: the graph handle now fails during native preparation
(`PreparedOptixPointClosedShapeBatchCountGraph2D.__init__`) rather than
returning incorrect replay counts. Both the report and the artifact trace the
exact exception (`RuntimeError: OptiX error: CUDA error` at `_check_status`,
line 12037 of `optix_runtime.py`). The narrative accurately characterizes this
as "a slightly different from the older Goal3312 zero-count replay" and
concludes correctly that both outcomes point to the same route decision.

The three-lane PIP picture (Numba for one-shot bounded, batch executor for
repeated, graph blocked) is consistent across Goal3842 and Goal4050.

---

## Summary of Findings

| Check | Result | Notes |
|---|---|---|
| No overclaim | Pass | All authorization flags structurally false; claim boundary section explicit |
| Route decision sensible | Pass | Graph quarantined; batch executor and scalar-count executor remain recommended |
| Artifact internally consistent | Pass | Non-blocking: graph timings copy-pasted from executor; status/error fields are authoritative |
| Tests appropriate | Pass | Static artifact reads and registry calls; no hidden app semantics; minor fragility on [-1] index |
| Continuity with prior evidence | Pass | Failure mode escalated from zero-count replay to prepare-time error; routing conclusion unchanged |

**Verdict: `accept`**

No fixes are required before this route guidance is used. The non-blocking
observation about `graph_raw.timings.mode` carrying a batch-executor mode
string is cosmetic only and does not affect any claim or test.
