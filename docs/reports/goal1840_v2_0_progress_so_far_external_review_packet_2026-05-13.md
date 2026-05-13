# Goal1840 v2.0 Progress So Far: External Review Packet

Date: 2026-05-13
Status: `needs-external-review`

## Purpose

This packet summarizes RTDL v2.0 progress so far for independent external
review. It is not a release decision and does not authorize a v2.0 tag.

The governing release gate is still Goal1814/Goal1818: v2.0 remains blocked
until the strict Python+partner+RTDL birth blockers are solved or explicitly
removed by a later 3-AI consensus.

## Current Verdict

Codex-side verdict:

- v2.0 implementation progress: `accept-with-boundary`
- v2.0 release readiness: `needs-more-evidence`

The strongest new evidence since the strict birth gate is that the OptiX
prepared 2-D ray/triangle any-hit primitive now has a measured Torch/CuPy path
with partner-owned CUDA inputs and partner-owned CUDA output flags.

That is a real zero-copy slice. It is not yet a whole-language or whole-release
zero-copy proof.

## Governing Consensus History

Goal1813 originally accepted a bounded v2.0 release candidate for host-stage
Python+partner+RTDL, but it was superseded by the stricter Goal1814 gate.

Goal1818 is now governing:

- current Python+partner path is real preview evidence;
- v2.0 remains `needs-more-evidence`;
- release remains blocked until the strict blockers are solved or explicitly
  removed by new 3-AI consensus.

Key files:

- `docs/reviews/goal1813_3ai_consensus_v2_0_release_readiness_2026-05-13.md`
- `docs/reviews/goal1818_3ai_consensus_goal1814_strict_v2_birth_gate_2026-05-13.md`

## Evidence Chain Since The Strict Gate

### Direct Device Descriptor Foundation

Goals 1819 and 1821 established the fail-closed direct device-pointer
descriptor boundary.

Accepted evidence:

- RTDL can observe partner CUDA device pointers through the Python partner
  protocol.
- The descriptor API does not by itself authorize zero-copy claims.
- OptiX device descriptor paths fail closed until native ABI support exists.

Key files:

- `docs/reports/goal1819_partner_direct_device_pointer_descriptor_2026-05-13.md`
- `docs/reviews/goal1820_gemini_review_goal1819_direct_device_descriptor_2026-05-13.md`
- `docs/reports/goal1821_optix_partner_device_descriptor_fail_closed_2026-05-13.md`
- `docs/reviews/goal1822_gemini_review_goal1821_optix_device_descriptor_fail_closed_2026-05-13.md`

### Device Ray Columns And Triangle Scene

Goals 1823, 1826, 1828, and 1829 moved from descriptors to native execution
pieces:

- partner-owned CUDA ray columns;
- partner-owned CUDA triangle columns;
- native OptiX ABI bindings;
- RTX pod validation packet and ctypes binding repair.

This phase was important but not yet true whole-primitive input zero-copy,
because some paths still packed/staged data into RTDL-owned native layouts.

Key files:

- `docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md`
- `docs/reviews/goal1824_gemini_review_goal1823_optix_device_ray_columns_2026-05-13.md`
- `docs/reports/goal1826_optix_partner_device_triangle_scene_2026-05-13.md`
- `docs/reviews/goal1827_gemini_review_goal1826_optix_device_triangle_scene_2026-05-13.md`
- `docs/reports/goal1828_optix_device_column_pod_validation_packet_2026-05-13.md`
- `docs/reports/goal1829_optix_device_column_pod_binding_fix_2026-05-13.md`
- `docs/reviews/goal1830_claude_review_goal1829_optix_device_column_pod_evidence_2026-05-13.md`

### Ray-Column True Zero-Copy Slice

Goal1831 established ray-side true zero-copy for the prepared OptiX any-hit
path.

Accepted claim:

> OptiX can read partner-owned CUDA ray columns directly for the prepared
> 2-D ray/triangle any-hit count path.

Boundary:

- triangle scene was still separate;
- whole-primitive zero-copy was not authorized;
- release readiness stayed blocked.

Key files:

- `docs/reports/goal1831_optix_ray_column_true_zero_copy_slice_2026-05-13.md`
- `docs/reviews/goal1832_claude_review_goal1831_optix_ray_column_zero_copy_2026-05-13.md`
- `docs/reviews/goal1833_claude_review_goal1831_pod_evidence_2026-05-13.md`
- `docs/reports/goal1831_optix_ray_column_true_zero_copy_pod_validation.json`

### Whole-Primitive Input Zero-Copy

Goal1834 extended the path to whole-primitive input zero-copy for Torch:

- partner-owned CUDA ray columns;
- partner-owned CUDA triangle columns;
- partner-owned contiguous `float32[N, 6]` AABB tensor;
- no RTDL-owned ray, triangle, or AABB input staging buffers for this path.

Accepted claim:

> The OptiX prepared 2-D ray/triangle any-hit primitive can execute from
> partner-owned Torch CUDA ray columns, triangle columns, and AABB tensor inputs
> without RTDL ray/triangle/AABB staging or repacking.

Boundary:

- OptiX GAS output remains native acceleration state;
- no broad RT-core speedup claim;
- no v2.0 release authorization.

Key files:

- `docs/reports/goal1834_optix_whole_primitive_input_zero_copy_2026-05-13.md`
- `docs/reviews/goal1835_claude_review_goal1834_input_zero_copy_2026-05-13.md`
- `docs/reports/goal1834_optix_whole_primitive_input_zero_copy_pod_validation.json`

### CuPy Conformance For Input Zero-Copy

Goal1836 confirmed the same input zero-copy contract with CuPy.

Important implementation detail:

