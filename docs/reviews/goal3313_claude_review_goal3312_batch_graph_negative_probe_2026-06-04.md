# Goal3313 Claude Review of Goal3312 Batch Graph Negative Probe

Date: 2026-06-04
Reviewer: Claude (independent)
Verdict: **accept-with-boundary**

---

## Findings by Severity

### Blockers

None.

### Medium

**M1 — Observed replay counts not stored as a structured field in the JSON artifact.**
The replay result `[0, 0, 0, 0, 0]` is recoverable only by parsing the embedded tuple strings in
the `"error"` field (`"prepared OptiX batch-count graph replay failed validation: (0, 0, 0, 0, 0)
!= (2, 2, 2, 2, 2)"`). There is no explicit `"replay"` array key. The data is present and the
test at line 76 checks `artifact["graph_status"] == "failed_closed"` and
`artifact["error"]` contains `"failed validation"`, but a programmatic consumer expecting a
`replay` field would miss the zero-count evidence. Future negative-probe artifacts should add a
`"replay"` key alongside `"batch"` to make the mismatch machine-readable without parsing error
strings.

**M2 — `CU_STREAM_CAPTURE_MODE_GLOBAL` used in constructor.**
`workloads.cpp` line 7624 calls `cuStreamBeginCapture(stream, CU_STREAM_CAPTURE_MODE_GLOBAL)`.
GLOBAL mode causes any operation on any non-blocked stream in the process during the capture
window to be included in the graph. In a single-threaded probe this is benign, but in a
concurrent or multi-pipeline runtime it could silently capture unrelated operations and produce a
non-deterministic graph. The graph already fails validation on the A5000 (graph replay returns
zeros), so there is no current safety consequence. Future CUDA-graph work on this path should
use `CU_STREAM_CAPTURE_MODE_THREAD_LOCAL` or `RELAXED` to constrain capture scope.

### Low

**L1 — `validate_on_prepare=False` bypass exposes a known-zero-replay handle.**
The `PreparedOptixPointClosedShapeBatchCountGraph2D` constructor accepts
`validate_on_prepare: bool = True`. When `False`, the caller receives a graph handle that
replays zeros on the A5000 without any runtime error. The default is `True` and this is an
internal experimental path, so the practical risk is low. The constructor or class docstring
should explicitly warn that `validate_on_prepare=False` is unsafe given the confirmed A5000
replay failure, so that any future caller opting in understands the known failure mode.

**L2 — Validation error message truncated to first 5 elements.**
On construction failure the message is formatted as
`f"{observed[:5]} != {expected[:5]}"`. For `request_count > 5` the mismatch for indices 5..N is
silently dropped from the message. Not a correctness issue (validation already fails) but a debug
ergonomics issue if this path is exercised with larger request counts.

**L3 — Batch phase globals record cumulative sum after replay (inherited pattern from Goal3310).**
In `replay_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d_optix`
(workloads.cpp lines 7698–7705), `g_optix_last_closed_shape_raw_candidate_count` and
`g_optix_last_closed_shape_emitted_count` are set to `total_count` — the sum across all
`request_count` slots. Any caller that reads these globals after a replay expecting a per-request
count will observe N× the per-request value. This matches the pattern noted in Goal3311 M1 for
the batch scalar-count path and is not a new regression.

---

## Review Questions

### Q1 — Does the graph surface remain generic and app-agnostic?

Pass. The native struct
`PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D` (workloads.cpp line 7534) and
all three C ABI functions in `rtdl_optix_api.cpp` (lines 467, 489, 503) operate exclusively on
`PreparedShapePairRelationBuild*` and `PreparedPointProbeColumns2D*` — generic handles with no
RayJoin-specific fields. The Python class `PreparedOptixPointClosedShapeBatchCountGraph2D` and
its factory method `prepare_device_filtered_prepared_points_batch_graph` carry the same
generic naming. The test at line 49 asserts `"rayjoin"` does not appear (case-insensitive) in the
graph struct body and passes on pod. No app-specific logic crosses the engine boundary.

### Q2 — Does the implementation fail closed, structurally and in the Python wrapper?

Pass. Two layers of fail-closed behavior are present:

**Native layer**: The `api.cpp` wrapper at line 481 initializes `*graph_out = nullptr` before
calling the constructor. On any exception thrown during construction (capture failure, node count
mismatch, cuGraphInstantiate failure) the catch block in the constructor destroys any partially
created `graph_exec`, `graph`, and `stream` resources and re-throws, leaving `*graph_out = nullptr`
and the caller with no dangling handle.

**Python layer**: `PreparedOptixPointClosedShapeBatchCountGraph2D.__init__` with the default
`validate_on_prepare=True` calls `count_device_filtered_prepared_points_batch` for the trusted
expected counts and then calls `self.replay()`. If `observed != expected`, it calls `self.close()`
(which destroys the native handle via the destroy symbol) sets `self._closed = True`, and raises
`RuntimeError`. The JSON artifact confirms `"graph_status": "failed_closed"` and the error string
`"prepared OptiX batch-count graph replay failed validation: (0, 0, 0, 0, 0) != (2, 2, 2, 2, 2)"`
matches this path. No caller of the public Python API can obtain a usable handle when replay
disagrees with the trusted batch-count path.

