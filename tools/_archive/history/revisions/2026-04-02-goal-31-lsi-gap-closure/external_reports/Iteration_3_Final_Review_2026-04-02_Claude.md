**Findings:**

1. `rtdl_embree_run_lsi(...)` is cleanly rerouted away from the BVH/`rtcIntersect1` path.
2. The dedicated `1e-7` LSI epsilon is appropriately separated from the broader `1e-6` helper epsilon.
3. The old BVH LSI callback code remains as benign dead code, but it no longer affects correctness.
4. Lowering metadata and baseline notes are consistent with the new `native_loop` contract.
5. The new exact-source tests are appropriate and robust.

Claude conclusion:

> Goal 31 is an acceptable closure. The BVH/`rtcIntersect1` gap is eliminated, CPU/Embree parity is restored on both the minimal reproducer and the frozen `k=5` exact-source slice, and the fix is consistent across the native layer, lowering plan, baseline contract, and test suite.

Approval sentence:

> Approved — the Goal 31 patch correctly replaces the broken BVH LSI candidate path with a double-precision analytic nested-loop that achieves full CPU/Embree parity on the exact-source dataset.
