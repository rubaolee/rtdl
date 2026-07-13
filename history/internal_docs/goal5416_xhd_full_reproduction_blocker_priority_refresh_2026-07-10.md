# Goal5416 — X-HD Full Reproduction Blocker Priority Refresh

## Verdict

```text
completed_full_reproduction_priority_refresh__figure5_level_b_next__lb_line_stopped
```

Goal5416 returns the project to the full X-HD reproduction mainline after
Goal5415 stopped the current explicit `-lb` row-identity path.

It does not run a POD job.  It is a priority and claim-boundary refresh over
existing evidence.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5416_full_reproduction_blocker_priority_refresh.json
```

Key status:

```text
bounded_same_input_value_reproduction_complete = true
level_b_representative_scalar_evidence_strong = true
full_xhd_paper_reproduction_complete = false
exact_paper_dataset_provenance_complete = false
performance_ratio_authorized = false
explicit_lb_line_closed = true
```

## Priority Order

### 1. Exact Input Provenance / Dataset Acquisition

Reason:

```text
Exact paper input files or deterministic regeneration provenance remain the
blocker for full paper and figure claims.
```

This remains first in principle.  However, no concrete exact-input file
candidate is currently ready to probe on POD.

### 2. Figure 5 Level-B Same-POD Matrix

Reason:

```text
Figure 5 has the strongest author log coverage and multiple Level-B
value-matched graphics / geo candidates.
```

Current best next work:

```text
Goal5417_figure5_level_b_same_pod_matrix_plan
```

Goal5417 should define the exact Level-B candidate list and denominator
columns before any new POD run.

Denominators must stay separate:

```text
author Running.AvgTime
author process wall
RTDL route wall
RTDL process wall
input load time
cold vs warm process
```

No author-vs-RTDL ratio is authorized unless a later review accepts a specific
same-denominator comparison.

### 3. Figure Status Closeout Refresh

Figures 7/8/9/10/11 remain blocked or closed under current evidence:

- Figure 7: `lb_comparison` matrix missing; current `-lb` line stopped.
- Figure 8: `tune_radius` logs missing.
- Figure 9: author denominator missing; plot expects four variants but logs
  provide two.
- Figure 10: scalability logs missing.
- Figure 11: memory denominator not aligned.

Do not reopen these without new author matrices, exact inputs, or external
review accepting a narrower diagnostic.

### 4. Generic System Extraction Only When App-Neutral

New RTDL APIs remain allowed only when:

- the need is generic;
- X-HD-specific names and figure semantics stay out of core/native;
- a non-X-HD consumer or behavior proof exists.

## Figure Matrix Summary

| Figure | Current Status | Next Allowed Move |
|---|---|---|
| Figure 5 | Level-B candidates available; full matrix not reproduced | Plan same-POD Level-B matrix with separated denominators |
| Figure 6 | Not claimed | Do not prioritize until exact-input/phase evidence changes |
| Figure 7 | Not reproduced; `lb_comparison` logs missing; current `-lb` line stopped | Reopen only with author `lb=0/lb=256` matrix or external review |
| Figure 8 | Not reproduced; `tune_radius` logs missing | Reopen only with author radius matrix |
| Figure 9 | Closed current line; author denominator missing | Reopen only with missing variants or reviewed mapping |
| Figure 10 | Not reproduced; scalability logs missing | Reopen only with author scalability matrix |
| Figure 11 | Closed; denominator not aligned | Reopen only with denominator-aligned generic worklist |

## Claim Boundary

Authorized:

- priority refresh;
- Figure 5 Level-B next focus;
- explicit `-lb` line remains closed;
- exact dataset remains primary blocker.

Not authorized:

- Figure 5 reproduction;
- Figure 7/8/9/10/11 reproduction;
- author-vs-RTDL performance ratio;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

## Validation

Commands:

```text
$env:PYTHONPATH='src'; py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5416_full_reproduction_blocker_priority_refresh.json > $null
$env:PYTHONPATH='src'; py -m unittest tests.goal5416_full_reproduction_priority_refresh_test tests.goal5415_stop_or_bounded_trace_gate_decision_test tests.goal5414_synthetic_payload_transition_trace_fixture_test
```

Result:

```text
Ran 14 tests in 0.012s
OK
```

The local Python launcher printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Recommended Next Goal

```text
Goal5417_figure5_level_b_same_pod_matrix_plan
```

Goal5417 should be a plan/spec goal, not an immediate performance claim.  It
should choose:

- candidate list;
- author command mode;
- RTDL command mode;
- hardware/POD expectations;
- denominator columns;
- tolerances;
- forbidden summaries.

Only after Goal5417 should a POD execution goal run the actual Figure 5
Level-B same-POD matrix.
