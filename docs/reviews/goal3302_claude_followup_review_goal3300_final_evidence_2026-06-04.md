# Goal3302 Claude Follow-Up Review — Goal3300 Final Evidence Packet
**Review date:** 2026-06-04
**Commit reviewed:** `0f70b017` (report, artifact, tests) / app and runner at `56a91c89`
**Prior review:** `docs/reviews/goal3301_claude_review_goal3300_boundary_event_count_route_2026-06-04.md`
**Verdict:** `accept`

---

## Summary

Both required-before-benchmark findings from Goal3301 are closed in code, tests,
and artifact. The report correctly characterizes the boundary-event route as a
negative PIP performance result. All claim-boundary flags remain False. The
next-primitive conclusion is well-supported by the split timing evidence in the
artifact.

---

## Findings by Severity

### Low — `point_order_mode` + boundary-event combination path is still not unit-tested

This was a "required before benchmark use" item in Goal3301 at low severity. It
remains unaddressed: no test exercises
`count_mode=boundary_event_point_id_count_device_columns` with a non-natural
`point_order_mode`. The existing tests in both
`tests/goal3300_rayjoin_boundary_event_count_route_test.py` and
`tests/goal2327_rayjoin_prepared_route_contract_test.py` use only the natural
ordering.

The pod artifact records `point_order_mode: "natural"` for the PIP run, which
is consistent. A reorder regression would only be detected on-pod. This finding
does not block acceptance at the current evidence level; it should be resolved
before any non-natural ordering is benchmarked on the boundary-event path.

---

## Goal3301 Finding Closure

### Finding 1 (Medium) — Disclosure guard did not cover warmup: CLOSED

**Code:** `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py:321-327`

`validate_rtdl_sample_payload` is now called unconditionally for every sample,
warmup and repeat alike:

```python
for index in range(warmup):
    ...
    validate_rtdl_sample_payload(workload=workload, count_mode=count_mode, payload=one())
for index in range(repeat):
    ...
    payload = one()
    validate_rtdl_sample_payload(workload=workload, count_mode=count_mode, payload=payload)
```

**Test:** `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py:403-427`

`test_rtdl_pip_boundary_event_count_route_rejects_missing_disclosure_even_in_warmup`
supplies `warmup=1, repeat=1` and omits `boundary_event_contract_not_positive_membership`
from the payload. It asserts `RuntimeError("did not disclose non-membership contract")`
is raised. This exercises the failure branch directly through the warmup path,
which is precisely the gap identified in Goal3301.

Both the warmup-coverage gap and the untested failure-branch gap are now closed.

---

### Finding 2 (Low / Observability) — `prepared_query_sec` conflated both phases: CLOSED

**Code:** `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py:550-570`

The two phases are now timed separately:

```python
boundary_event_columns = _phase_time(
    phases,
    "boundary_event_device_columns_sec",
    lambda: prepared.first_boundary_crossing_device_columns(packed_points),
)
...
boundary_event_count_columns = _phase_time(
    phases,
    "boundary_event_grouped_count_sec",
    lambda: boundary_event_columns.grouped_count_by_point_id_device_columns(...),
)
...
phases["prepared_query_sec"] = (
    phases["boundary_event_device_columns_sec"]
    + phases["boundary_event_grouped_count_sec"]
)
```

`prepared_query_sec` is now the compatibility sum of the two split keys, not a
single fused timing. Both split keys are required to be present.

**Contract test:** `tests/goal2327_rayjoin_prepared_route_contract_test.py:220-227`

```python
self.assertIn("boundary_event_device_columns_sec", payload["phases_sec"])
self.assertIn("boundary_event_grouped_count_sec", payload["phases_sec"])
self.assertIn("prepared_query_sec", payload["phases_sec"])
self.assertAlmostEqual(
    payload["phases_sec"]["prepared_query_sec"],
    payload["phases_sec"]["boundary_event_device_columns_sec"]
    + payload["phases_sec"]["boundary_event_grouped_count_sec"],
)
```

**Runner:** `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py:347-349`

The runner extracts both split keys into `boundary_event_device_columns_ms` and
`boundary_event_grouped_count_ms`.

**Artifact:** Both fields are populated with 15 samples in the PIP section of
`docs/reports/goal3300_boundary_event_same_slice_pod_2026-06-04.json`. The split
medians are 3.763 ms and 0.133 ms respectively, and their sum (3.896 ms) matches
`prepared_query_ms.median` (3.894 ms) within floating-point rounding.

---

### Incidental — `event_capacity` tight-capacity pattern removed

