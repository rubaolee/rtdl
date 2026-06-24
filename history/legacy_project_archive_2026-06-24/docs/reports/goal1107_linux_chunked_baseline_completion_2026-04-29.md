# Goal1107 Linux Chunked Baseline Completion

Date: 2026-04-29

## Result

Status: COMPLETE FOR BASELINE INTAKE

Goal1106's chunked Barnes-Hut Embree timing runner completed the missing 20M current-contract non-OptiX baseline on Linux. A first radius-`10.0` run exposed a missing radius guard in Goal1102 and was superseded. The corrected radius-`0.1` run matches the Goal1093 current RTX Barnes-Hut contract, and Goal1102 intake now reports all four baseline rows present and valid.

## Linux Host

- Host: `lx1`
- Checkout path: `/tmp/rtdl_goal1108_radius_fix`
- Source commit: `a4a636d96c169362e5c6acea3df20582a3af8a71`
- Backend: Embree fixed-radius count-threshold prepared runtime

## Command

```text
/usr/bin/time -v env PYTHONPATH=src:. python3 scripts/goal1106_barnes_hut_chunked_embree_timing_baseline.py --body-count 20000000 --chunk-size 250000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json
```

## Barnes-Hut 20M Result

| Metric | Value |
| --- | ---: |
| Query count | `20,000,000` |
| Build node count | `65,536` |
| Hit threshold | `4` |
| Radius | `0.1` |
| Chunk size | `250,000` |
| Chunk count | `80` |
| Threshold reached count | `20,000,000` |
| Native query median | `53.465870 s` |
| Point packing median | `40.991653 s` |
| Python postprocess median | `1.886023 s` |
| Wall clock for full command | `5:20.92` |
| Max RSS | `326,732 KB` |
| Exit status | `0` |

The previous non-chunked attempt was killed by signal 9 after reaching about 15 GB RSS. The chunked run completed with about 325 MB max RSS, so the blocker was Python materialization pressure, not an Embree correctness blocker.

The first chunked run used radius `10.0` and is superseded. Goal1102 now guards radius explicitly and accepts only the corrected radius-`0.1` current-contract artifact.

## Intake Result

Goal1102 current-contract baseline intake:

| Metric | Value |
| --- | ---: |
| `row_count` | `4` |
| `ok_count` | `4` |
| `missing_count` | `0` |
| `blocked_count` | `0` |
| `public_speedup_claim_authorized_count` | `0` |

Overall status: `ready_for_2ai_baseline_review_not_public_claim`

Artifact set complete: `true`

## Artifacts

- `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json`
- `docs/reports/linux_goal1108_logs/barnes_hut_20m_chunked_embree_timing_radius_0_1.log`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md`

## Boundary

This closes the missing non-OptiX baseline artifact gap. It does not authorize public RTX speedup claims. The next claim step still requires same-current-contract RTX artifact comparison, public wording review, and 2+ AI consensus.
