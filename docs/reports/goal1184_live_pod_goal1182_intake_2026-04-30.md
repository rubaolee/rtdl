# Goal1184 Live Pod Goal1182 Intake

Date: 2026-04-30

## Scope

Goal1184 records the live RTX pod execution of the Goal1182 packet and the local
intake result for copied-back artifacts. It is external-review input only and
not release authorization.

## Pod

- SSH target: `root@213.173.108.38 -p 17886`
- SSH key used locally: `~/.ssh/id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX A4500`
- VRAM: `20470 MiB`
- Driver: `550.127.05`
- CUDA reported by driver: `12.4`
- CUDA compiler installed on pod: `13.0.88`

## Source Archive

- Local archive:
  `docs/reports/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz`
- Pod archive:
  `/tmp/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz`
- Source archive SHA256:
  `b5f7c732d927acaaf5daf1ee2840aef6943ab6e01e81138111df73f98fbd5e00`
- Remote archive SHA check: `matched`

## Result Archive

- Remote result:
  `/tmp/goal1182_goal1170_results.tgz`
- Local result:
  `docs/reports/goal1182_live_pod_2026-04-30/goal1182_goal1170_results.tgz`
- Result SHA256:
  `a1dc4f77bc8397cd57cfb30cab57f81fb0201a394d6cf938570556d27987d954`
- Local SHA check: `matched`

## Local Intake

- Intake report:
  `docs/reports/goal1182_live_pod_2026-04-30/goal1182_goal1170_intake_2026-04-30.md`
- Intake JSON:
  `docs/reports/goal1182_live_pod_2026-04-30/goal1182_goal1170_intake_2026-04-30.json`
- Intake status: `valid: true`
- Audit-normalized intake status: `valid: `True``
- Artifact count: `8`
- Valid artifact count: `8`

## Artifact Rows

| Artifact | Intake | Interpretation |
| --- | --- | --- |
| `database_compact_summary.json` | valid | clean-source compact-summary DB evidence; not SQL/DBMS or whole-app speedup wording |
| `graph_visibility_edges.json` | valid | strict-pass graph visibility-edge evidence |
| `road_hazard_native_summary.json` | valid | strict-pass road-hazard prepared native summary evidence |
| `polygon_pair_candidate_discovery.json` | valid | candidate-discovery evidence; exact polygon continuation remains separate |
| `polygon_jaccard_safe_chunk.json` | valid | safe-chunk Jaccard candidate-discovery evidence; exact Jaccard continuation remains separate |
| `hausdorff_threshold_prepared.json` | valid | prepared Hausdorff threshold evidence with oracle match |
| `ann_candidate_65536_timing.json` | valid | timing-only replacement row; no oracle claim in this row |
| `robot_pose_count_262144_timing.json` | valid | timing-only replacement row; no oracle claim in this row |

## Notable Timings

- DB compact-summary prepared warm-query median: `0.09356001392006874` s.
- Hausdorff prepared OptiX query median: `0.0012965835630893707` s.
- ANN candidate timing-only OptiX query median: `0.000985078513622284` s.
- Robot pose-count timing-only prepared query median: `0.00046299397945404053` s.
- Polygon pair candidate discovery phase: `2.950786828994751` s.
- Polygon Jaccard candidate discovery phase: `1.830097883939743` s.

## Boundary

This report records copied-back RTX A4500 artifacts and local intake only. It
does not authorize release, tagging, or new public RTX speedup wording. Public
wording still requires external review and a separate consensus report.

The source-commit field in several artifacts uses the executor label
`goal1175-archive-<sha>`. For this Goal1184 run, the authoritative provenance is
the Goal1182 packet command and archive SHA above:

`b5f7c732d927acaaf5daf1ee2840aef6943ab6e01e81138111df73f98fbd5e00`
