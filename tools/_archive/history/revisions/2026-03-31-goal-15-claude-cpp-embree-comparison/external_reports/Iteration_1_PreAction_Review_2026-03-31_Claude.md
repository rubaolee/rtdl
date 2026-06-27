1. **lsi and pip are the two simplest, best-defined query families** in your RTDL design doc (`rayjoin_target.md:30`), making them the right scope for a first correctness+performance validation without entangling more complex output policies.

2. **Embree is the right baseline choice here** — it is CPU-portable and needs no OptiX/CUDA, so the comparison is reproducible and isolates the DSL abstraction cost from hardware availability.

3. **The RTDL lowering pipeline already has skeleton structure** for exactly this path (input normalization → acceleration planning → ray formulation), so a comparison run will also stress-test whether the generated skeleton is a faithful translation of the high-level kernel, not just a benchmark.

Consensus to begin implementation
