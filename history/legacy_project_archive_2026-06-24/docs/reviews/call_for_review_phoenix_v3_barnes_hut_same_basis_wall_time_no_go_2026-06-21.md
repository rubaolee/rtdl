# Call For Review: Phoenix V3 Barnes-Hut Same-Basis Wall-Time No-Go

Reviewer: Claude or Gemini external AI.

Please critically review the new Phoenix V3 packet:

- `docs/rebuild/v3/phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.md`
- Script: `scripts/v3_phoenix_barnes_hut_same_basis_wall_time_no_go.py`
- Test: `tests/v3_phoenix_barnes_hut_same_basis_wall_time_no_go_test.py`

Context:

- Phoenix V3 must promote only reusable, evidence-backed language/engine capabilities.
- Existing M6 Barnes-Hut evidence was blocked partly because route ratios mixed CUDA-event kernel timing for fused Numba CUDA with wall-hot timing for CPU and prepared OptiX routes.
- The new packet re-reads the saved serious-run M6 artifact with one timing basis: `repeat_seconds_median` wall time for every route.
- Under this same basis, fused Numba CUDA remains fastest at 32,768, 65,536, and 131,072 bodies; prepared RTDL/OptiX+Numba remains slower by 7.022x, 4.990x, and 13.591x respectively.
- The packet therefore keeps current prepared RTDL/OptiX frontier-emission rows out of M7, forbids public RT-core/Barnes-Hut/broad V3-over-V2 claims, and identifies the reusable fused aggregate-tree/vector partner route as the only plausible next V3 candidate.

Questions for review:

1. Is the same-basis interpretation correct, or is there a hidden timing/accounting flaw?
2. Is the no-go decision for current prepared RTDL/OptiX frontier-emission sufficiently supported?
3. Is it honest to preserve the fused Numba CUDA partner route as a future separate V3 M7 candidate, while not promoting it in this packet?
4. Are any public/user-facing claims still too strong?
5. What concrete fixes are required before this packet can be treated as reviewed Phoenix V3 evidence?

Required verdict format:

- `approve`
- `approve-with-amendments`
- `block`

Please prioritize correctness and user-responsible claim boundaries over politeness.
