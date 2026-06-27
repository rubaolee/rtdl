# Goal2990 - v2.6 Neutral Partner Handoff Foundation

Date: 2026-06-01
Status: v2.6 N-0 foundation; local descriptor/lease proof only; not release authorization

## Purpose

Goal2990 begins the v2.6 `N-0` neutral-buffer-seam cleanup from Goal2989 and
Claude's v2.6 note. The narrow goal is to prove that user-selected CuPy and
Numba partner columns can enter an RTDL neutral handoff packet without becoming
Triton/torch-carrier traffic.

In short, this is the v2.6 neutral partner handoff foundation: CuPy/Numba
columns get neutral descriptors and leases without torch carrier/coercion.

This is the first cleanup needed before Numba can become a first-class
user-selectable partner.

## What Changed

Added `src/rtdsl/v2_6_neutral_partner_handoff.py` with:

- `plan_v2_6_neutral_partner_handoff(...)`
- `prepare_v2_6_neutral_partner_handoff(...)`
- `validate_v2_6_neutral_partner_handoff(...)`
- `V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION`

The packet accepts explicitly selected `partner="cupy"` or `partner="numba"`
and records, per named column:

- the neutral-buffer descriptor;
- source protocol (`cupy`, `cuda_array_interface`, etc.);
- runtime-observed direct device pointer status;
- copy/borrow transfer label;
- neutral-seam lease transition log;
- `torch_conversion_used = false`;
- `torch_carrier_used = false`.

It fails closed when:

- the selected partner is unsupported;
- a required CUDA/device-resident column is actually host-resident;
- a torch source column is used for the CuPy/Numba neutral path;
- a host-stage transfer appears on this path.

The new symbols are importable as `rtdsl` attributes for internal benchmark
work, but they are intentionally absent from `rtdsl.__all__` because this is
still an experimental v2.6 foundation surface.

## Why This Matters

Before this goal, v2.5 could describe neutral-buffer metadata and could wrap
the Triton torch carrier with a seam lease, but CuPy/Numba hit-stream gather was
still planning-only. That meant the project could not yet say that Numba was a
first-class partner lane.

Goal2990 does not execute a Numba app yet. It removes the next design ambiguity:

```text
CuPy/Numba partner path -> neutral descriptor + lease
not CuPy/Numba partner path -> hidden torch carrier
```

This preserves the user decision from Goal2989: users choose supported partners,
and RTDL provides support for those partner handoff contracts without hiding a
different partner underneath.

## Current Boundaries

This is not a release authorization and not true-zero-copy wording.

Goal2990 does not authorize:

- v2.6 release;
- v2.5 release;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- Numba speedup wording;
- automatic partner selection;
- automatic Triton selection;
- app-specific native engine logic.

It also does not yet prove:

- end-to-end Numba continuation execution;
- CuPy/Numba runtime parity on a pod;
- a benchmark app using Numba as a real continuation path;
- full partner-neutral multi-partner composition.

## Local Validation

`tests/goal2990_v2_6_neutral_partner_handoff_test.py` uses fake CuPy/Numba-style
CUDA array objects so the descriptor and lease path is testable on Windows
without requiring CUDA:

- fake CuPy DLPack/CUDA columns produce `source_protocol="cupy"`;
- fake Numba CUDA-array-interface columns produce
  `source_protocol="cuda_array_interface"`;
- fake torch CUDA columns are rejected for the CuPy/Numba neutral path;
- fake host columns are rejected when device residency is required;
- all accepted packets complete `handoff_begin -> continuation_complete`;
- all accepted packets keep release, zero-copy, and speedup claims false.

Planned focused gate:

```powershell
$env:PYTHONPATH="src;."
py -3 -m py_compile src\rtdsl\v2_6_neutral_partner_handoff.py tests\goal2990_v2_6_neutral_partner_handoff_test.py
py -3 -m unittest tests.goal2990_v2_6_neutral_partner_handoff_test tests.goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_test tests.goal2692_neutral_buffer_seam_lifetime_contract_test tests.goal2703_neutral_buffer_lease_state_machine_test
```

## Next Step

The next v2.6 step should be a pod-backed runtime demonstrator:

1. choose one benchmark-app continuation that can use the existing Numba
   segmented count/sum kernels;
2. feed the columns through the Goal2990 neutral handoff packet;
3. execute Numba as an explicit user-selected partner;
4. compare against the CPU/reference path for exact parity;
5. keep performance and release claims blocked until a later same-contract gate.
