# Call For Review - Goals5363-5365 X-HD lb / Heavy-Offload Packet

Please strictly review the X-HD `lb` / heavy-cell offload packet.

## Files Under Review

Result docs:

```text
history/internal_docs/goal5363_xhd_lb_heavy_offload_semantics_audit_result_2026-07-09.md
history/internal_docs/goal5364_xhd_lb_trace_gate_author_pair_contract_result_2026-07-09.md
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb0_disabled_raw_dragon_asian_translated_initial_none_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb256_raw_dragon_asian_translated_initial_none_pod.json
```

Implementation / tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5363_lb_heavy_offload_semantics_audit.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5364_lb_trace_gate_author_pair_contract.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5365_rtdl_lb_counterpart_gate.py
tests/goal5363_lb_heavy_offload_semantics_audit_test.py
tests/goal5364_lb_trace_gate_author_pair_contract_test.py
tests/goal5365_rtdl_lb_counterpart_gate_test.py
```

## Summary To Verify

Goal5363:

```text
Author lb semantics:
  lb=0 -> threshold UINT32_MAX -> offload disabled
  lb=N -> offload cells whose point_count > N
  offload row shape = (in_queue index, cell id)

RTDL has a shape-aligned candidate:
  cell_point_count > max_inline_points

No explicit -lb support is claimed.
```

Goal5364:

```text
Author Level-B Dragon->Asian lb pair:
  lb0 HDResult = 52.453487396240234, OffloadingSize=0, WL Heavy Peak=0
  lb256 HDResult = 52.453487396240234, OffloadingSize=27133990,
    WL Heavy Peak=217071920

This is a temporary Level-B input, not exact paper Figure 7.
```

Goal5365:

```text
RTDL same-input counterparts with translate_each_input_to_min_bound:
  lb0/disabled offload:
    HDResult = 52.453491321261296
    abs diff = 3.925e-06
    heavy_offload_peak_rows = 0

  max_inline_points=256:
    HDResult = 52.453491321261296
    abs diff = 3.925e-06
    heavy_offload_peak_rows = 24508120

Behavior-level gate passed at tolerance 5e-6.
Row-count/byte parity is not claimed.
```

Non-parity facts:

```text
author lb256 OffloadingSize = 27133990
RTDL lb256 heavy_offload_peak_rows = 24508120

author WL Heavy Peak = 217071920 bytes
RTDL author-width candidate = 196064960 bytes
```

## Review Questions

1. Does Goal5363 correctly extract author lb semantics and avoid claiming
   support?
2. Does Goal5364 correctly promote the author pair into a contract without
   calling it Figure 7?
3. Did Goal5365 use the POD wrapper and valid remote RTDL native build evidence?
4. Does Goal5365 correctly explain why `--translate-each-input-to-min-bound`
   is required?
5. Does Goal5365 honestly pass only a behavior-level gate: value match,
   lb0 zero offload, lb256 positive offload?
6. Does Goal5365 correctly refuse row-count parity and same-denominator memory
   parity?
7. Is explicit `-lb` support still pending owner/review decision, rather than
   automatically authorized?
8. Are Figure 7, Figure 11, performance ratio, exact paper dataset, and full
   paper reproduction claims all still forbidden?

## Expected Verdict Labels

Choose one:

```text
approve_goals5363_5365_xhd_lb_heavy_offload_packet
approve_with_required_amendments
revise_goals5363_5365_xhd_lb_heavy_offload_packet
block_goals5363_5365_xhd_lb_heavy_offload_packet
```

## Allowed Summary If Approved

```text
RTDL has passed a Level-B behavior gate for lb-style offload: it matches author
HDResult within 5e-6 for disabled-offload and max_inline_points=256
counterparts, and reproduces the zero-vs-positive offload switch.  This does
not prove row-count parity, byte-denominator parity, Figure 7/11, or general
explicit -lb support.
```

## Forbidden Summaries

```text
explicit -lb support without additional owner/review decision
author RT-core parity
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```
