# Codex Consensus: Goal 146 Jaccard Linux Multi-Backend Stress

Goal 146 is accepted.

The technical result is real:

- `run_embree`, `run_optix`, and `run_vulkan` now accept the two narrow
  Jaccard workloads through documented native CPU/oracle fallback
- raw mode is explicitly rejected on those fallback paths
- focused local and Linux tests are clean on their accepted platforms
- the Linux stress rows at `copies=64` and `copies=128` are in the requested
  multi-second range
- all accepted backend rows are exactly consistent with the Python truth row

The key honesty boundary remains:

- this is **not** native Embree/OptiX/Vulkan Jaccard maturity
- this is **not** RT-core acceleration
- these timing rows are wrapper execution times under documented fallback

The goal is therefore closed as:

- wrapper-level backend-surface usability
- Linux large-scale consistency
- narrow Jaccard workload stress evidence

and not as native backend closure.
