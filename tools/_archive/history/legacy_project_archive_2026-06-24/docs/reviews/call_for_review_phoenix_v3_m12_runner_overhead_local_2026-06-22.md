# Call For Review: Phoenix V3 M12 Local Runner-Overhead Reduction

Date: 2026-06-22
Status: `pending_external_review_not_release`

This packet asks for review of the M12 local generic runner-overhead reduction.
It does not authorize release, public speedup wording, focused POD, or all-app
POD by itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_by_this_packet: false
full_all_app_pod_spend_authorized_by_this_packet: false
```

## Inputs

- M11 consensus:
  `docs/reviews/codex_jason_phoenix_v3_m11_spatial_segment_intersection_2ai_consensus_2026-06-22.md`
- M12 JSON:
  `docs/rebuild/v3/phoenix_v3_runner_overhead_m12_local_2026-06-22.json`
- M12 report:
  `docs/reports/phoenix_v3_runner_overhead_m12_local_2026-06-22.md`
- Microbench evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_runner_overhead_m12_local_microbench_20260622.json`
- Core runner:
  `src/rtdsl/prepared_execution.py`
- Spatial LSI route:
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## Summary

M11 found:

- Spatial LSI productized-runner metadata was clean.
- Spatial LSI was not a speed win.
- New runner-inclusive median was `1.627x` slower than the old hot route.
- M11 review required local generic runner-overhead reduction before more POD.

M12 implements optional generic runner hooks:

- `PreparedExecutionSessionTask.measured_run_prepared`
- `PreparedExecutionSessionTask.finalize_output`

The intended behavior is that measured repeats execute a lightweight hot path,
while rich output payload construction happens exactly once after timing.

Local microbench:

- heavy full runner call: `0.0009929465000168421s`
- heavy finalize-once runner call: `0.0008233700499986298s`
- finalize-once speedup: `1.2059541150646593x`
- saved fraction: `0.17078105418100165`

Local tests passed:

```text
py -3 -m unittest tests.v3_phoenix_runner_overhead_microbench_test tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test
```

## Questions For Reviewer

1. Is M12 a legitimate generic runner-overhead reduction rather than
   app-specific tuning?
2. Are the new hooks safe and bounded enough for V3?
3. Does the local microbench justify one bounded focused POD rerun of the same
   Spatial LSI A/B?
4. Should more local evidence be required before any POD?
5. Does M12 authorize release, public speedup wording, or all-app POD?

## Requested Verdict Labels

Choose exactly one:

- `approve_m12_focused_pod_rerun`: accept M12 and authorize one focused POD
  rerun of the same Spatial LSI A/B only.
- `approve_m12_no_pod_yet`: accept M12 but require more local evidence before
  POD.
- `revise_m12_before_decision`: require code/report changes before deciding.
- `reject_m12`: M12 violates scope or does not solve the overhead problem.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- focused POD authorization: yes/no
- all-app POD authorization: yes/no
- whether M12 can be treated as a generic runner-overhead reduction

## Goal-Level Decision Audit

Decision: request review before any post-M12 POD rerun.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish move would be to treat a local microbench as POD evidence.
3. Was there another path?
   Yes: immediately rerun POD, but that would violate the M11 consensus.
4. Can I now try a different path?
   Yes: get review and only then run a bounded focused rerun if authorized.
