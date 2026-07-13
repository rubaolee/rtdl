# Goal4859 Completion: RayJoin Section 5.7 County x Zipcode Byte-Equal Reproduction

Date: 2026-07-02

## Verdict Requested

`completed_county_zipcode_section57_byte_equal__production_streaming_writer_passed__no_broad_performance_claim`

## Scope

This goal reproduced the RayJoin Section 5.7 County x Zipcode polygon-overlay output against the AuthorPatch baseline using the RTDL product route.

This is not a full eight-pair Section 5.7 claim, not a broad RayJoin performance claim, and not a Numba-partner performance claim. Correctness was the gate.

## Evidence

AuthorPatch baseline:

`/workspace/goal4861_author_intended_baseline/author_intended_county_zipcode_overlay.txt`

RTDL output:

`/workspace/goal4859_rtdl_county_zipcode_overlay.txt`

Both files:

- Size: 2.3G
- Lines: 87,758,114
- SHA256: `02fcae3f53a8486134412564c438a19d7d999d1948742e7f115a5d13f94836ef`
- `cmp`: `BYTE_EQUAL`

Debug streaming comparer also passed before production writer validation:

- Artifact directory: `/workspace/rtdl_goal4859_exec/history/internal_docs/goal4865_streaming_mismatch_trace_after_internal_display_no_endpoint_snap`
- `stream_match: true`
- `first_diff: null`
- Streamed chains: 29,253,961
- Streamed lines: 87,758,114
- Streamed face count: 115,515

Production run summary:

- `output.streaming: true`
- `output.chain_count: 29253961`
- `output.face_count: 115515`
- `output.line_count: 87758114`
- `output.point_count: 58504153`
- `phase_seconds.total_sec: 449.25938529521227`
- `phase_seconds.output_chain_stream_write_sec: 266.9479373469949`
- `lsi.intersection_count: 965844`

## Issues Exposed And Fixed

1. LSI direction contract was wrong for overlay.

   Author source runs map0 edges as query against map1 as the prepared/traversed map. RTDL had the direction reversed for this reproduction path. Fixing the direction removed early shared-vertex/degenerate-chain mismatches.

2. Intersection coordinate construction did not match the author edge-equation route.

   RTDL was using a different parametric reconstruction path. The repaired route follows the author edge-equation form for scaled intersections and keeps rational identity separate from display output.

3. Fast array scaling was unsafe for byte-level reproduction.

   The vectorized long-double scaling path created last-digit mismatches. It is now opt-in; the default reproduction path uses the scalar author-compatible scaling route.

4. Geometry identity and display coordinates had been conflated.

   The output-chain point identity must be based on the raw/rational geometry point, while emitted text must follow the author display contract. RTDL now carries `display_points` separately from identity `points`.

5. Display output must follow the author internal-integer display path.

   The decisive rule is: rational/raw coordinates are preserved for identity, while xsect display is produced from the author-style scaled integer point converted back to world coordinates, with a very narrow positive exact-half compatibility adjustment. Earlier endpoint-display snapping and broad half-boundary heuristics were too wide and were removed or narrowed.

6. Production output-chain writing was not scalable.

   The old production writer materialized 29,253,961 output chains before writing. On the POD it was killed before producing the file. The product route now streams output chains directly to disk when `output_path` is provided, preserving the same face-id and point-id assignment order while avoiding the memory blow-up.

## Important Non-Claims

- This does not claim all eight Section 5.7 pairs are reproduced.
- This does not claim a RayJoin-wide or RTDL-wide speedup.
- This does not claim Numba is central to this specific output path.
- This does not claim the old V3/V4 experimental work is part of the public product surface.
- This does not make any Embree claim.

## Next Work

1. Send this report for external review.
2. Add focused regression coverage for the exposed display/identity contracts so future changes do not require a 2.3G output comparison to catch the same bugs.
3. Decide whether to expand Section 5.7 beyond County x Zipcode only after exact additional inputs and AuthorPatch baselines are available.
