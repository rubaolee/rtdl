# Goal1107 Linux Chunked Baseline Completion

Date: 2026-04-29

## Result

Status: COMPLETE FOR BASELINE INTAKE

Goal1106's chunked Barnes-Hut Embree timing runner completed the missing 20M current-contract non-OptiX baseline on Linux. Goal1102 intake now reports all four baseline rows present and valid.

## Linux Host

- Host: `lx1`
- Checkout path: `/tmp/rtdl_goal1106_chunked`
- Source commit: `87b077894ea6056b0af4e329d006321d41816392`
- Backend: Embree fixed-radius count-threshold prepared runtime

## Command

```text
/usr/bin/time -v env PYTHONPATH=src:. python3 scripts/goal1106_barnes_hut_chunked_embree_timing_baseline.py --body-count 20000000 --chunk-size 250000 --iterations 3 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json
```

## Barnes-Hut 20M Result

| Metric | Value |
| --- | ---: |
| Query count | `20,000,000` |
| Build node count | `65,536` |
| Hit threshold | `4` |
| Chunk size | `250,000` |
| Chunk count | `80` |
| Threshold reached count | `20,000,000` |
| Native query median | `53.904498 s` |
| Point packing median | `41.028221 s` |
| Python postprocess median | `1.886505 s` |
| Wall clock for full command | `5:22.56` |
| Max RSS | `325,240 KB` |
| Exit status | `0` |

The previous non-chunked attempt was killed by signal 9 after reaching about 15 GB RSS. The chunked run completed with about 325 MB max RSS, so the blocker was Python materialization pressure, not an Embree correctness blocker.

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
- `docs/reports/linux_goal1106_logs/barnes_hut_20m_chunked_embree_timing.log`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md`

## Boundary

This closes the missing non-OptiX baseline artifact gap. It does not authorize public RTX speedup claims. The next claim step still requires same-current-contract RTX artifact comparison, public wording review, and 2+ AI consensus.
