# Goal 1578: OptiX COLLECT_K_BOUNDED Derived Carry Alias Promotion Readiness

## Verdict

`RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` is the strongest current candidate for OptiX `COLLECT_K_BOUNDED` production promotion, but it should remain diagnostic until one additional NVIDIA architecture validates the same suite.

The evidence now supports the design and single-GPU correctness/performance case. It does not yet support public speedup wording, stable primitive promotion, release action, or default enablement.

## Evidence Summary

| Goal | Outcome | Promotion Signal |
|---|---|---|
| Goal1571 | Host-count pointer carry diagnostic was parity-correct but slower. | Rejected pointer + host-count path. |
| Goal1572 | Device-count pointer carry diagnostic reduced carry copy but increased pointer descriptor overhead. | Rejected pointer descriptor path. |
| Goal1573 | Derived carry alias preserved parity and improved odd-carry long cases. | Positive candidate. |
| Goal1574 | Claude review plus edge validation supported the guard but recommended more coverage. | Keep diagnostic, broaden tests. |
| Goal1575 | Added `carry_payload_copies` so topology carries and physical row-payload copies are distinct. | Profiler accounting clarified. |
| Goal1576 | Blocked-alias topologies validated the guard correctly copies unsafe carries. | Safety evidence strengthened. |
| Goal1577 | Bounded even/odd sweep passed and targeted rerun resolved noisy cases as non-regressing. | Strong single-GPU promotion evidence. |

## External Review

Gemini reviewed this promotion-readiness report and agreed with the conclusion:

- the derived carry alias is the strongest production-promotion candidate,
- it should remain diagnostic until one additional NVIDIA architecture validates the same suite,
- the claim boundaries are appropriately conservative.

Saved review:

- `docs/reviews/goal1578_derived_carry_alias_promotion_readiness_gemini_review_2026-05-08.md`

## What Is Proven

- Parity is clean on the measured RTX 4000 Ada pod.
- The alias path preserves the derived descriptor fast path.
- Pointer descriptor alternatives are worse and should not be promoted.
- The topology guard blocks unsafe aliases and allows safe aliases.
- `carry_copies` remains a merge-tree topology counter.
- `carry_payload_copies` records physical row-payload copies and proves the alias removes payload copies in safe carry levels.
- The bounded even/odd sweep covers bitonic, no-carry, blocked-carry, mixed blocked/safe carry, and safe-carry merge cases.

## What Is Not Proven

- The result is not yet validated on a second NVIDIA architecture.
- The result does not authorize broad RTX/GPU acceleration wording.
- The result does not authorize true zero-copy wording.
- The result does not promote `COLLECT_K_BOUNDED` from experimental to stable.
- The result does not justify release action.

## Promotion Blocker

The only major remaining blocker is hardware diversity.

Run the same focused suite on at least one additional NVIDIA architecture. Good candidates include Ampere, Hopper, Blackwell, or a non-Ada RTX device with enough shared memory for the tiled row-width-2 path.

The local Linux GTX 1070 is not sufficient for accepted performance evidence because prior Goal1508 measurements showed it falls below the shared-memory requirement and predicts the dynamic fallback path for the target counts.

## Next-Pod Validation Commands

After cloning or resetting the pod checkout to `origin/main`, build OptiX:

```bash
cd /root/rtdl_goal1545_pod
git fetch origin main
git reset --hard origin/main
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
```

Run focused static tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_test \
  tests.goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_test \
  tests.goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_test \
  tests.goal1570_v1_5_4_optix_collect_k_carry_alias_implementation_preflight_test
```

Run the baseline bounded sweep:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 \
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 \
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1 \
LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64 \
PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 7 8192 12289 16385 20481 24577 32769 45057 49153 65536 65537 \
  --repeats 5 \
  --profile-jsonl /tmp/goal1578_next_arch_baseline.jsonl \
  --json-out /tmp/goal1578_next_arch_baseline.json \
  --md-out /tmp/goal1578_next_arch_baseline.md
```

Run the alias bounded sweep:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 \
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 \
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1 \
RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1 \
LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64 \
PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 7 8192 12289 16385 20481 24577 32769 45057 49153 65536 65537 \
  --repeats 5 \
  --profile-jsonl /tmp/goal1578_next_arch_alias.jsonl \
  --json-out /tmp/goal1578_next_arch_alias.json \
  --md-out /tmp/goal1578_next_arch_alias.md
```

If any small deltas look suspicious, rerun the targeted suite:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 \
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 \
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 \
RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 \
RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1 \
RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1 \
LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64 \
PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 49153 65536 65537 \
  --repeats 9 \
  --profile-jsonl /tmp/goal1578_next_arch_targeted_alias.jsonl \
  --json-out /tmp/goal1578_next_arch_targeted_alias.json \
  --md-out /tmp/goal1578_next_arch_targeted_alias.md
```

## Promotion Criteria

Promotion becomes reasonable if the second architecture shows:

- accepted Goal1506-style evidence,
- parity passing for all sweep cases,
- profile topology matching expected,
- no correctness failure in blocked aliases,
- no material regression on no-carry cases,
- improvements or neutrality on carry cases after targeted rerun if needed.

If these pass, the next patch should be small:

- either make derived carry alias part of the default fastest OptiX collect-k path when all prerequisite flags are active,
- or fold it into a named fastest-path preset if the project keeps explicit feature flags.

## Claim Boundary

This report is a promotion-readiness artifact only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
