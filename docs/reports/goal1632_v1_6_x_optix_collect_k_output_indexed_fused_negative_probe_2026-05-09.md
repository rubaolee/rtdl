# Goal1632 v1.6.x OptiX Collect-K Output-Indexed Fused Negative Probe

## Verdict

`output_indexed_fused_not_selected`

The existing output-indexed fused materialize+mark diagnostic is not selected as the next production collect-k optimization candidate for the large final-merge bottleneck.

## Scope

- Git source: latest `main` at the time of the pod run, reset on pod before build.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Probe command: `python3 scripts/goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe.py --library build/librtdl_optix.so --repeats 100 --pair-counts 1 2 4 --segment-capacity 131072 --json-out docs/reports/goal1632_output_indexed_fused_probe_segment131072_repeats100.json`.
- Artifact: `docs/reports/goal1632_output_indexed_fused_probe_segment131072_repeats100.json`.

## Result

| pair_count | reference_us | fused_us | reference_over_fused | parity |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 114.570690 | 145.260480 | 0.788726 | mismatch_count=0 |
| 2 | 175.215140 | 241.612280 | 0.725191 | mismatch_count=0 |
| 4 | 303.914290 | 401.266620 | 0.757387 | mismatch_count=0 |

The fused path preserved parity in this diagnostic, but it was slower than the reference path for all measured cases.

## Next Work

Do not integrate the output-indexed fused materialize+mark path into production collect-k based on this evidence.

The remaining large-count bottleneck should be investigated around the final pair merge end-to-end path, especially the final count/prefix/compact sequence and per-call launch/synchronization shape. Any new optimization must stay opt-in until parity, stage profile, focused collect-k sweep, and external review are recorded.

## Claim Boundary

This is internal negative diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
