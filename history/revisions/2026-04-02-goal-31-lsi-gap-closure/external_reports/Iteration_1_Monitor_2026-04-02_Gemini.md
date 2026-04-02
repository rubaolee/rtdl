### Gemini monitoring note

Decision criteria:
- full parity on the minimal reproducer and frozen `k=5` slice
- no heuristic closure based only on one patched epsilon
- clear documentation of whether the accepted local runtime remains BVH-backed or becomes `native_loop`

Acceptable closure:
- new regression coverage for the exact-source mismatch
- matching CPU and Embree row sets on the known reproducers
- a short report explaining why the accepted implementation path was chosen

Invalid closure:
- any remaining pair mismatch
- undocumented backend-contract change
- cross-host ambiguity about whether the bug was actually fixed
