# Goal3516 — Claude Independent Review of Goal3511 Steady-State Relation Stream

**Review date:** 2026-06-05
**Reviewer:** Claude Sonnet 4.6 (independent, read-only)
**Goal under review:** Goal3511 — steady-state timing evidence for the prepared active relation device-column stream
**Commits reviewed:** `b156242b` (Goal3511), `51f98850` (Goal3516 bookkeeping)
**Verdict:** `accept-with-boundary`

---

## Files Reviewed

- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` — warmup flag and timing instrumentation
- `tests/goal3511_overlay_area_steady_state_relation_stream_test.py` — test suite
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_2026-06-05.md` — author report
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json` — measured read pod
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_cache_write_pod_2026-06-05.json` — cache write pod (cross-reference)
- Prior context: Goal3447, Goal3507, Goal3509 reports and reviews

---

## Question 1: Separation of monolithic `relation_discovery` from the active relation device-column pass

**Finding: separation is correctly implemented and mechanically enforced.**

The executor (`goal3492_...executor.py` lines 519–603) wraps the entire OptiX prepared-context
lifecycle — context creation, packed left preparation, all warmup passes, the measured final
pass, bounds filter, active shape ordinals, and relation ordinal download — under a single
`discovery_start` / `relation_discovery_sec` outer timer. This is the monolithic timer.

The `--relation-column-warmup-repeats` flag (lines 541–551) inserts n discard passes before
the measured pass, each timed independently into `relation_column_warmup_secs`. The final
measured pass (lines 552–555) is timed into `active_relation_device_columns_sec` with a
`cp.cuda.Stream.null.synchronize()` fence on both sides.

The output dict (lines 1094–1096) exposes all three fields separately:
- `timing_sec.relation_discovery` — monolithic outer timer
- `timing_sec.active_relation_device_columns_warmup_secs` — list of per-warmup times
- `timing_sec.active_relation_device_columns` — final measured pass only

The `--relation-stream-steady-state-evidence` flag (lines 956–998, 999–1010) correctly
overrides the schema and goal label to `rtdl.goal3511.overlay_area_steady_state_relation_stream.v1`
and `goal: 3511` regardless of any other evidence flags that may also be set. The override
takes unconditional precedence via the leading branch.

The report's statement that "the monolithic `relation_discovery` timer contains setup, first-use
runtime behavior, and surrounding host orchestration" is consistent with the code: the outer
timer includes context creation, packed left preparation, and warmup passes alongside the
measured pass, so it cannot be interpreted as steady-state RT traversal time.

---

## Question 2: Pod artifact support for reported steady-state numbers

**Finding: every reported number matches the pod artifact exactly.**

From `goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`:

| Reported value | Reported | Pod artifact | Match |
|---|---:|---:|---|
| Monolithic `relation_discovery` | 1.4564 s | 1.4563929... s | ✓ |
| Warmup 1 | 0.3716 s | 0.37163624... s | ✓ |
| Warmup 2 | 0.00746 s | 0.0074598... s | ✓ |
| Warmup 3 | 0.00716 s | 0.007164366... s | ✓ |
| Final measured active relation columns | 0.00387 s | 0.0038709240... s | ✓ |

All test assertions in
`test_pod_artifact_separates_steady_state_relation_columns_from_setup` pass against
the pod values:
- `warmups[0] > 0.1` → 0.3716 > 0.1 ✓
- `min(warmups[1:]) < 0.01` → 0.00716 < 0.01 ✓
- `active_relation_device_columns < 0.005` → 0.00387 < 0.005 ✓
- `relation_discovery > 1.0` → 1.4564 > 1.0 ✓

The cache write pod (schema `rtdl.goal3509...`, `goal: 3509`, no warmup passes) shows
`active_relation_device_columns: 0.33553s` — a first-call cold value — which independently
confirms that the warmup separation in the Goal3511 read pod is genuine. The two-order-of-
magnitude drop from warmup 1 (0.3716 s) to warmup 2 (0.00746 s) and from warmup 2 to the
final measured pass (0.00387 s) is consistent with JIT compilation completing on the first
call and the resident column path reaching thermal steady state by the second pass.

The `relation_stream_steady_state_evidence: true` field and `relation_column_warmup_repeats: 3`
in the pod confirm the run was correctly invoked with `--relation-column-warmup-repeats 3
--relation-stream-steady-state-evidence`.

---

## Question 3: Absence of overstatement

**Finding: no overstatement found in code, artifact, or report.**

The report states explicitly:

> "The slower monolithic `relation_discovery` timer should not be described as RT traversal
> time. It contains setup, first-use runtime behavior, and surrounding host orchestration."

> "Goal3511 does not authorize release, public speedup wording, broad RT-core speedup
> wording, true zero-copy wording, RayJoin paper reproduction claims, `rtdl beats RayJoin`
> wording, or full overlay claims."

The pod artifact `claim_boundary` carries all seven prohibited fields as `false`:
```json
"claim_boundary": {
  "full_overlay_area_claim_authorized": false,
  "public_speedup_claim_authorized": false,
  "rayjoin_paper_reproduction_claim_authorized": false,
  "release_authorized": false,
  "rt_core_speedup_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "true_zero_copy_claim_authorized": false
}
```

The test `test_pod_artifact_separates_steady_state_relation_columns_from_setup` (lines 65–67)
mechanically enforces all claim_boundary fields are `false`. The executor metadata,
bounds-filter metadata, active-shape-ordinal metadata, and task planner summary all carry
the same `false` contract fields.

