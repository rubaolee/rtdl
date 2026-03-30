# Iteration 6 Pre-Implementation Report

## Scope

Step 1 and Step 2 are complete. The next implementation slice covers the remaining practical baseline work needed before the Embree baseline can be considered complete enough to package:

- Step 3: make the shared runtime ABI visible and reusable in runner code,
- Step 4: strengthen CPU vs Embree correctness coverage using the frozen contract helpers,
- Step 5: formalize representative dataset references for executable baseline runs,
- Step 6: add a reproducible local benchmark harness,
- Step 7: add reproducible workload runners,
- Step 8: update docs so contributors can actually use the new runners and harness,
- Step 9: validate authored programs on Embree, not just compile/lower them.

## Proposed Deliverables

1. A generic baseline runner module that:
   - exposes one entry point per baseline workload,
   - runs both `run_cpu(...)` and `run_embree(...)`,
   - compares outputs through the baseline comparison helper.

2. A benchmark script that:
   - runs the baseline workloads repeatedly,
   - records backend/workload/dataset/iteration/timing metadata,
   - writes raw results to a JSON artifact under `build/`.

3. Stronger tests that:
   - verify CPU vs Embree parity using `compare_baseline_rows(...)`,
   - verify authored Codex/Gemini examples can execute on Embree for the workloads they represent.

4. Documentation updates that:
   - explain the new baseline runners,
   - explain the benchmark harness,
   - explain what “representative dataset” means in the current baseline.

## Review Questions For Gemini

1. Is this the right remaining implementation slice for the Embree baseline?
2. What specific acceptance checks should be used for this slice?
3. Are any pieces missing or misordered?
4. If acceptable, what conditions would constitute consensus to begin implementing this slice?
