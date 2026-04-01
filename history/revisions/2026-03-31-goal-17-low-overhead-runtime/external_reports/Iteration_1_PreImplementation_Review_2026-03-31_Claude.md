---

**1. Decision: `Consensus to begin implementation.`**

---

**2. Reasoning**

The scope is correctly scoped and evidence-grounded:

- The diagnosis is correct. Goal 15 confirmed the native path uses the same Embree C API already exposed by RTDL — the gap is entirely host-path overhead (object creation, repeated validation, ctypes marshaling, result rematerialization), not a different algorithm. Goal 17 targets exactly that.
- The slice boundary is tight. Targeting `lsi` and `pip` only, two workloads with measured baselines (7.6x and 37.4x), is the minimum surface needed to prove the architecture shift works before expanding. Narrowing further would not produce useful evidence.
- The DSL contract is preserved. The authoring surface stays Python. Only the execution data path changes. This is the right split and aligns with the "Python as control plane, not data plane" design rule now documented in `runtime_overhead_architecture.md`.
- The deliverables are concrete. Packed buffers + prepared execution path + three-way benchmark is a complete, falsifiable result. No speculative scope.
- The non-goals are honest. No claim of full parity in one round, no OptiX, no complete data-plane removal. That honesty makes the acceptance bar achievable.

One thing to watch: Goal 15's native timing includes wrapper overhead (it calls the same Embree C API), so the "native gap" baseline is a lower bound of achievability, not a ceiling. The final report must state this explicitly to avoid overclaiming.

---

**3. Acceptance criteria for final review**

| # | Criterion |
|---|-----------|
| 1 | Python DSL authoring surface is unchanged — existing kernel definitions run without modification. |
| 2 | New prepared path compiles once and binds inputs once; no repeated normalization or ctypes marshaling on subsequent calls. |
| 3 | Packed input containers exist for segments, points, and polygons and pass negative-input tests. |
| 4 | Correctness parity: `lsi` and `pip` output matches the current RTDL Embree path on all tested fixtures. |
| 5 | Benchmark reports all three paths — current RTDL Embree / new prepared RTDL Embree / Goal 15 native — on the same fixtures and hardware. |
| 6 | The prepared path shows a statistically meaningful speedup over current RTDL Embree for both `lsi` and `pip` (any improvement that closes a visible fraction of the 7.6x / 37.4x gap is acceptable; exact parity with native is not required). |
| 7 | The report explicitly states the remaining native gap and acknowledges that Goal 15 native timing includes wrapper overhead — no overclaiming. |
| 8 | Regression test coverage for the new packed-input path exists and passes in CI. |