The Goal3511 schema name itself — `overlay_area_steady_state_relation_stream` — is precise
and does not claim a general speedup. The timing result is presented as a primitive-level
observation scoped to this public-CDB dataset on this RTX A5000 pod.

---

## Question 4: Correctness stability

**Finding: all correctness metrics are stable and consistent with the prior goal chain.**

From the pod artifact, verified against the test assertions and prior artifacts:

| Metric | Goal3511 pod | Test assertion | Prior (Goal3509) | Stable |
|---|---|---|---|---|
| `relation_row_count` | 4,543 | `== 4543` | 4,543 | ✓ |
| `candidate_relation_row_count` | 2,274 | `== 2274` | 2,274 | ✓ |
| `supported_relation_row_count` | 2,149 | `== 2149` | 2,149 | ✓ |
| `exact_positive_row_count` | 1,086 | `== observed` | 1,086 | ✓ |
| `observed_positive_row_count` | 1,086 | `== exact` | 1,086 | ✓ |
| `planned_triangle_pair_count` | 4,070,240 | `== 4070240` | 4,070,240 | ✓ |
| `total_area_abs_error` | 9.228e-09 | `< 1.0e-8` | 9.228e-09 | ✓ |
| `max_relation_abs_error` | 1.041e-09 | `< 2.0e-9` | 1.041e-09 | ✓ |
| `unsupported_positive_relation_row_count` | 0 | — | 0 | ✓ |

Left and right triangle counts (41,178 / 32,087), component counts (3,117 / 2,623), and
geometry status distributions (make_valid/valid) all match the prior cache-chain artifacts.
The workload has not drifted.

The three `unsupported_relation_row_count` rows are present and unaffected; none have
positive exact area, consistent with all prior runs.

---

## Question 5: Soundness of the next-step interpretation

**Finding: the next-step interpretation is sound and grounded in the evidence.**

The pod shows:
- First-call warmup: 0.3716 s (JIT + device setup)
- Second-call warmup: 0.00746 s (warm but not fully steady)
- Third-call warmup: 0.00716 s (steady state reached)
- Final measured pass: 0.00387 s (steady state, consistent with Goal3447's 0.00359 s median)

This pattern confirms the resident relation-column primitive itself is fast. The ~1.46 s
monolithic `relation_discovery` cost is dominated by setup, JIT, and orchestration rather
than by the OptiX traversal kernel for this dataset.

The report's conclusion — that the next target is "a clearer prepared-execution API that
lets users keep right-side scenes, packed left-side columns, relation columns, payload
caches, and continuation inputs alive across repeated calls while recording setup versus
steady-state timing honestly" — is the correct inference from this evidence. It identifies
the lifetime/ownership gap as the next addressable problem, not RT traversal throughput.
This is consistent with what Goal3447 already established about the resident column
primitive's cost floor.

The interpretation does not overclaim "RTDL is ready for this user pattern today" — it
frames the evidence as motivation for a future API direction. That is the right level of
confidence for single-pod, single-dataset evidence.

---

## Question 6: Required fixes before Goal3516 evidence bookkeeping can close

**Finding: no required fixes.**

All six review dimensions are satisfied:

1. **Schema override is correct.** The `--relation-stream-steady-state-evidence` flag takes
   the leading branch in the schema/goal dispatch (lines 956–998, 999–1010), producing
   the correct `rtdl.goal3511...` label regardless of other flags. No labeling confusion.

2. **Warmup timing is cleanly implemented.** The warmup loop, the measured pass, and the
   monolithic outer timer are mechanically separate. The output dict exposes all three
   layers. The test enforces numeric bounds on each.

3. **Pod numbers are internally consistent.** The write pod (no warmup, cold first call)
   and the read pod (3 warmups, sub-5ms final) form a coherent pair that independently
   validates the warmup separation claim.

4. **Correctness chain is unbroken.** All invariants match Goals 3507, 3509, and the
   relation-row counts match Goal3447.

5. **All boundary fields are false** at every level (top-level, executor metadata,
   task planner summary, sub-operation metadata). The test enforces this mechanically.

6. **Minor observation (no fix required):** The pod artifact has
   `single_triangulation_payload_evidence: true` alongside
   `relation_stream_steady_state_evidence: true`, indicating both flags were passed at
   invocation. Because the Goal3511 schema/goal override takes unconditional precedence,
   the artifact is correctly labeled. The `single_triangulation_payload_evidence` field
   is an informational metadata field and does not affect the evidence interpretation.
   This is not a defect.

---

## Verdict

**`accept-with-boundary`**

Goal3511 correctly separates the monolithic `relation_discovery` timer from the resident
active relation device-column pass by adding explicit warmup passes and an isolated
measured-pass timer. The pod artifact supports all reported numbers exactly. No overstatement
of RT traversal speedup, whole-app speedup, public speedup, or RayJoin reproduction appears
in the code, artifact, or report. Correctness is stable across the full goal chain.
The next-step interpretation is grounded in the evidence and points to the right problem
(prepared-execution API lifetime, not traversal throughput).

Goal3511 is valid timing-and-evidence hygiene for the v2.8 internal closeout sequence. It
does not authorize release, public speedup wording, broad RT-core speedup wording, true
zero-copy wording, RayJoin reproduction claims, or `rtdl beats RayJoin` wording.
Goal3516 evidence bookkeeping may close.
