# Goal3787 Post-HIPRT Closeout Regression Packet

Status: clean-pod validated on the NVIDIA CUDA/Orochi HIPRT route.

## Purpose

Goal3787 records a combined regression packet after the Goal3786 benchmark
adequacy refresh. It checks that the HIPRT parity implementation chain, the
benchmark adequacy matrix, and the AMD functional runbook/runner still agree at
the same source commit.

## Evidence

Tracked artifact:

`docs/reports/goal3787_post_hiprt_closeout_regression_a5000.json`

Pod evidence:

- SSH target used: `root@69.30.85.203 -p 22057`.
- Clean checkout workdir: `/root/rtdl_goal3783_clean_1780855862`.
- Source commit: `6660d635`.
- GPU/driver: `NVIDIA RTX A5000, 580.126.09`.
- HIPRT library:
  `/root/rtdl_goal3783_clean_1780855862/build/librtdl_hiprt.so`.
- Combined suite: 32 test modules.
- Result: `Ran 176 tests in 14.995s`, `OK`.
- Scoped source dirty: `false`.

## What It Covers

The packet combines:

- the Goal3753/3763-3783 HIPRT parity and implementation tests;
- the Goal3740/3747/3757/3759/3760/3761 benchmark adequacy tests;
- the Goal3784 AMD functional validation runbook test;
- the Goal3785 fail-closed AMD pod runner test;
- the Goal3786 current adequacy-after-HIPRT-closeout test;
- the Goal3787 packet test itself.

The artifact records:

- HIPRT parity validation: `accept`;
- HIPRT parity stage counts: 10 ready, 0 missing generic extension, 0
  compatibility-only;
- benchmark adequacy validation: `accept`;
- benchmark adequacy counts: 3 strong, 7 adequate, 0 near-parity, 0
  needs-major-followup;
- Numba reference gaps: none;
- all claim-boundary flags: false.

## Boundary

This is NVIDIA CUDA/Orochi HIPRT regression evidence: not AMD hardware evidence.
It does not authorize AMD performance claims, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
claims, release claims, zero-copy claims, or app-specific native-engine logic.

Actual AMD evidence still requires the Goal3784 artifact produced by the
Goal3785 runner on an AMD pod.

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3787_post_hiprt_closeout_regression_packet_test
```
