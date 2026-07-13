# Call For Review - Goal5364 X-HD lb Trace Gate Author-Pair Contract

Please strictly review Goal5364.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5364_lb_trace_gate_author_pair_contract.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
tests/goal5364_lb_trace_gate_author_pair_contract_test.py
history/internal_docs/goal5364_xhd_lb_trace_gate_author_pair_contract_result_2026-07-09.md
```

Input evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
```

## Review Questions

1. Does Goal5364 correctly preserve Goal5296 as a Level-B temporary-input
   author-only diagnostic, not Figure 7 reproduction?
2. Does it correctly verify that author `lb=0` and `lb=256` return equal
   `HDResult` on the Dragon -> AsianDragon pair?
3. Does it correctly verify that author `lb=0` has zero heavy offload while
   author `lb=256` has positive `LargeCells`, `OffloadingSize`, and
   `WL Heavy Peak`?
4. Does the RTDL counterpart contract require same-input `lb0` and `lb256`
   runs instead of silently treating existing RTDL artifacts as sufficient?
5. Does it correctly require RTDL `lb0` to produce zero offload fields and RTDL
   `lb256` to produce positive offload fields?
6. Does it avoid claiming explicit `-lb` support before the RTDL counterpart
   run exists?
7. Does it avoid Figure 7 / Figure 11 / performance / same-denominator claims?
8. Is the next step correctly identified as running RTDL lb0/lb256 counterpart
   on the same Level-B input?

## Expected Verdict Labels

Choose one:

```text
approve_goal5364_lb_trace_gate_author_pair_contract
approve_with_required_amendments
revise_goal5364_lb_trace_gate_author_pair_contract
block_goal5364_lb_trace_gate_author_pair_contract
```

## Allowed Summary If Approved

```text
The author Level-B lb=0/lb=256 pair is ready as a contract for the next RTDL
counterpart run. Explicit -lb remains unsupported until that counterpart gate
passes.
```

## Forbidden Summaries

```text
explicit -lb support
author RT-core parity
Figure 7 reproduction
Figure 11 reproduction
same-denominator memory parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```