Goal3301 flagged `event_capacity=max(1, packed_points.count)` at app line 586 as
underdocumented for coincident-edge geometry. That argument is now absent entirely
from the `first_boundary_crossing_device_columns` call (no `event_capacity`
parameter is passed). The artifact confirms no overflow occurred on the 512-point
PIP slice that produced 3961 events (≈7.7 events per probe point on average).
The practical concern from Goal3301 is resolved by the change, though the
underlying capacity behavior is now implicit in the runtime default rather than
documented at the call site.

---

## Review Answers

### Q1 — Were the two Goal3301 findings closed in code, tests, and artifact?

**Yes.** Both required-before-benchmark findings are closed.

- The disclosure guard now fires on every call including warmup, and the failure
  branch is exercised by a named test that verifies `RuntimeError` is raised when
  the disclosure flag is missing from a warmup sample.
- Both boundary-event phases are recorded as separate timing keys; the contract
  test enforces their presence and sum equality; the runner extracts them; the
  artifact contains both with 15 measured samples.

---

### Q2 — Does the report correctly state that the boundary-event route is a negative PIP performance result?

**Yes.** The report header reads "Status: complete with RTX A5000 pod evidence;
negative for PIP performance." The comparison table labels the PIP row as
"boundary-event count, not PIP membership" with a 17.52× ratio against RayJoin.
The interpretation block names the bottleneck precisely: 3.76 ms median to produce
the boundary-event stream against a 0.22 ms RayJoin query time. The conclusion
("This is a useful contract probe and a poor PIP performance route") is accurate
and clearly stated.

The report also draws the correct contrast with the Goal3294 tuned PIP route
(approximately 0.361 ms median on the same pod), attributing the difference to
counting inside the closed-shape membership path rather than materializing a
boundary-event stream.

---

### Q3 — Does the artifact preserve the app-agnostic boundary and all claim blocks?

**Yes.** The artifact at `docs/reports/goal3300_boundary_event_same_slice_pod_2026-06-04.json`
contains:

- `claim_boundary` with all six flags False. The test at
  `tests/goal3300_rayjoin_boundary_event_count_route_test.py:45` programmatically
  asserts `assertFalse(any(artifact["claim_boundary"].values()))`.
- `status: "pass_with_optimization_gap"` — not `pass`.
- `count_contract_status: "rtdl_boundary_event_count_not_pip_membership"` for
  the PIP row.
- `rayjoin_positive_assignment_count_available: false` for PIP — the upstream
  binary does not expose it.
- `native_phase_samples` for all 15 PIP measured repeats, each with
  `mode: "boundary_event_device_columns"` and `candidate_download: 0.0`,
  confirming device-resident execution with no candidate download.

The app-agnostic boundary is preserved: the app's native calls are to
`first_boundary_crossing_device_columns` and
`grouped_count_by_point_id_device_columns` — generic closed-shape primitives.
RayJoin interpretation stays in the Python benchmark layer.

---

### Q4 — Is the next-primitive conclusion sound?

**Yes.** The split timing evidence directly supports it. The bottleneck is
boundary-event production (3.763 ms median), not continuation: the grouped-count
phase is 0.133 ms median — about 3.5% of the total. Producing 3961 event rows
for 512 probe points (≈7.7 per point) without any candidate download is the
costly step.

The conclusion — that a fused generic closed-shape first-hit or predicate-count
path that can stop or reduce inside traversal without writing a boundary-event
row stream is the correct next primitive — is well-supported. Boundary-event
materialization is the wrong route for PIP membership-count performance.
The finding is useful: it rules out a plausible optimization direction and
narrows the design space for the next primitive.

---

## What is Well Done

- The warmup-guard and split-timing fixes are both small, targeted, and do not
  introduce new abstractions. The `validate_rtdl_sample_payload` helper calls
  cleanly from both loops.
- The failure-branch test uses `warmup=1, repeat=1` to trigger the guard on the
  first warmup call, which is the exact regression scenario that Goal3301 flagged.
- The `prepared_query_sec` compatibility sum is computed from the two named keys
  rather than being re-timed separately, so there is no double-execution cost and
  the sum identity is verifiable by inspection and test.
- The artifact `native_phase_samples` for the PIP run contains all 15 measured
  repeats with full native-phase structure, including `emitted_count: 3961`
  and `candidate_download: 0.0` on every sample. This is more evidence than the
  median alone.
- The three outlier samples (indices 4, 5, 6) in `boundary_event_device_columns_ms`
  (21 ms, 12 ms, 168 ms) are faithfully retained in the artifact and do not
  distort the median (3.763 ms). This is correct artifact hygiene.
- The runner test for the boundary-event route now covers split timing extraction
  directly (lines 395-401), confirming that both `boundary_event_device_columns_ms`
  and `boundary_event_grouped_count_ms` are populated from the right phase keys.
