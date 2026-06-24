# Goal1103 Claude Review

Date: 2026-04-29

Reviewer: Claude (Sonnet 4.6)

Verdict: **ACCEPT**

## Criteria

### 1. Correctly decomposes the four baseline rows

Pass. The manifest contains exactly four rows in a deliberate execution order:

| Order | Name | Body/copy count | Backend |
| ---: | --- | --- | --- |
| 1 | `barnes_hut_validation_embree` | 4 096 bodies | embree (with validation) |
| 2 | `facility_cpu_oracle` | 2 500 000 copies | cpu_oracle |
| 3 | `facility_embree` | 2 500 000 copies | embree |
| 4 | `barnes_hut_timing_embree` | 20 000 000 bodies | embree (skip-validation) |

Ordering is intentional: the small validation row runs before the 20 M timing row so the timing row is not interpreted in isolation. The `valid` guard (`len(rows) == 4 and all(...)`) enforces count and command-prefix structure at generation time.

### 2. Avoids blind large local runs on a 16 GB Mac

Pass. Three distinct safety levels are assigned and tested:

- `safe_to_run` — row 1 only (4 096 bodies, memory-trivial)
- `prefer_linux_or_windows_large_ram` — rows 2 and 3 (2.5 M facility copies; large array allocation)
- `do_not_run_on_16gb_mac_without_user_approval` — row 4 only (20 M bodies; likely OOM on 16 GB)

The test `test_current_mac_recommendations_do_not_blindly_run_large_rows` pins all four values explicitly, so a future edit that silently softens a recommendation will fail CI.

### 3. Preserves no-public-speedup-claim boundaries

Pass. The `boundary` field reads:

> Goal1103 is an execution manifest only. It does not run full baselines, does not start cloud, and does not authorize public RTX speedup claims.

This string appears in the JSON artifact, in the Markdown preamble, and again in the Markdown `## Boundary` section. The test `test_manifest_has_four_ordered_rows_and_no_claim_boundary` asserts the exact substring `"does not authorize public RTX speedup claims"`. The `recommended_next_local_action` value (`run_barnes_hut_validation_embree_then_goal1102_intake`) routes through Goal1102's intake gate rather than any public-claim gate.

### 4. Goal1101/Goal1102 compatible artifact names

Pass. All four `expected_artifact` paths match Goal1102's `EXPECTED` list verbatim (verified against `scripts/goal1102_current_contract_baseline_intake.py`):

| Goal1103 expected_artifact | Goal1102 EXPECTED path |
| --- | --- |
| `…/facility_recentered_2_5m_cpu_oracle_baseline.json` | `DEFAULT_DIR / "facility_recentered_2_5m_cpu_oracle_baseline.json"` ✓ |
| `…/facility_recentered_2_5m_embree_baseline.json` | `DEFAULT_DIR / "facility_recentered_2_5m_embree_baseline.json"` ✓ |
| `…/barnes_hut_depth8_4096_embree_validation_baseline.json` | `DEFAULT_DIR / "barnes_hut_depth8_4096_embree_validation_baseline.json"` ✓ |
| `…/barnes_hut_depth8_20m_embree_timing_baseline.json` | `DEFAULT_DIR / "barnes_hut_depth8_20m_embree_timing_baseline.json"` ✓ |

The output directory `docs/reports/goal1101_current_contract_non_optix_baselines` matches Goal1102's `DEFAULT_DIR`. Every command invokes `scripts/goal1101_current_contract_non_optix_baseline_profiler.py`, which is the profiler defined in Goal1101.

## Minor Observation (non-blocking)

The facility rows use `--copies 2500000` but Goal1102 validates against `query_count: 10_000_000`. The 4× relationship is implicit (Goal1101's profiler presumably expands copies to queries internally). Goal1103 is not responsible for documenting this multiplier, but a reader unfamiliar with the profiler may wonder why the numbers differ. No action required here; the artifact names are correct and the count check belongs to Goal1102's intake validation.

## Test Coverage

Four tests cover all review criteria:

| Test | Criteria covered |
| --- | --- |
| `test_manifest_has_four_ordered_rows_and_no_claim_boundary` | Row count, ordering, boundary string |
| `test_current_mac_recommendations_do_not_blindly_run_large_rows` | 16 GB Mac safety levels |
| `test_commands_target_goal1101_profiler_and_goal1102_artifact_names` | Artifact name and directory compatibility |
| `test_markdown_includes_row_by_row_commands` | Markdown output completeness |

## Boundary

This review covers Goal1103 (execution manifest) only. It does not constitute a baseline review, a performance claim, or authorization for public RTX speedup statements.
