# Goal3864 - Full Scale Refresh After LibRTS Multi-Operation Probe

Date: 2026-06-08

Status: internal scale-profile refresh.

## Purpose

Goal3862 added the generic prepared AABB multi-operation count path:

```text
rtdl_optix_count_prepared_aabb_index_2d_multi_operation_packed_queries
```

Goal3864 reruns the full ten-app current scale-profile packet after that native rebuild and LibRTS app routing change.

## Evidence

Pod:

```text
ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519
```

Artifact directory:

```text
docs/reports/goal3864_full_scale_after_librts_multi_operation_a5000/
```

Command:

```text
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-json docs/reports/goal3864_full_scale_after_librts_multi_operation_a5000/summary.json \
  --output-dir docs/reports/goal3864_full_scale_after_librts_multi_operation_a5000/outputs \
  --heartbeat-sec 20
```

## Result

All ten rows passed.

| App | Status | Process sec |
| --- | --- | ---: |
| `hausdorff_xhd` | pass | 1.752 |
| `spatial_rayjoin` | pass | 1.502 |
| `rt_dbscan` | pass | 3.503 |
| `robot_collision` | pass | 1.525 |
| `contact_manifold` | pass | 0.752 |
| `raydb_style` | pass | 2.002 |
| `barnes_hut` | pass | 1.752 |
| `librts_spatial_index` | pass | 2.003 |
| `rtnn` | pass | 2.753 |
| `triangle_counting` | pass | 1.502 |

The LibRTS row confirms the new generic route:

```text
multi_operation_native_used: true
payload elapsed_sec: 0.840265
prepared query median sec: 0.032481
claim_flag_violations: []
```

The full packet also preserves the current registry boundary:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_rt_core_claim_authorized: false
paper_reproduction_claim_authorized: false
```

## External Review Note

Gemini Flash produced a read-only review at:

```text
docs/reviews/goal3863_gemini_review_goal3859_3862_perf_chain_2026-06-08.md
```

Verdict: `accept-with-boundary`.

That review is useful as a boundary check but should not be treated as canonical for the exact Goal3859 CuPy ratio because it used rounded or misread RT-DBSCAN timings in one paragraph. The authoritative Goal3859 artifact ratio remains:

```text
new_vs_cupy_ratio: 1.0170780716207275
```

## Boundary

This goal does not authorize:

- release action;
- public speedup wording;
- whole-app acceleration claims;
- broad RT-core claims;
- paper reproduction claims;
- true zero-copy claims;
- automatic partner selection claims;
- app-specific native-engine logic.

The accepted conclusion is narrower: after Goal3862, the current ten-app scale-profile packet still passes, and the LibRTS row now exercises the generic AABB multi-operation path.

