# Goal3523: Gemini Review - v2.8 vs v2.3 Same-Contract Comparison Protocol

Date: 2026-06-05

## Verdict

**`accept-with-boundary`**

Goal3523 is ready for pod execution. It successfully establishes a rigorous protocol for comparing v2.8 and v2.3 benchmark performance while preventing the conflation of non-identical contracts. The protocol clearly defines necessary next steps and maintains strict claim boundaries.

## Findings

### 1. Correct Avoidance of Fake Ratios (Pass)

The protocol explicitly addresses and correctly avoids producing misleading all-app v2.8/v2.3 ratios from non-identical contracts. This is achieved through:
*   The `comparison_class` field in `V28VsV23BenchmarkComparisonRow` which clearly categorizes each app's comparison status (e.g., `fresh_same_contract_pod_required` for contract changes).
*   Detailed `boundary` and `required_next_action` descriptions for each app, justifying why most existing artifacts cannot be directly ratioed.
*   The `test_most_rows_require_fresh_same_contract_pod_run` in the unit tests, which validates that a majority of rows correctly require fresh pod evidence due to contract differences.
*   The top-level statement in `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md` reinforcing the necessity to avoid fake all-app ratios.

### 2. All 10 Apps Represented and `contact_manifold` Boundary Correct (Pass)

All 10 v2.8 benchmark applications are correctly represented in the `V2_8_VS_V2_3_COMPARISON_ROWS` list. The `test_all_v2_8_benchmark_apps_are_represented` unit test confirms this coverage.
The `contact_manifold` app correctly states its v2.3 promotion boundary. It is marked as `v2_3_not_promoted`, and its `boundary` message explicitly notes its absence from the v2.3 released app table. This is verified by `test_contact_manifold_records_v2_3_promotion_boundary`.

### 3. Artifact-Ratio Rows (`rt_dbscan`, `triangle_counting`) Bounded Correctly (Pass)

The two apps permitted to have artifact-based ratios (`rt_dbscan`, `triangle_counting`) are appropriately bounded:
*   **`rt_dbscan`**: Marked as `same_output_evolved_runtime_existing_artifact`. The boundary note clarifies that the ratio applies specifically to the grouped-stream path and not to raw RT-count. The `required_next_action` indicates a rerun is still needed for final publication quality.
*   **`triangle_counting`**: Marked as `same_contract_existing_artifact`. The boundary describes it as a "synthetic RT-Graph summary row, not paper-scale graph reproduction." The `required_next_action` notes that while artifacts are close enough for internal status, a rerun is needed for the final table.
Both are clearly designated as "internal" and "triage facts for the pod run," not final public claims, which is critical for maintaining integrity.

### 4. Fresh-Pod-Required Actions are Precise (Pass)

The `required_next_action` descriptions for all `fresh_same_contract_pod_required` rows provide sufficient detail to guide a pod run. Examples include:
*   `hausdorff_xhd`: "Run both threshold-decision and exact-witness rows..."
*   `spatial_rayjoin`: "Run count/parity and overlay-area as two explicit rows..."
*   `robot_collision`: "Run identical pose/obstacle/link counts under v2.3 evidence baseline and v2.8 HEAD, separating setup/warmup/steady-state."
These, combined with the comprehensive "Required Pod Packet" section in the protocol document (specifying environment, workspaces, and run order), ensure a precise and reproducible pod execution.

### 5. Claim Boundaries are Preserved (Pass)

The protocol diligently preserves all specified claim boundaries.
*   The `V2_8_VS_V2_3_COMPARISON_CLAIM_BOUNDARY` constant in the Python source code explicitly lists all disallowed claims (e.g., public release, public speedup, whole-app speedup, broad RT-core, true-zero-copy, etc.).
*   The `V28VsV23BenchmarkComparisonRow` dataclass explicitly sets `public_claim_authorized` and `release_authorized` to `False`, and these are validated in the `__post_init__` method and by unit tests.
*   The dedicated "Claim Boundary" section in the protocol document reiterates these restrictions.
This multi-layered enforcement ensures that no unauthorized public claims can be derived directly from this protocol.
