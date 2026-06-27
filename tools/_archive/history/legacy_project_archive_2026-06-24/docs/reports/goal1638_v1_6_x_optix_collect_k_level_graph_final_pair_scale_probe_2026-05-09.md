# Goal1638 v1.6.x OptiX Collect-K Level Graph Final-Pair Scale Probe

## Verdict

`bounded_positive_diagnostic_not_production_ready`

The existing collect-k compact-level CUDA graph replay probe shows a small positive replay-only signal at the largest legal single-pair diagnostic size, but it does not yet justify reviving graph replay as a production `COLLECT_K_BOUNDED` optimization.

## Scope

- Probe: `scripts/goal1557_v1_5_4_optix_collect_k_level_graph_probe.py`.
- Native entry: `rtdl_optix_collect_k_level_graph_replay_probe`.
- Sequence measured by the existing probe: materialize, mark, device-prefix, compact.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Git commit on pod: `7a2b4329a4de0d1ab41192992b65f032e3a404ec`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Artifact: `docs/reports/goal1638_level_graph_pair1_segment65536_repeats1000.json`.

## Result

The initial intended final-pair scale attempt used `pair_count=1`, `segment_capacity=131072`, and `repeats=100`, but the existing native probe rejected it because its total block count guardrail is `1..512`.

The largest legal single-pair diagnostic run used `pair_count=1`, `segment_capacity=65536`, and `repeats=1000`:

| field | value |
| --- | ---: |
| direct_per_replay_us | 55.437160 |
| graph_per_replay_us | 53.254800 |
| direct_over_graph_speedup | 1.040980x |
| first_pair_count | 131072 |

## Interpretation

Goal1637 showed that the final-pair mark kernel itself is small while the host-visible wait is much larger. This Goal1638 probe says the old compact-level CUDA graph replay path can reduce replay overhead slightly at a bounded diagnostic scale, but the benefit is small and the existing probe cannot cover the current `segment_capacity=131072` final-pair target.

The next production-relevant direction is not to blindly re-enable the old graph replay path. A future candidate should either measure a prepared end-to-end stable-topology graph for the real final-pair scale, or restructure the final merge/mark/prefix/compact dependency chain so that the measured wait in Goal1637 is reduced under normal `COLLECT_K_BOUNDED` execution.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
