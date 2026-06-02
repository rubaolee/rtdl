# Goal2991 - v2.6 Numba Neutral-Handoff Pod Runner

Date: 2026-06-01
Status: runner prepared; CUDA pod execution still required

## Purpose

Goal2991 prepares the pod runner for the next v2.6 step after the Goal2990
neutral handoff packet. It is a bridge from local descriptor/lease proof to a
real Numba continuation smoke:

```text
Numba CUDA device arrays
  -> Goal2990 neutral handoff packet
  -> Numba segmented count/sum kernels
  -> CPU parity check
```

This is still not a release authorization and not a Numba speedup claim.

## Runner

Added:

- `scripts/goal2991_v2_6_numba_neutral_handoff_pod_runner.py`

The runner:

- imports Numba/CUDA and fails closed when unavailable;
- builds a deterministic grouped-reduction fixture;
- copies `group_ids` and `values` to Numba CUDA device arrays;
- feeds those arrays through `prepare_v2_6_neutral_partner_handoff(..., partner="numba")`;
- validates the Goal2990 neutral handoff packet;
- runs `run_numba_segmented_count_i64(...)`;
- runs `run_numba_segmented_sum_f64(...)`;
- compares both outputs to CPU NumPy references;
- writes a JSON artifact with source commit, dirty status, phase timing,
  handoff metadata, parity flags, and claim-boundary flags.

The runner deliberately contains no torch import and no torch carrier path.

## Progress Logging

The runner prints bounded progress messages:

```text
[goal2991] importing Numba/CUDA stack
[goal2991] building fixture rows=...
[goal2991] copying fixture to device
[goal2991] preparing v2.6 neutral handoff packet
[goal2991] running Numba segmented count
[goal2991] running Numba segmented sum
[goal2991] validating CPU parity
[goal2991] wrote ...
[goal2991] status=...
```

## Local Validation

`tests/goal2991_v2_6_numba_neutral_handoff_pod_runner_test.py` verifies:

- the runner calls the Goal2990 neutral handoff packet before Numba execution;
- count and sum both route through Numba continuation helpers;
- CPU parity fields are recorded;
- torch is absent from the runner source;
- release, speedup, and true-zero-copy claims remain false;
- an optional tiny runtime smoke executes only when Numba CUDA is available.

## Pod Command

On a CUDA pod:

```bash
cd /path/to/rtdl_v0_4_release_prep_review
PYTHONPATH=src:. python scripts/goal2991_v2_6_numba_neutral_handoff_pod_runner.py \
  --rows 1000000 \
  --groups 4096
```

Expected artifact:

```text
docs/reports/goal2991_v2_6_numba_neutral_handoff_pod/goal2991_numba_neutral_handoff.json
```

## Boundary

Goal2991 does not authorize:

- v2.6 release;
- v2.5 release;
- public speedup wording;
- Numba speedup wording;
- broad RT-core wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native engine logic.

## Next Step

Run this on a CUDA pod. If it passes, the next goal should wire one real
benchmark-app continuation through `partner="numba"` as a user-selected path,
still with CPU/reference parity and no performance claim.
