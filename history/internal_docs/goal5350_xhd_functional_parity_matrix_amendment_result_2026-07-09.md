# Goal5350 - X-HD Functional Parity Matrix Amendment

## Verdict Label

```text
functional_parity_matrix_amended_after_witness_and_variant_audits__full_parity_still_false
```

## Purpose

Goal5347 created a broad functional feature parity matrix. Goals5348 and 5349
then refined two important rows:

```text
Goal5348: exact-witness entrypoint vs fast-scalar exact-value-only route
Goal5349: hd_exec variant names accepted for value output, but not algorithm parity
```

Goal5350 records those refinements in one amended matrix artifact so future work
does not continue from the older, overbroad wording.

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5350_functional_parity_matrix_amendment.json
```

## Main Amendments

### Witness Status

Old broad reading:

```text
Exact-witness vs fast-scalar mode split is a blocking gap for same functionality.
```

Refined status:

```text
hd_exec-compatible 3-D GPU entrypoint on reviewed Level-B artifacts:
  exact-witness covered.

fast-scalar / global-bound early-break route:
  exact scalar HDResult only; per-source witnesses may be approximate.
```

### Variant Status

Old behavior:

```text
Parser accepted eb/nn/itk/clover/rt, but runtime rejected non-rt variants.
```

Refined status after Goal5349:

```text
All author variant names are accepted for directed HDResult value output.
Non-rt variants do not reproduce author variant-specific algorithms or
performance denominators.
```

## Still Not Complete

Full functional parity remains false. Major blockers still include:

```text
exact paper input artifacts/provenance;
full Figure 5 workload matrix coverage;
author variant-specific algorithm and performance semantics;
author-equivalent pruning / EB / Prune behavior;
load-balance / heavy-cell offload behavior;
adaptive grid auto-sizing;
Figure 5-11 denominator-aligned performance and memory matrices.
```

## Validation

```text
py -m unittest tests.goal5350_xhd_functional_parity_matrix_amendment_test
Ran 4 tests OK
```

Recommended combined check:

```text
py -m unittest tests.goal5348_xhd_witness_parity_entrypoint_audit_test tests.goal5349_xhd_hd_exec_variant_value_surface_test tests.goal5350_xhd_functional_parity_matrix_amendment_test
```

## Next Step

Send Goal5350 for strict review with Goals5348-5349. If accepted, use
Goal5350's amended status as the current functional parity map until a larger
matrix rewrite is warranted.
