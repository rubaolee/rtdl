# Goal598: v0.9.2 Apple RT Masked Segment-Intersection Closure

Date: 2026-04-19

Status: ACCEPTED with Codex + Gemini + Claude implementation consensus

## Goal

Reduce Apple Metal/MPS RT overhead for bounded 2D `segment_intersection` while preserving exact RTDL row identity and CPU-reference parity.

## Design Evidence

Goal598 started from the accepted break-even report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_v0_9_2_apple_rt_segment_intersection_break_even_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_break_even_external_review_2026-04-19.md`

The accepted design rejected multi-primitive `Any` traversal because MPS does not provide reliable primitive identity for `Any`. RTDL needs the `right_id` for every emitted row, so the implemented path uses nearest-hit traversal with primitive index and primitive masks.

## Implementation

Changed file:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`

Implementation summary:

- Right segments are partitioned into chunks of at most 32 valid segments.
- Each right segment in a chunk is extruded into a quadrilateral primitive.
- Each primitive receives one mask bit.
- Each left segment becomes one MPS ray with the full chunk mask.
- MPS nearest-hit traversal returns candidate primitive identity.
- Exact RTDL correctness is preserved by analytic `segment_intersection_point` refinement after traversal.
- The primitive bit is cleared after each candidate, including analytic false positives, so traversal can continue without repeating the same candidate.
- Per-left rows are sorted by original right-segment index before flattening, preserving left-major/right-input-order output.

This reduces acceleration-structure builds from one per right segment to one per <=32 right segments. It does not eliminate dense-output enumeration cost.

## Correctness Tests

Added test file:

- `/Users/rl2025/rtdl_python_only/tests/goal598_apple_rt_masked_segment_intersection_test.py`

Focused command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal598_apple_rt_masked_segment_intersection_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal597_apple_rt_masked_hitcount_test tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 16 tests in 0.042s
OK
```

Coverage includes:

- zero-hit and one-hit cases
- multiple intersections in a single chunk
- more than 32 right segments, forcing multiple chunks
- duplicate right segments crossing at the same point/distance
- left-major/right-input-order output
- parity against the CPU Python reference and the broader Apple RT dispatch surface

Additional validation:

```bash
make build-apple-rt
git diff --check
```

Both passed.

## Performance Evidence

Post-change performance artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_post_masked_segment_intersection_perf_macos_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_post_masked_segment_intersection_perf_macos_2026-04-19.json`

Fresh local Apple M4 harness result, 5 warmups and 20 measured repeats:

| Workload | Embree median | Apple RT median | Apple/Embree | Parity | Stability |
| --- | ---: | ---: | ---: | --- | --- |
| `segment_intersection_2d` | 0.007503292 s | 0.031314438 s | 4.173x | True | True |

Comparison to the latest pre-Goal598 dense segment artifact:

| Artifact | Apple RT segment median | Apple/Embree | Stability |
| --- | ---: | ---: | --- |
| Goal597 post-hitcount artifact | 0.092515083 s | 11.867x | True |
| Goal598 post-segment artifact | 0.031314438 s | 4.173x | True |

Measured local improvement for the dense 128x128 segment fixture:

```text
0.092515083 / 0.031314438 = 2.954x lower Apple RT median time
```

## Honesty Boundary

This is a real Apple Metal/MPS RT optimization and a real improvement on the local dense fixture. It is still not a public claim that Apple RT is generally faster than Embree:

- Apple RT segment intersection remains about 4.17x slower than Embree on this dense fixture.
- Dense all-pair output still requires enumeration; the optimization primarily removes per-right-segment AS-build overhead.
- Closest-hit timing in the same harness is unstable and must remain engineering-triage evidence only.
- Public docs may say v0.9.2 reduces Apple RT segment-intersection overhead, but must not call the Apple backend mature or globally optimized.

## External Review

Gemini external implementation review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_implementation_external_review_2026-04-19.md`
- Verdict: ACCEPT

Claude external implementation review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal598_claude_implementation_review_2026-04-19.md`
- Verdict: ACCEPT
- Note: Claude identified a minor pre-existing error-path release-style inconsistency in Apple RT native code; it is not a Goal598 blocker and is not a correctness/performance regression.

## Codex Verdict

ACCEPT. Goal598 achieved correctness-preserving Apple RT segment-intersection optimization with stable local parity and a measured segment-intersection median reduction versus the latest pre-Goal598 artifact.
