# Goal 30 Precision ABI Fix (2026-04-02)

## Scope

Goal 30 addressed only the first confirmed problem from Goal 29:
- float32 truncation in the active native RTDL-to-Embree geometry ABI

This round did **not** attempt to redesign the current Embree `lsi` broad phase.

## Code Changes

The active native geometry ABI was widened from float to double in the live RTDL Embree path:
- Python `ctypes` structs in `src/rtdsl/embree_runtime.py`
- matching native structs and polygon vertex-pointer types in `src/native/rtdl_embree.cpp`
- native comparison apps that share the ABI:
  - `apps/goal15_lsi_native.cpp`
  - `apps/goal15_pip_native.cpp`

The widened fields now include:
- segment coordinates
- point coordinates
- triangle coordinates
- ray coordinates and `tmax`
- polygon vertex arrays
- `lsi` intersection coordinates
- nearest-segment distance output

No DSL-surface change was made.

## Verification

Targeted ABI verification passed:
- `python3 -m unittest tests.goal30_precision_abi_test`

Relevant regression slice passed:
- `python3 -m unittest tests.goal30_precision_abi_test tests.goal19_compare_test tests.goal28c_conversion_test`

## Measured Result

### Minimal exact-source reproducer

The Goal 29 four-pair exact-source reproducer was rerun after the ABI widening.

Observed result:
- CPU pairs:
  - `(24, 368)`
  - `(25, 367)`
  - `(26, 365)`
  - `(111, 345)`
- Embree pairs:
  - none

So the precision-only change did **not** make the minimal exact-source `lsi` reproducer parity-clean.

### Frozen `k=5` exact-source slice

The frozen Goal 29 `k=5` exact-source slice was rerun after the ABI widening.

Observed result:
- CPU count: `7`
- Embree count: `3`
- CPU-only pairs remained:
  - `(24, 368)`
  - `(25, 367)`
  - `(26, 365)`
  - `(111, 345)`
- Embree-only pairs remained:
  - none

So the precision-only change also did **not** reduce the known pair mismatch on the frozen larger slice.

## Honest Conclusion

Goal 30 still matters because it removes a confirmed quality problem:
- the active native geometry ABI no longer truncates exact-source coordinates to float before entering the native Embree path

But Goal 30 does **not** solve the larger exact-source `lsi` mismatch.

The measured outcome is:
- precision ABI fix: completed
- exact-source `lsi` parity improvement: not observed on the known reproducers

Therefore the unresolved blocker from Goal 29 remains:
- the current Embree-side `lsi` candidate-generation / broad-phase path still needs direct instrumentation or redesign

## Next Required Goal

The next correct round is:

**instrument or redesign the Embree `lsi` broad phase so the exact-source missing pairs can be explained before or inside native candidate traversal**

That round should start from the now-cleaner baseline:
- no float32 truncation in the active RTDL native geometry ABI
- same frozen exact-source reproducers still available
