# Goal5348 - X-HD Witness Parity / Entrypoint Route Audit Result

## Verdict Label

```text
witness_parity_entrypoint_route_audit_complete__goal5347_witness_blocker_refined
```

## Purpose

Goal5347 correctly identified an "exact-witness vs fast-scalar mode split", but
its matrix made that split look like a broad blocker for the user-facing
`hd_exec`-compatible entrypoint. Goal5348 audits the current runner and POD
artifacts to separate three things that must not be collapsed:

1. the default `hd_exec`-compatible 3-D GPU route;
2. the reviewed exact-witness Level-B / representative artifacts;
3. the faster fast-scalar / early-break route.

## Finding

The `hd_exec`-compatible app entrypoint defaults to the exact-witness route for
3-D GPU inputs:

```text
auto + n_dims=3 + execution=gpu -> cell-mbr-exact-witness
```

The fast-scalar route remains valuable, but it is not the default 3-D GPU
entrypoint and must not be used as evidence of exact per-source witness parity.

## Evidence

Entrypoint source:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Key source facts:

```text
_select_route_label returns public-columnar only for 2-D or CPU;
otherwise auto returns cell-mbr-exact-witness.

cell-mbr-exact-witness witness_contract:
directed_input1_to_input2_per_source_witness_exact_seed_route

cell-mbr-fast-scalar witness_contract:
directed_input1_to_input2_witness_may_be_approximate_for_fast_scalar
```

Exact-witness artifacts:

```text
ModelNet40 all-400:
  artifact: xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
  matched: 400/400
  route_label: cell-mbr-exact-witness
  per_source_witness_exact: true for every case

Stanford representatives:
  Dragon -> HappyBuddha
  Dragon -> AsianDragon scaled 1e-3
  ThaiStatuette scaled 1e-3 -> HappyBuddha
  ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3

All four use route_label=cell-mbr-exact-witness and
per_source_witness_exact=true.
```

Fast-scalar artifact:

```text
xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
```

Fast-scalar facts:

```text
HDResult matches the author rerun scalar.
per_source_witness_exact = false
global_bound_early_break = true
global_bound_early_break_count = 409376 / 437645 sources
```

This is an exact scalar directed-HD route, not an exact per-source witness
route.

## Goal5347 Refinement

Goal5347's witness blocker should be refined as follows:

```text
Not a blocker for:
  hd_exec-compatible 3-D GPU value + exact-witness entrypoint on reviewed
  Level-B / representative artifacts.

Still a blocker for:
  claiming the fast-scalar route has exact per-source witnesses;
  claiming author RT-core algorithm identity;
  claiming exact paper dataset reproduction without exact input artifacts.
```

This means the current system is stronger than Goal5347's broad wording
suggested, while the claim boundary remains strict.

## What This Does Not Prove

Goal5348 does not prove:

```text
full X-HD paper reproduction;
exact paper dataset identity;
author RT-core kernel / algorithm identity;
performance parity or ratio;
that fast-scalar per-source witnesses are exact.
```

## Files

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5348_witness_parity_entrypoint_route_audit.json
tests/goal5348_xhd_witness_parity_entrypoint_audit_test.py
```

## Validation

```text
py -m unittest tests.goal5348_xhd_witness_parity_entrypoint_audit_test
```

Expected:

```text
Ran 5 tests OK
```

## Recommended Next Step

Send Goal5348 together with Goals5345-5347 for strict review. After review,
update the functional parity matrix wording so the witness status is not
overstated in either direction:

```text
entrypoint exact-witness route: covered for reviewed Level-B artifacts;
fast-scalar early-break route: exact scalar value only, witness approximate.
```
