# Goal1633 v1.6.x OptiX Collect-K Plain Fused Negative Probe

## Verdict

`plain_fused_materialize_mark_not_selected`

The existing plain fused materialize+mark diagnostic is not selected as the next production collect-k optimization candidate.

## Scope

- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build state: latest pod checkout after the Goal1631/Goal1632 evidence, using `build/librtdl_optix.so`.
- Probe command: `python3 scripts/goal1565_v1_5_4_optix_collect_k_fused_materialize_mark_probe.py --library build/librtdl_optix.so --repeats 100 --pair-counts 1 2 4 --segment-capacity 131072 --json-out docs/reports/goal1633_plain_fused_probe_segment131072_repeats100.json`.
- Artifact: `docs/reports/goal1633_plain_fused_probe_segment131072_repeats100.json`.

## Result

| pair_count | reference_us | fused_us | reference_over_fused | parity |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 114.604190 | 140.043910 | 0.818345 | mismatch_count=0 |
| 2 | 174.919440 | 214.711510 | 0.814672 | mismatch_count=0 |
| 4 | 303.912590 | 340.756170 | 0.891877 | mismatch_count=0 |

The fused path preserved parity in this diagnostic, but it was slower than the reference path for all measured cases.

## Next Work

Do not integrate the plain fused materialize+mark path into production collect-k based on this evidence.

Together with Goal1632, this points the next investigation away from materialize+mark fusion and toward final pair merge orchestration: final prefix/count handling, compact launch shape, and host synchronization boundaries.

## Claim Boundary

This is internal negative diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
