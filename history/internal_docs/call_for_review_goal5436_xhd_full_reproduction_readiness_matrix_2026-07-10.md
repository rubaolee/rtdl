# Call For Review - Goal5436 X-HD Full Reproduction Readiness Matrix

Please strictly review Goal5436.

This goal builds a machine-readable readiness matrix for the actual active
objective: full X-HD paper reproduction with Python/RTDL/partner functionality
matching the author C++/CUDA/OptiX implementation and fair performance
evaluation.

It does **not** run POD, run author code, run RTDL code, contact external
parties, compare outputs, accept exact-equivalence, or upgrade claims.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5436_full_reproduction_readiness_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5436_full_reproduction_readiness_matrix.json
tests/goal5436_full_reproduction_readiness_matrix_test.py
history/internal_docs/goal5436_xhd_full_reproduction_readiness_matrix_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5435_external_response_inbox_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5345_exact_reproduction_readiness.json
```

## Summary To Attack

Current output:

```text
full_xhd_paper_reproduction_ready = false
status = full_xhd_reproduction_not_ready__await_external_response_or_artifact
next_action = send_or_review_action_packet_and_wait_for_classified_external_response
```

Satisfied:

```text
level_b_representative_scalar_evidence = true
```

Not satisfied:

```text
exact_inputs_or_accepted_exact_equivalence
same_input_author_rtdl_gate_on_exact_or_accepted_inputs
full_functional_parity_with_author_visible_behavior
denominator_aligned_performance_matrix
pod_execution_ready_for_next_gate
```

The matrix deliberately distinguishes broad Level-B evidence from full paper
reproduction readiness.

## Claim Boundary To Attack

Authorized:

```text
readiness_matrix_claimed
```

Forbidden:

```text
exact_paper_dataset_reproduction_claimed
figure5_reproduction_claimed
full_xhd_paper_reproduction_claimed
performance_ratio_claimed
author_rt_core_algorithm_equivalence_claimed
pod_execution_claimed
new_rtdl_route_code_added
explicit_lb_reopened
route_micro_optimization_goal_authorized
```

## Stop-Loss Gate G-1

This goal mentions exact input / byte identity / `-lb` only as blocked
requirements. It must not reopen app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: full-reproduction readiness matrix / external-response governance workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5436_full_reproduction_readiness_matrix.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5436_full_reproduction_readiness_matrix.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5436_full_reproduction_readiness_matrix.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5436_xhd_full_reproduction_readiness_matrix_2026-07-10.md history/internal_docs/call_for_review_goal5436_xhd_full_reproduction_readiness_matrix_2026-07-10.md
py -m unittest tests.goal5436_full_reproduction_readiness_matrix_test tests.goal5435_external_response_inbox_gate_test tests.goal5434_water_bg_external_action_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5436_xhd_full_reproduction_readiness_matrix
```

Revise:

```text
revise_goal5436_xhd_full_reproduction_readiness_matrix
```

Block:

```text
block_goal5436_xhd_full_reproduction_readiness_matrix
```

## Review Questions

1. Does the matrix correctly identify current Level-B representative scalar
   evidence as satisfied without promoting it to exact/full reproduction?
2. Does it correctly keep exact inputs or accepted exact-equivalence unsatisfied?
3. Does it correctly keep same-input POD gate readiness unsatisfied?
4. Does it correctly keep full functional parity with author visible behavior
   unsatisfied?
5. Does it correctly keep denominator-aligned performance matrix unsatisfied?
6. Does it correctly report the current external state from Goal5434/5435?
7. Does it keep route micro-optimization and explicit `-lb` unauthorized?
8. Does the script avoid POD, author execution, RTDL route execution, and route
   optimization code?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
10. Are the tests strong enough to prevent the known failure mode: reporting
    broad Level-B scalar evidence as if it completed full X-HD paper
    reproduction?

## Expected Answer Shape

Please answer with:

```text
Verdict: <one requested label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