### Q3 — Does the report accurately record the negative result?

Pass with one note (see M1).

The report records: `exact=2`, `trusted single=2`, `trusted batch=[2,2,2,2,2]`, `graph replay
observed=[0,0,0,0,0]`, `wrapper status=failed_closed`. These match the JSON artifact fields
exactly. The timing artifact has `"mode": "prepared_points_device_filtered_batch_graph_replay"`,
consistent with the Python mode mapping at `mode_value == 10` (optix_runtime.py line 6434–6435).
The report does not claim a performance win; the status line explicitly reads "fail-closed negative
probe; not accepted as a performance optimization." The single sentence "This is negative evidence
plus a fail-closed guard, not a performance win" in the report boundary section is confirmed by
the test at line 69 (`assertIn("not a performance win", report)`).

The one gap: the JSON `"timings"` block records `"raw_candidate_count": 0` and
`"emitted_count": 0` for the replay path. These zeros reflect the cumulative-sum global state
after a replay that returned zeros everywhere (L3), not a separately recorded replay-result array.
The replay values are embedded only in the `"error"` string (M1).

### Q4 — Are claim boundaries, timing mode labels, commit hash, pod build/test evidence, and future-version notes consistent?

Pass.

- **Commit hash**: JSON `"rtdl_commit": "5970995b1b858f75af57da16f03dba0ce07f6d4b"` matches
  the report provenance section. This is the "Goal3312 fail-close batch graph replay validation"
  commit in the recent log, which is the appropriate evidence commit.
- **GPU/driver**: `"NVIDIA RTX A5000, 580.126.09"` consistent with the Goal3310 and Goal3312
  report pod sections.
- **Pod build/test**: `make build-optix` passed; `tests.goal3312_prepared_point_batch_graph_count_test` 3/3 passed; `tests.goal3310_prepared_point_batch_scalar_count_test` 5/5 passed. All evidence checkboxes in the report are present and consistent.
- **Timing mode label**: `reset_closed_shape_membership_phase_timings(10u)` (workloads.cpp line
  7688) → Python `mode_value == 10` → `"prepared_points_device_filtered_batch_graph_replay"`
  (optix_runtime.py line 6434). JSON `"mode": "prepared_points_device_filtered_batch_graph_replay"`.
  Consistent end-to-end.
- **Claim-boundary flags**: All six flags are `false` in the JSON; `assertFalse(any(artifact["claim_boundary"].values()))` passes.
- **Future-version note**: `docs/research/future_version_to_do_list.md` line 28 reads
  "Do not use this graph path as performance evidence until the native replay mismatch is fixed."
  This is present and consistent with the report interpretation section.

### Q5 — Should this graph surface remain as a guarded experimental/negative path, or quarantined further?

Pass — the current quarantine is adequate.

The graph surface is:
1. Gated by a Python symbol lookup (`_find_optional_backend_symbol`) that returns `None` if the
   backend is not built with the graph symbols, preventing silent failures.
2. Validated on construction by default (`validate_on_prepare=True`), so no caller can receive a
   handle that replays zeros without explicitly opting out.
3. Fail-closed at the native level: the C ABI initializes `*graph_out = nullptr` and cleans up
   on exception.
4. Documented as a negative result in the report, future-version list, and JSON artifact.

No additional quarantine (removal from the ABI, additional build gate) is required at this stage.
The surface is experimental and not on any public or release path. Removing it prematurely would
delete the evidence of the replay failure and the fail-closed guard that was hard-won in this
goal.

The `validate_on_prepare=False` opt-out (L1) should be accompanied by a documentation warning
before any further development extends this path.

### Q6 — Is the recommended next direction sound?

Pass. Goal3310 showed the native scalar-count traversal floor settling near `0.241 ms` per
request; batching at 32 requests reduced host overhead to effectively zero, confirming that
further improvement requires a reduction in native traversal cost. Goal3312 tested CUDA graph
replay as one candidate for that reduction and found it does not currently work correctly on the
A5000.

The recommended next direction — a more compact generic closed-shape predicate-count primitive —
is consistent with the analysis in `docs/research/future_version_to_do_list.md` (lines 13–19,
the "Generic Closed-Shape Boundary Selection" entry) and with the Goal3311 review Q6 finding.
Attempting CUDA graph replay further would require first understanding why `cuGraphLaunch`
produces zeros for an OptiX pipeline with device-prefiltered prepared points; that investigation
is correctly deferred to a future goal rather than blocking the current release preparation track.

---

## Claim Boundaries

This review does not authorize and explicitly preserves the existing prohibition on:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims;
- app-specific native-engine direction.

Goal3312 is negative evidence plus a fail-closed guard. The graph replay path produced zeros on a
live A5000 smoke while trusted single and batch-count paths produced the correct count of 2. The
Python wrapper correctly failed closed, and the JSON artifact records all six claim-boundary flags
as `false`. This review confirms that characterization and makes no additional performance
authorization.

The graph handle (`PreparedOptixPointClosedShapeBatchCountGraph2D`) must not be used as
performance evidence and must not be promoted to any public or release-path surface until the
native replay mismatch is understood and the validation passes on hardware.
