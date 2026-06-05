# Goal3516 v2.8 Evidence Bookkeeping Closure

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3516 closes the evidence-bookkeeping step required by the Goal3515 v2.8
closeout sequence. It does not close v2.8, does not authorize release, and does
not authorize public speedup, broad RT-core speedup, true zero-copy, RayJoin
paper reproduction, `rtdl beats RayJoin`, or full overlay claims.

## Bookkeeping Closed

| Evidence | Status | Review |
| --- | --- | --- |
| Goal3507 JSON prepared-payload cache | committed/pushed | Goal3508 Claude `accept-with-boundary` |
| Goal3509 binary prepared-payload cache | committed/pushed | Goal3510 Claude `accept-with-boundary` |
| Goal3511 steady-state relation stream | committed/pushed | Goal3516 Claude + Gemini `accept-with-boundary` |

## Goal3511 Review Results

Claude review:

- Path:
  `docs/reviews/goal3516_claude_review_goal3511_steady_state_relation_stream_2026-06-05.md`
- Verdict: `accept-with-boundary`
- Required fixes: none
- Noted minor observation: both `single_triangulation_payload_evidence: true`
  and `relation_stream_steady_state_evidence: true` are set in the pod artifact,
  but the Goal3511 schema override takes precedence and this is not a defect.

Gemini backup review:

- Path:
  `docs/reviews/goal3516_gemini_review_goal3511_steady_state_relation_stream_2026-06-05.md`
- Verdict: `accept-with-boundary`
- Required fixes: none

Both reviews agree that Goal3511 correctly separates the monolithic
`relation_discovery` timer from the measured resident relation-column pass:

- Monolithic `relation_discovery`: `1.4563929829746485s`
- Warmups: `0.37163624819368124s`, `0.0074598342180252075s`,
  `0.007164366543292999s`
- Final measured active relation device columns:
  `0.0038709240034222603s`

Both reviews agree that the correct next target is a clear prepared-execution
API/user pattern, not another immediate RT traversal tweak.

## Validation

Local focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3511_overlay_area_steady_state_relation_stream_test tests.goal3509_overlay_area_binary_prepared_payload_cache_test tests.goal3507_overlay_area_prepared_payload_cache_test
```

Result:

```text
Ran 9 tests in 0.008s
OK
```

## Boundaries

All reviewed artifacts preserve:

- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- RayJoin paper reproduction claim: false
- `rtdl beats RayJoin` claim: false
- full overlay claim: false
- hidden partner auto-selection: false
- app-specific native-engine logic: false

## Next Action

Proceed to Goal3517: define the prepared-execution user pattern. That goal
should make the current v2.8 story explicit for users:

```text
prepare -> pack/cache -> warm -> run steady-state -> explain timings
```

The pattern must keep setup, cache load, warmup, steady-state relation stream,
planner, executor, and validation oracle timing separate.
