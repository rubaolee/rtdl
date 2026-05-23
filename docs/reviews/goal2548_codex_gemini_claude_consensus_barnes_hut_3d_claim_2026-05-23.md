# Goal2548 Codex-Gemini-Claude Consensus: Barnes-Hut 3-D Claim

Date: 2026-05-23

## Reviewed Files

- `docs/reports/goal2548_barnes_hut_3d_claim_packet_2026-05-23.md`
- `docs/reports/goal2545_2547_barnes_hut_resident_float32_3d_optimization_2026-05-23.md`
- `docs/reports/goal2543_barnes_hut_authors_code_optix_timing_2026-05-23.md`
- `docs/reports/goal2543_barnes_hut_authors_code_raw_timing_2026-05-23.txt`
- Goal2544-2547 JSON artifacts referenced by the claim packet

## External Reviews

- Gemini review: `docs/reviews/goal2548_gemini_review_barnes_hut_3d_claim_2026-05-23.md`
- Claude review: `docs/reviews/goal2548_claude_review_barnes_hut_3d_claim_2026-05-23.md`

## Consensus Verdict

Codex, Gemini, and Claude agree that the Barnes-Hut 3-D claim is acceptable
only as a bounded diagnostic kernel-phase statement after the wording changes
applied to the claim packet.

The acceptable statement is:

> On an RTX A5000 pod, RTDL's Goal2547 3-D scalar CUDA diagnostic kernel
> reached a `0.509 ms` resident-kernel minimum at 32,768 bodies on an
> authors-generated input file, under the
> `generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1` contract
> (correctness validated against RTDL's own 3-D Python reference, not the
> authors' output). For engineering orientation: the authors' OWL/OptiX
> artifact, recompiled at `NUM_POINTS=32768` on the same pod and patched from
> device ordinal `1` to `0` for pod compatibility, reported a `6.616 ms` force
> phase under a different OWL/OptiX traversal contract. No speedup ratio should
> be inferred; the tree construction and traversal contracts differ, and this
> is a diagnostic resident-kernel/force-phase comparison only, not a paper
> reproduction or whole-application claim.

## Required Boundaries

The following remain blocked:

- any headline or public claim that RTDL is `13x faster` than RT-BarnesHut;
- any speedup ratio between the `0.509 ms` and `6.616 ms` measurements;
- any RT-BarnesHut paper reproduction claim;
- any same-tree or same-traversal-contract claim;
- any native OptiX/RT-core Barnes-Hut implementation claim for RTDL;
- any whole-application speedup claim including setup, tree build, transfer,
  input generation, or timestep integration;
- any claim that RTDL outputs have been numerically compared against authors'
  per-body force output.

## Engineering Interpretation

The 3-D result is still valuable: it closes the earlier 2-D mismatch and moves
the diagnostic path onto the authors' dimensionality, input file, and scalar
inverse-square force model. The next stronger claim requires either matching
the authors' exact tree/traversal contract or collecting authors per-body force
outputs and proving numeric agreement under a clearly reviewed contract.
