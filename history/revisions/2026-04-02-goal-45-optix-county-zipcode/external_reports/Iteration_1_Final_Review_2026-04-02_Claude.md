Verdict: APPROVE

Findings:
1. Script correctness is sound. Parity check is a strict 3-way comparison: CPU rows == JIT rows == warm rows. Sort keys are correct for set-equivalence (`lsi_rows` by `(left_id, right_id)`, `pip_rows` by `(point_id, polygon_id, contains)`). Speedup formula (cpu_median / optix_warm_median) is correct.
2. Report is honest about failures. All 4 rejected points are named with explicit reasons. The `2677`-family failure cluster and the `2300`-family `lsi` divergence at `1x12` are both disclosed and not minimized.
3. Report correctly frames sub-1x GPU performance. The `0.52x` to `0.87x` speedup values are reported plainly and correctly attributed to small slice size on the `nvcc` PTX fallback path.
4. Boundary statements are explicit and accurate. The report does not claim full-ladder parity, whole-dataset closure, or that OptiX is faster than the C oracle. The "What Goal 45 Closed" / "Boundary" split is clean.

Risks:
1. `1x8` `lsi` is a zero-row parity case (`0 == 0`). It remains a valid exact-row parity point, but it is a weaker signal than `1x10`, which has non-zero `lsi` rows on both backends.
2. All accepted performance points are sub-1x. The accepted set is the parity-clean subset, not a performance-representative subset.
3. Results are specific to the `nvcc` PTX fallback path. The default NVRTC path is not tested here.
