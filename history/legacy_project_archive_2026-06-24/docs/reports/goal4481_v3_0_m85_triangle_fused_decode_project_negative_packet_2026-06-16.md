# Goal4481 / V3.0 M85: Fused Decode/Project Negative

## Verdict

Do not promote `--segment-ray-output-builder numba_fused_decode_project`.

The candidate is correct, but slower. It replaces CuPy vectorized decode/weight/projection with one no-C++ Numba CUDA output-fill kernel. That slightly improves prepared batch build, but segment-ray construction gets much slower, so total wall time loses on all three large rows.

## Matrix

Warmup=1/repeat=3. Current means Goal4479 full columns with `cupy_vectorized` output. Candidate means the same route with `numba_fused_decode_project`.

| Dataset | Current total | Fused total | Fused speedup | Current segment build | Fused segment build | Segment speedup | Same count/rays/weights |
|---|---:|---:|---:|---:|---:|---:|---|
| com-lj | 6.489s | 7.216s | 0.899x | 1.149s | 1.740s | 0.661x | yes |
| soc-LiveJournal1 | 13.273s | 14.047s | 0.945x | 1.496s | 2.135s | 0.701x | yes |
| com-orkut | 35.990s | 37.780s | 0.953x | 7.281s | 10.962s | 0.664x | yes |

## Interpretation

This is useful evidence, even though it is not a win. A simple Numba fused output kernel is not automatically better than CuPy's vectorized decode/projection chain. It avoids some vectorized materialization, but the Numba output-fill path is slower enough that the current route should stay on `cupy_vectorized`.

Next useful work is not this fused output builder. The remaining target is still the unique/count boundary itself: either further reduce sort/RLE cost or move to a grouped/local unique-count strategy that avoids global sorting pressure.

## Artifacts

- `goal4481_v3_0_m85_triangle_fused_decode_project_com_lj_w1r3_2026-06-16.json`
- `goal4481_v3_0_m85_triangle_fused_decode_project_soc_livejournal1_w1r3_2026-06-16.json`
- `goal4481_v3_0_m85_triangle_fused_decode_project_com_orkut_w1r3_2026-06-16.json`
