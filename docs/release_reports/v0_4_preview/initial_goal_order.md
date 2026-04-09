# RTDL v0.4 Preview: Initial Goal Order

## Goal order

1. Define the public `point_in_volume` workload contract.
2. Add the Python/DSL surface for that workload.
3. Add the Python reference implementation and deterministic fixtures.
4. Add native CPU/oracle support and closure tests.
5. Close Embree for the new workload.
6. Close OptiX and Vulkan under explicit bounded contracts.
7. Add the public example chain and tutorial extension.
8. Add bounded benchmark/release evidence.
9. Run the final `v0.4` doc and release audit.

## Why this order

This order forces correctness and public semantics to come before backend
breadth and demo presentation.

That is the main lesson from the `v0.3.0` line.
