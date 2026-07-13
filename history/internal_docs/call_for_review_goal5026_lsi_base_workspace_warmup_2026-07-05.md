# Call For Review - Goal5026 LSI Base Workspace Warmup

Please review:

- `history/internal_docs/goal5026_lsi_base_workspace_warmup_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5026_query6_lsi_base_workspace_warmup_top4.json`

## Requested Verdict Label

```text
approve_goal5026_lsi_workspace_moved_to_session_with_bounded_claim
```

or, if the accounting is judged misleading:

```text
fail_goal5026_warmup_accounting_or_regime_boundary
```

## Review Questions

1. Is `--prepared-lsi-base-workspace-warmup` correctly scoped to prepared LSI base-session + query-batch mode, rather than cold CLI or paper-text reproduction?

2. Does the implementation avoid same-query replay by using a tiny unmeasured one-chain warmup query before the measured chain-contiguous batches?

3. Does the evidence support the core finding: first measured batch LSI moved from about `1.595s` to about `0.055s`, while the corresponding cost appeared as about `1.612s` of session preparation?

4. Does the report correctly avoid presenting this as a 6-batch net throughput win after charging the new session warmup cost?

5. Are the regime boundaries honest: no cold CLI claim, no paper-text claim, no author parity claim, no 10x claim?

6. Does the code keep this at app-layer orchestration over existing generic prepared-base LSI functionality, without adding RayJoin-specific RTDL core/native semantics?

7. Is the session-phase accounting clean, i.e. timing-only fields are copied into `session_phase_seconds` and count/metadata fields are not misreported as seconds?

8. Is the recommended next target correct: carrier first-call/JIT variance before chasing the smaller persistent sort floor?

## Context For Reviewer

Prior accepted comparison:

```text
Goal5025 native lexsort:
  body_sum        3.012616s
  first_batch     1.825161s
  first_batch_lsi 1.595264s
  later_body_sum  1.187455s
```

Goal5026:

```text
body_sum        2.160384s
first_batch     0.986529s
first_batch_lsi 0.055278s
later_body_sum  1.173854s
session_warmup  1.612296s
```

Thus the body route improves, especially first-query body latency, but the new warmup cost exceeds the 6-batch body saving unless it is legitimately amortized or hidden in prepared-service setup.
