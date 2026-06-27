The revised plan addresses all five blockers from Iteration 2:

1. **Output-format contradiction** — Fixed. The revised plan explicitly states no header line, with data-only rows shown in examples. The `left_id,right_id` line is clarified as **not** a header.

2. **LSI intersection wording imprecision** — Fixed. "Fat rays" and Cohen-Sutherland/Shamos-Hoey are gone. The predicate is now precisely tied to RTDL's `reference._segment_intersection(...)` semantics: non-parallel under epsilon, `0 <= t <= 1` and `0 <= u <= 1`.

3. **PIP triangle fan changes semantic object** — Fixed. Triangle fans are dropped. The plan now uses Embree only for broad-phase candidate filtering, with the same point-in-polygon refinement semantics as RTDL for final membership, preserving `boundary_mode="inclusive"`.

4. **Exact rational arithmetic too strong** — Fixed. Three-tier oracle strategy: tiny exact fixtures, medium RTDL `run_cpu(...)` parity, larger RTDL `run_embree(...)` parity.

5. **Timing boundary ambiguity** — Fixed. Two explicit timing views: native kernel/build timing (excludes data generation and output), and RTDL end-to-end host-path timing (includes normalization/materialization, excludes synthetic data generation if pre-generated once for both sides).

No new blockers introduced. The sequencing (`lsi` first, `pip` only after `lsi` passes) is a sound risk gate.

Consensus to begin implementation.