- Torch reports contiguous strides in elements, such as `(1,)` and `(6, 1)`.
- CuPy reports contiguous byte strides, such as `(8,)`, `(4,)`, and `(24, 4)`.
- RTDL now accepts both forms only for the known contiguous layouts.

Pod artifact:

- GPU: NVIDIA RTX A4500
- partner: CuPy 14.0.1
- `observed_count == expected_count == 1`
- ray and triangle metadata: `source_protocols: ["cupy"]`
- `true_zero_copy_authorized: true`
- `rt_core_speedup_claim_authorized: false`
- `v2_0_release_authorized: false`

Key files:

- `docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_2026-05-13.md`
- `docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_pod_validation.json`

External review status:

- Review handoffs exist for Claude and Gemini.
- Gemini Flash was capacity-blocked during one attempt, and a later Gemini
  attempt produced an incomplete stub that was removed rather than counted.
- Goal1836 still needs a valid external review if it will be used as release
  evidence.

Key handoffs:

- `docs/handoff/HANDOFF_GEMINI_GOAL1837_GOAL1836_CUPY_ZERO_COPY_REVIEW.md`
- `docs/handoff/HANDOFF_CLAUDE_GOAL1837_GOAL1836_CUPY_ZERO_COPY_REVIEW.md`

### Partner-Owned Output Flags

Goal1838 added the first partner-owned output path for the same OptiX primitive.

New native entry point:

- `rtdl_optix_write_prepared_ray_anyhit_2d_device_flags`

Accepted Codex-side claim:

> The OptiX prepared 2-D ray/triangle any-hit primitive can read partner-owned
> Torch or CuPy CUDA input columns and write per-ray any-hit flags into a
> partner-owned Torch or CuPy CUDA output vector without RTDL-owned input or
> output staging buffers.

Pod artifacts:

- CuPy artifact: `observed_flags: [1, 0]`
- Torch artifact: `observed_flags: [1, 0]`
- both have `observed_count == expected_count == 1`
- both keep `rt_core_speedup_claim_authorized: false`
- both keep `v2_0_release_authorized: false`

Key files:

- `docs/reports/goal1838_optix_partner_owned_output_flags_zero_copy_2026-05-13.md`
- `docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json`
- `docs/reports/goal1838_optix_partner_owned_output_flags_torch_pod_validation.json`
- `tests/goal1838_optix_partner_owned_output_flags_zero_copy_test.py`

External review status:

- `docs/handoff/HANDOFF_EXTERNAL_GOAL1839_GOAL1838_OUTPUT_ZERO_COPY_REVIEW.md`
  is ready.
- Gemini produced an incomplete review stub with blank findings/verdicts. It
  was deleted and must not be counted as consensus.
- Goal1838 needs a valid Claude or Gemini review before it is counted as
  external consensus evidence.

## Current Technical Surface

Currently proven with pod evidence:

- OptiX prepared 2-D ray/triangle any-hit primitive.
- Torch CUDA input columns.
- CuPy CUDA input columns.
- Torch CUDA output flags.
- CuPy CUDA output flags.
- Partner-owned AABB tensor for GAS input.
- Native OptiX execution on NVIDIA RTX A4500.

Still not proven:

- broad RT-core speedup;
- whole-app acceleration;
- arbitrary PyTorch/CuPy program acceleration;
- partner-owned outputs for other primitives;
- zero-copy for Embree, because Embree is CPU and not a CUDA device-pointer
  backend;
- package-install release surface beyond source-tree execution;
- full v2.0 learner documentation for the now-upgraded zero-copy path;
- valid external consensus for Goals 1836 and 1838.

## Validation Snapshot

Latest focused local validation after Goal1838:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1671_v1_8_v2_0_partner_gate_test \
  tests.goal1675_partner_protocol_substrate_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1819_partner_direct_device_pointer_descriptor_test \
  tests.goal1821_optix_partner_device_descriptor_fail_closed_test \
  tests.goal1823_optix_partner_device_ray_columns_partial_abi_test \
  tests.goal1826_optix_partner_device_triangle_scene_test \
  tests.goal1828_optix_device_column_pod_validation_packet_test \
  tests.goal1831_optix_ray_column_true_zero_copy_slice_test \
  tests.goal1834_optix_whole_primitive_input_zero_copy_test \
  tests.goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_test \
  tests.goal1838_optix_partner_owned_output_flags_zero_copy_test
```

Result:

```text
Ran 52 tests
OK
```

Pod validation after Goal1838:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy --goal Goal1838 --output-flags \
  --output docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner torch --goal Goal1838-Torch --output-flags \
  --output docs/reports/goal1838_optix_partner_owned_output_flags_torch_pod_validation.json
```

Result:

```text
CuPy: pass, observed_flags [1, 0]
Torch: pass, observed_flags [1, 0]
```

## External Review Questions

External reviewers should answer:

1. Does Goal1838 genuinely close the first input-plus-output true zero-copy
   slice for the OptiX prepared 2-D any-hit primitive?
2. Are the Python validators narrow enough, especially for CuPy byte strides
   and output buffer dtype/shape/stride/device checks?
3. Are the reports careful enough about OptiX GAS state, avoiding a false
   "no native state" claim?
4. Does the current evidence reduce any of the Goal1814 blockers, and which
   blockers still remain?
5. Should v2.0 remain `needs-more-evidence` after Goal1838?

## Recommended External Verdict

If the reviewers agree with the evidence, the recommended verdict is:

- Goal1836: `accept-with-boundary`
- Goal1838: `accept-with-boundary`
- v2.0 release readiness: `needs-more-evidence`

The strict v2.0 gate should not be relaxed until this evidence is reviewed and
the remaining release blockers are either solved or explicitly scoped out by
new 3-AI consensus.
