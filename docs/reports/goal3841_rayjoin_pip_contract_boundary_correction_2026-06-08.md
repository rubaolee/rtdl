# Goal3841 RayJoin PIP Contract Boundary Correction

Date: 2026-06-08

Status: internal metadata correction; no new runtime artifact.

## Purpose

Goal3840 updated the current benchmark adequacy metadata after RayJoin LSI and
overlay gained no-RawKernel Numba scalar-count references. The update was
directionally correct, but the spatial RayJoin row could be overread because it
mentioned the strong Goal3761 native-PIP cross-size packet beside the bounded
public-CDB PIP evidence from Goals3833/3834.

Goal3841 makes the distinction explicit:

- Goal3761 is strong native-PIP cross-size evidence against a dense all-CuPy
  candidate contract.
- Goals3833/3834 remain the bounded 512 public-CDB PIP scalar-count evidence,
  and that row is still CuPy-favorable.
- Goal3834 still matters because it gives a no-RawKernel Numba reference for
  users who need Python-source custom CUDA logic.
- Goal3838 still makes LSI and overlay scalar-count coverage strong: Numba is
  slightly faster than dense CuPy, while RTDL/OptiX is about `260x` faster than
  Numba/CuPy on those bounded public-CDB scalar contracts.

## Metadata Change

The current adequacy version is now:

`rtdl.v2_10.benchmark_adequacy_after_goal3841.v1`

The spatial RayJoin performance wording now blocks three possible misreadings:

- the Goal3761 native-PIP packet is not the bounded 512 public-CDB PIP row;
- bounded public-CDB PIP is not currently an RTDL/OptiX performance win;
- none of the current packets authorize a universal PIP-dominance,
  RTDL-beats-RayJoin, or RayJoin paper-reproduction claim.

## Claim Boundary

This correction does not authorize:

- release action;
- public speedup wording;
- whole-app RayJoin wording;
- RayJoin paper reproduction claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner selection.

It only keeps the internal advisory API honest about which RayJoin subcontracts
are currently fast and which ones merely have Numba reference coverage.
