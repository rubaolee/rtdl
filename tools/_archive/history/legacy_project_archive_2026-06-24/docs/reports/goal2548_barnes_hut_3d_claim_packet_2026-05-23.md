# Goal2548 Barnes-Hut 3-D Claim Packet

Date: 2026-05-23

## Purpose

This packet defines the strongest Barnes-Hut statement currently supported by
the Goal2543-2547 evidence, and explicitly separates it from unsupported
authors-code, paper-reproduction, and public-speedup claims.

The user requested stronger Barnes-Hut claims, specifically moving the RTDL
prototype from the earlier 2-D vector force contract to a 3-D contract closer
to the RT-BarnesHut artifact. Goal2547 implements that 3-D diagnostic path.

## Evidence Inputs

Primary RTDL evidence:

- `docs/reports/goal2544_barnes_hut_subtree_containment_pod_32768_2026-05-23.json`
- `docs/reports/goal2545_barnes_hut_resident_state_pod_32768_2026-05-23.json`
- `docs/reports/goal2546_barnes_hut_float32_subtree_pod_32768_r20_2026-05-23.json`
- `docs/reports/goal2547_barnes_hut_3d_scalar_subtree_pod_authors_input_32768_2026-05-23.json`

Authors-code evidence:

- `docs/reports/goal2543_barnes_hut_authors_code_optix_timing_2026-05-23.md`
- `docs/reports/goal2543_barnes_hut_authors_code_raw_timing_2026-05-23.txt`

Rollup report:

- `docs/reports/goal2545_2547_barnes_hut_resident_float32_3d_optimization_2026-05-23.md`

## Environment

Pod used for the evidence:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Device:

`NVIDIA RTX A5000`, driver `565.57.01`

The authors' OWL/OptiX artifact was built and timed on the same pod after
installing OptiX SDK 8.1 and CUDA 12.6. For the 32,768-body measurement, the
authors' artifact was recompiled at `NUM_POINTS=32768` for size-matched
diagnostic comparison, and its device ordinal was patched from `1` to `0` for
the one-GPU pod.

## Supported Technical Facts

At 32,768 bodies:

| Path | Resident/force min | Contract |
|---|---:|---|
| Goal2542 RTDL 2-D rope float64 | `37.036 ms` | 2-D vector force, generic RTDL tree |
| Goal2544 RTDL 2-D subtree float64 | `3.971 ms` | 2-D vector force, generic RTDL tree |
| Goal2545 RTDL 2-D resident repeated float64 | `3.565 ms` | 2-D vector force, prepared state reused |
| Goal2546 RTDL 2-D subtree float32 | `0.473 ms` | 2-D vector force, float32 diagnostic |
| Goal2547 RTDL 3-D scalar float32 | `0.509 ms` | 3-D scalar inverse-square force, authors input, generic RTDL tree |
| Authors OWL/OptiX force phase | `6.616 ms` | authors artifact recompiled at 32,768 bodies, 3-D scalar inverse-square force |

Goal2547 metadata records:

- `same_dimension_as_authors`: `true`
- `same_scalar_inverse_square_force_shape_as_authors`: `true`
- `same_tree_contract_as_authors`: `false`
- `public_speedup_claim_authorized`: `false`

Goal2547 correctness against RTDL's own Python 3-D scalar reference at 32,768
bodies:

- visited-node delta: `0`
- contribution-row delta: `0`
- max scalar relative error: `4.329e-05`
- mean scalar relative error: `1.741e-07`

## Strongest Currently Defensible Claim

The strongest claim currently supported is:

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

This is intentionally a strong but bounded statement. It is stronger than the
earlier 2-D vector comparison because it shares the authors' dimensionality,
input file, and scalar inverse-square force shape. It is still weaker than a
same-contract claim because the RTDL prototype does not yet reproduce the
authors' exact tree construction, triangle encoding, autorope traversal, or
OWL/OptiX RT-core execution path.

## Not Authorized

Do not claim:

- RTDL reproduces the RT-BarnesHut paper result.
- RTDL is `13x faster` than the authors' implementation as a public speedup
  claim.
- any speedup ratio between the `0.509 ms` and `6.616 ms` measurements.
- RTDL and the authors' artifact execute the same tree/traversal contract.
- RTDL native OptiX already implements Barnes-Hut fused traversal.
- The result is a whole-application speedup including setup, tree build, input
  generation, host-to-device preparation, or timestep integration.

## Next Gate For A Stronger Claim

To upgrade from this bounded diagnostic claim to a same-contract claim, one of
these must happen:

- implement the authors' exact 3-D tree/traversal contract in the RTDL
  diagnostic path and compare outputs/timings on the same input;
- patch the authors' artifact to dump per-body force outputs and prove numeric
  agreement with a clearly documented RTDL contract variant;
- implement the generic 3-D scalar aggregate-frontier primitive in native
  OptiX/RTDL and compare it against both RTDL Python reference and the authors'
  artifact under an externally reviewed boundary.
