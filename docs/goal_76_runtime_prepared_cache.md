## Goal 76: Runtime Prepared-Execution Cache

### Objective

Move a repeatable performance win into the RTDL runtime instead of pushing the burden onto programmers.

This goal adds automatic prepared-execution reuse for repeated identical raw-input calls on the RTDL backend runtimes:

- Embree
- OptiX
- Vulkan

The change is intentionally semantics-preserving. It does not alter RTDL kernels, emitted rows, or workload contracts. It only avoids repeated prepare-and-bind work when the same compiled kernel is invoked again with the same raw logical inputs.

### Accepted Scope

- automatic in-process prepared-execution reuse
- repeated identical raw-input calls only
- cache bypass for already packed inputs
- bounded in-process LRU cache
- focused unit-test validation

### Non-Goals

- no change to workload semantics
- no end-to-end benchmark claim
- no new programmer-visible optimization knobs
- no change to PostGIS or oracle truth contracts

### Why This Goal Exists

Goals 70-72 showed that prepared-execution boundaries can materially improve backend performance, but those wins should not require every programmer or demo path to hand-manage prepared objects. RTDL should absorb the obvious repeated-call optimization inside the runtime whenever it can do so safely.

### Result

RTDL now reuses prepared executions automatically for repeated identical raw-input calls on Embree, OptiX, and Vulkan. The cache is keyed by compiled-kernel signature plus normalized logical inputs, and it is explicitly bypassed for already packed inputs.
