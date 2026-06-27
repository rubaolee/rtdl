# Goal 30 Spec (Codex)

Date: 2026-04-02
Round: Goal 30 Precision ABI Fix

Intent:
- continue from Goal 29 without overclaiming
- fix only the confirmed float32 truncation problem in the native geometry ABI
- leave the larger Embree `lsi` broad-phase redesign for a later round

Planned code areas:
- `src/rtdsl/embree_runtime.py`
- `src/native/rtdl_embree.cpp`
- native comparison apps that share the ABI

Success for this round:
- the precision ABI is widened cleanly and verified
- the Goal 29 minimal reproducer and the frozen `k=5` slice are rerun
- final reporting states clearly whether precision alone was enough
