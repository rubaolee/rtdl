# Goal 1575: OptiX COLLECT_K_BOUNDED Carry Payload Accounting

## Verdict

Goal1575 clarifies profiler accounting for carry handling after the derived carry alias diagnostic.

The existing `carry_copies` field remains a topology counter: it counts levels where an odd carry segment exists. A new `carry_payload_copies` field records actual row-payload device copies. This avoids overstating payload movement when `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` aliases the row payload but still performs the required carry-count device copy.

## Scope

- Repository base measured on pod: `5111c462f62b7f381c784d58754b09c179983fb2` plus the Goal1575 accounting patch.
- Pod: `root@157.157.221.29 -p 22942`, NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- CUDA/OptiX: CUDA `12.8`, OptiX SDK at `/root/vendor/optix-sdk`.
- Counts: `32769`, `65537`, `131072`.

## Results

| Case | Path | Accepted | Parity | carry_copies | carry_payload_copies |
|---:|---|---|---|---:|---:|
| 32769 | Baseline | Yes | Yes | 4 | 4 |
| 65537 | Baseline | Yes | Yes | 5 | 5 |
| 131072 | Baseline | Yes | Yes | 0 | 0 |
| 32769 | Derived carry alias diagnostic | Yes | Yes | 4 | 0 |
| 65537 | Derived carry alias diagnostic | Yes | Yes | 5 | 0 |
| 131072 | Derived carry alias diagnostic | Yes | Yes | 0 | 0 |

Both baseline and alias runs produced accepted Goal1506-style evidence with parity passing and profile topology matching expected.

## Interpretation

The new field confirms the intended distinction:

- `carry_copies`: topology count, useful for validating merge-tree shape.
- `carry_payload_copies`: physical row-payload copy count, useful for measuring whether carry aliasing eliminated payload movement.

The derived carry alias diagnostic still performs carry-count device copies. Therefore `carry_payload_copies=0` does not mean "no carry-related device work"; it means no row payload copy occurred for those carry levels.

## Artifacts

- `docs/reports/goal1575_v1_5_4_optix_collect_k_carry_payload_accounting_alias_profile_2026-05-08.json`
- `docs/reports/goal1575_v1_5_4_optix_collect_k_carry_payload_accounting_alias_profile_2026-05-08.md`
- `docs/reports/goal1575_v1_5_4_optix_collect_k_carry_payload_accounting_baseline_profile_2026-05-08.json`
- `docs/reports/goal1575_v1_5_4_optix_collect_k_carry_payload_accounting_baseline_profile_2026-05-08.md`
