# Review Debt: V4 Primitive Grouped-I64 Candidate

Date: 2026-06-24
Status: Claude review received; Antigravity CLI output capture blocked; POD gate passed

## Requested Review

Packet:

- `future/v4/reviews/call_for_review_v4_primitive_grouped_i64_candidate_2026-06-24.md`

Expected verdict labels:

- `accept_candidate_continue_to_catalog_promotion_decision`
- `accept_with_required_amendments_before_catalog_decision`
- `reject_candidate_wrong_v4_boundary`
- `blocked_insufficient_evidence`

## Attempted Reviewer

Antigravity CLI:

```powershell
C:\Users\Lestat\AppData\Local\agy\bin\agy.exe --print ...
```

The CLI authenticated and contacted the backend, but returned empty stdout in
print mode. A minimal prompt probe also returned empty stdout. The explicit log
showed successful silent auth and generation requests, but did not expose the
model response body.

After the RTX A5000 POD gate passed, the CLI was retried with a minimal
`--print "Reply with exactly: antigravity-ok"` prompt and `--print-timeout 60s`.
It again exited successfully with empty stdout, so no review verdict can be
recorded from this channel yet.

Claude CLI:

- Raw review: `future/v4/reviews/claude_v4_primitive_grouped_i64_candidate_review_2026-06-24.raw.md`
- Verdict: `accept_with_required_amendments_before_catalog_decision`

Required amendments from Claude before any catalog-promotion decision:

1. Add a GPU-mode candidate regression path so the grouped-i64 surface is
   exercised by the catalog gate machinery before promotion. Status: closed by
   `scripts/v4_catalog_regression_gate.py --mode gpu --include-candidates` and
   RTX A5000 evidence
   `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`.
2. Keep promotion atomic: when and only when promoted, move it from candidate
   catalog to measured catalog with Torch measured and update the frontdoor
   measured-surface count from 3 to 4.
3. State the OptiX ABI scope explicitly; this POD validated OptiX 8.0 headers,
   while OptiX 9.1 failed against driver 570.195.03.
4. Document group-width coverage or expand it beyond `group_width=16`.

## Handling

This is recorded as partially closed review debt. Claude has reviewed the
candidate and allowed continuation toward a catalog-promotion decision after
required amendments. Antigravity remains unavailable as an output-capturing
review channel. The implementation remains a candidate only and does not move
into the measured V4 catalog or release scope until the amendments, promotion
decision, and required review consensus are obtained. The RTX A5000 POD gate has
now passed and is recorded at:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`

## Non-Authorization

This debt record does not authorize:

- V4 release
- measured catalog promotion
- public speedup claims
- RT-core performance claims
- true-zero-copy wording
- Tier-3 callback claims
