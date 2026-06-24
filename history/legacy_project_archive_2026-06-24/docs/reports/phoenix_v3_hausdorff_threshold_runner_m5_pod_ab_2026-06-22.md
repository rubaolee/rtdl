# Phoenix V3 Hausdorff Threshold Runner M5 POD A/B

Date: 2026-06-22
Status: `valid_negative_evidence_not_third_set_a_material_win`

## Verdict

The focused pod evidence is valid, but it does not pass the pre-registered
Hausdorff M5 gate.

The productized runner route executes and preserves the useful OptiX-over-Embree
threshold-summary result, but it regresses by about 2-3% versus the legacy
app-front-door prepared OptiX route. Therefore Hausdorff M5 cannot count as the
third material Set-A runner-backed probe.

No release, all-app rerun, public speedup wording, broad V3-over-V2 wording,
whole-Hausdorff wording, true-zero-copy wording, or V4/external-buffer wording
is authorized.

## Evidence Paths

Remote pod:

```text
host: root@213.173.108.14 -p 11592
gpu: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
remote base: /root/rtdl_v3_rebuild_20260620/current
backup: /root/rtdl_v3_rebuild_20260620/phoenix_v3_patch_backups_20260622_hausdorff_m5
```

Local pulled artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_rerun2_metric_aligned/
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_rerun3_stability/
```

Earlier fail-closed hardware-gate artifact was caused by a script glue bug
calling a non-existent hardware-gate function. It did not run the benchmark.
The script was fixed to call the existing
`v3_optix_hardware_gate.build_payload(...)` API before the serious reruns.

## Configuration

```text
points per side: 1,048,576
copies: 262,144
threshold: 0.4
repeat: 5
warmup: 1
routes:
  - same_contract_embree
  - legacy_app_front_door_prepared_optix
  - productized_prepared_execution_runner
```

## Local And Remote Gates

Local:

```text
py_compile app + pod script: OK
tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test
tests.goal879_hausdorff_threshold_rt_core_subpath_test
tests.goal1132_hausdorff_phase_contract_test

13 tests OK
```

Remote:

```text
py_compile app + pod script: OK
tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test

6 tests OK
```

Remote broader runtime/app focused gate:

```text
tests.v3_phoenix_prepared_execution_session_runner_test
tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test
tests.goal879_hausdorff_threshold_rt_core_subpath_test
tests.goal1132_hausdorff_phase_contract_test

42 tests OK
```

Remote wording gate was not used as a pod blocker because that remote tree does
not contain the full current local `docs/rebuild/v3` documentation corpus; the
same wording/scorecard gate passed locally before pod work.

## Results

Sample `rerun2_metric_aligned`:

| Comparison | Query | Phase Total | Wrapper Wall |
| --- | ---: | ---: | ---: |
| Legacy OptiX vs Embree | 1.644x | 1.250x | 1.562x |
| Runner OptiX vs Embree | 1.642x | 1.220x | 1.541x |
| Runner vs Legacy | 0.999x | 0.976x | 0.987x |

Failed checks:

```text
runner_regressed_vs_legacy_phase_total
```

Sample `rerun3_stability`:

| Comparison | Query | Phase Total | Wrapper Wall |
| --- | ---: | ---: | ---: |
| Legacy OptiX vs Embree | 1.648x | 1.242x | 1.554x |
| Runner OptiX vs Embree | 1.600x | 1.211x | 1.519x |
| Runner vs Legacy | 0.971x | 0.975x | 0.978x |

Failed checks:

```text
runner_regressed_vs_legacy_phase_total
runner_regressed_vs_legacy_wrapper_wall
```

## Interpretation

Positive:

- The productized runner route executes both directed legs.
- The route preserves oracle parity.
- The route carries the required metadata boundaries.
- Threshold rows are not materialized on host.
- Prepared search-structure residency is reported.
- True zero-copy and V4 external-buffer claims remain false.
- Runner OptiX still beats same-contract Embree by about 1.21-1.22x
  phase-total on the large row.

Negative:

- The runner does not beat or match the legacy app-front-door prepared OptiX
  route under the pre-registered no-regression gate.
- The regression is small but repeated across two independent serious samples.
- Therefore the result is not a third Set-A material runner-backed win.

Root cause reading:

- Hot query is near parity in the metric-aligned sample, so the primitive itself
  is not the problem.
- The remaining loss is runner/session wrapper overhead and prepare/input
  phase variance.
- This is exactly why broad V3 cannot be claimed from old app-front-door rows:
  the productized runtime trunk must carry the win, not merely wrap an old win.

## Resource Use

Approximate pod benchmark wall time:

```text
fail-closed hardware-gate attempt: negligible benchmark cost
rerun2 serious sample: about 2.7 minutes
rerun3 serious sample: about 2.6 minutes
remote smoke/gates/sync overhead: a few minutes
estimated paid pod cost at $1/4h: well under $0.25
```

## Next Action

Do not spend more pod time trying to rescue Hausdorff M5 by repeating the same
run.

Request second-AI result review. If accepted, classify Hausdorff M5 as valid
negative evidence and choose the next path:

- either implement a generic runner-overhead reduction that helps all runner
  routes, then rerun a focused no-regression test;
- or choose another third Set-A family by 2-AI consensus.

Do not all-app rerun.

## Goal-Level Decision Audit

Decision: classify the Hausdorff M5 focused POD result as negative and stop
repeating the same run.

1. Was I foolish?

   No for this decision. The pre-registered no-regression gate failed twice,
   so stopping avoids spending pod time to chase noise.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be counting OptiX-over-Embree as a
   Phoenix trunk win while ignoring the runner regression versus the legacy
   app-front-door route.

3. Was there another path?

   Yes. I could keep rerunning until one sample passes, or lower the
   no-regression bar after seeing the result. Both would be dishonest.

4. Can I now try a different path that actually solves the problem?

   Yes. Treat this as useful negative evidence: the generic route exists, but
   the productized runner still has overhead. Either fix runner overhead as a
   generic runtime issue or select a different third Set-A family with 2-AI
   consensus.
