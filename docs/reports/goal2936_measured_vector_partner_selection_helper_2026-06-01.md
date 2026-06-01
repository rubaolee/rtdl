# Goal2936: Measured Vector Partner Selection Helper

Date: 2026-06-01
Status: local focused gate passed

## Purpose

Goal2936 turns the Goal2933 Barnes-Hut lesson into a reusable v2.5 helper:
users should be able to explicitly measure same-contract partner candidates and
select the fastest one for a generic continuation without hiding dispatch in
the RTDL engine.

New public helper:

`rt.measured_grouped_vector_sum_2d_partner_selection(...)`

The helper accepts caller-supplied partner columns for `torch`, `triton`,
`cupy`, or any subset of those partners, runs the existing generic
`grouped_vector_sum_2d_partner_columns` adapter for each candidate, validates
same-contract output by default, and returns the selected columns plus
selection metadata.

## Design Rule

This is not a smart dispatcher. It is caller-requested measurement:

- the user/app chooses the candidate partner set;
- the helper records candidate order, timings, skips, errors, and the selected
  partner;
- the native RT engine is not called;
- no app meaning is embedded;
- no speedup, zero-copy, release, or automatic-partner claim is authorized.

That keeps the v2.5 principle intact: Python users can choose any supported
partner, but RTDL does not silently route work in a way that makes performance
or reproducibility hard to explain.

## Files

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `tests/goal2936_measured_vector_partner_selection_helper_test.py`

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2936_measured_vector_partner_selection_helper_test tests.goal2934_current_packet_after_cupy_vector_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 14 tests
OK
```

## Boundary

Goal2936 is an internal v2.5 ergonomics/runtime hardening step. It does not
authorize v2.5 release, public speedup wording, broad RT-core wording,
whole-app speedup wording, true-zero-copy wording, automatic Triton/CuPy
selection wording, package-install wording, paper-reproduction wording, or
app-specific native engine logic.
