# Goal3792 Post-Runner-Discovery Regression Packet

Status: clean-pod validated on the NVIDIA CUDA/Orochi HIPRT route.

## Purpose

Goal3792 refreshes the combined post-HIPRT regression packet after Goal3788
and Goal3790. The prior Goal3787 packet was still valid, but it predated the
Hausdorff alias/metadata audit and the AMD runner HIPRT-prefix autodiscovery
hardening.

## Evidence

Tracked artifact:

`docs/reports/goal3792_post_runner_discovery_regression_a5000.json`

Pod evidence:

- SSH target used: `root@69.30.85.203 -p 22057`.
- Clean checkout workdir: `/root/rtdl_goal3788_clean_1780857956`.
- Source commit: `a7a10228`.
- GPU/driver: `NVIDIA RTX A5000, 580.126.09`.
- HIPRT library:
  `/root/rtdl_goal3788_clean_1780857956/build/librtdl_hiprt.so`.
- Combined suite: 34 test modules.
- Result: `Ran 185 tests in 14.612s`, `OK`.
- Scoped source dirty: `false`.

## What It Covers

The packet combines:

- the Goal3753/3763-3783 HIPRT parity and implementation tests;
- the Goal3740/3747/3757/3759/3760/3761 benchmark adequacy tests;
- the Goal3784 AMD functional validation runbook test;
- the Goal3785 fail-closed AMD pod runner test;
- the Goal3786 current adequacy-after-HIPRT-closeout test;
- the Goal3787 prior packet test;
- the Goal3788 Hausdorff generic alias and metadata audit test;
- the Goal3790 HIPRT-prefix discovery test.

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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3792_post_runner_discovery_regression_packet_test
```
