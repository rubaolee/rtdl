# Goal 30 Precision ABI Fix

Goal 30 addresses only the first confirmed problem from Goal 29:
- float32 truncation in the active native RTDL-to-Embree geometry ABI

Scope:
- widen the active native geometry ABI from float to double where RTDL passes exact-source geometry into the Embree backend
- keep the current `lsi` broad-phase design unchanged in this round
- verify whether the precision-only change improves the Goal 29 reproducer and the larger exact-source `k=5` slice

Non-goals:
- no claim that this round fully fixes larger-slice `lsi` parity
- no redesign of the Embree `lsi` broad phase
- no change to the DSL surface

Closure conditions:
- Claude reviews plan and final result
- Gemini monitors the whole round
- the round closes with one of:
  - a precision fix that measurably improves the reproducer and is kept, or
  - an honest result that precision widening alone is insufficient
