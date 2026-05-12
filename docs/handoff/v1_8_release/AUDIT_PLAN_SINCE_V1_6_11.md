# Audit Plan Since v1.6.11 Release-Candidate Boundary

Date: 2026-05-11

## Purpose

Audit all work since the v1.6.11 release-candidate boundary before treating the
current RTDL state as v1.8/v2.0 release evidence.

The audit must distinguish:

1. **Strict tracked-family native ABI cleanup:** whether lowercase app-shaped
   native callable/export names have been migrated or quarantined.
2. **Broader native app-agnostic readiness:** whether non-strict semantic
   leakage and legacy purity blockers remain.
3. **Release readiness:** whether pod/hardware evidence and distinct-AI
   consensus are sufficient to make any public claim.

Do not treat strict `9/14/0` as a release pass by itself.

## Scope

Audit all local goals and reports after the v1.6.11 release-candidate
checkpoint, especially:

- Goal1668 native app-agnostic directive and baseline.
- Goal1669 Python+partner architecture.
- Goal1670 external partner consensus.
- Goal1671 v1.8/v2.0 partner gate.
- Goal1672 native app-leakage classification.
- Goal1673 through Goal1676 first cleanup and regression guard.
- Goal1677 through Goal1679 pod and full-suite triage.
- Goal1680 current native leakage gap.
- Goal1681 PIP migration.
- Goal1682 Hausdorff migration.
- Goal1683 consensus remediation.
- Goal1684 through Goal1687 independent reviews/reconciliation.
- Goal1688 and Goal1690 BFS migrations.
- Goal1689 and Goal1691 Gemini BFS reviews.
- Goal1692 through Goal1694 Gemini migration plans.
- Goal1695 KNN migration and Goal1696 Gemini review.
- Goal1697 polygon migration and Goal1698 Gemini review.
- Goal1699 DB migration and Goal1700 Gemini review.
- Current post-Goal1700 handoffs for expanded boundary review.

## Primary Questions

1. Are all goal reports present, readable, and internally consistent with their
   tests?
2. Does each architecture, release, or performance-relevant goal have 2+ AI
   consensus from distinct AI systems, not Codex+Codex?
3. Are authoring and reviewing roles disclosed clearly, especially where Claude
   or Gemini also helped produce a migration?
4. Do reports avoid overclaiming v1.8/v2.0 readiness before pod/hardware
   evidence?
5. Does the source tree match the claimed strict native ABI counts?
6. Are Python compatibility APIs preserved while native ABI names are generic?
7. Are remaining non-strict blockers documented and tracked?

## Native ABI Audit

Run or reproduce the strict scan over `src/native/**`:

```text
\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b
```

Expected post-Goal1699 state:

- strict regex unique symbols: `9`
- strict regex occurrences: `14`
- false-positive symbols: `9`
- false-positive occurrences: `14`
- real lowercase callable/export symbols: `0`

The only strict hits should be uppercase `RTDL_DB_*` constants:

- `RTDL_DB_KIND_BOOL`
- `RTDL_DB_KIND_FLOAT64`
- `RTDL_DB_KIND_INT64`
- `RTDL_DB_OP_BETWEEN`
- `RTDL_DB_OP_EQ`
- `RTDL_DB_OP_GE`
- `RTDL_DB_OP_GT`
- `RTDL_DB_OP_LE`
- `RTDL_DB_OP_LT`

Verify old ABI names are absent for:

- PIP family.
- Hausdorff family.
- BFS family.
- KNN family.
- Polygon family.
- DB family.
- Earlier pose/root oracle cleanup.

Verify replacement names are present and used by Python runtime bindings.

## Expanded Semantic Audit

Run a separate read-only search over `src/native/**` for expanded terms from
the v1.7 gate:

- `table`
- `column`
- `edge`
- `vertex`
- `agent`
- `trajectory`

Classify each finding as:

- generic/structural implementation detail,
- false positive,
- legacy non-release/proof surface,
- release blocker.

This audit must not silently ignore expanded-term hits. The result should
become a superseding report before any absolute app-agnostic release claim.

## Purity-Audit Blockers

Run `native_symbol_purity_audit(repo_root=...)` and verify the remaining
legacy customized native symbols.

Current expected blocker set:

- `rtdl_embree_run_lsi`
- `rtdl_optix_run_lsi`
- `rtdl_embree_run_overlay`
- `rtdl_optix_run_overlay`
- `rtdl_embree_run_triangle_probe`
- `rtdl_optix_run_triangle_probe`

Decide for each:

- migrate to generic terminology,
- quarantine outside the release surface,
- or document as a non-release proof path with enforceable gating.

Do not claim native internals are absolutely app-agnostic while these remain
release reachable.

## Partner Track Audit

Confirm the partner architecture remains:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

Check that partner code and reports do not introduce:

- PyTorch-specific native ABI;
- CuPy-specific native ABI;
- app-specific native backdoors;
- claims of zero-copy without measured evidence;
- whole-app speedup wording.

Confirm DLPack/tensor handoff language is protocol-owned and partner-neutral.

## Consensus Audit

For every goal used as release evidence, require:

- at least two independent reviews;
- distinct AI systems, not Codex+Codex;
- explicit reviewer identity;
- clear verdict among `accept`, `accept-with-boundary`, or
  `needs-more-evidence`;
- disclosure when a reviewer also helped author the goal.

Known review artifacts to verify include:

- Goal1684 Gemini review.
- Goal1685 Claude review and follow-up.
- Goal1686 Gemini remaining leakage plan.
- Goal1687 reconciliation.
- Goal1689 Gemini review for Goal1688.
- Goal1691 Gemini review for Goal1690.
- Goal1692 through Goal1694 Gemini plans.
- Goal1696 Gemini review for Goal1695.
- Goal1698 Gemini review for Goal1697.
- Goal1700 Gemini review for Goal1699.
- Pending Claude/Gemini post-Goal1700 boundary reviews.

Any missing/ambiguous goals must be listed and blocked from release evidence
until reviewed.

## Pod And Hardware Evidence Audit

Do not treat local source/test success as pod evidence.

Verify whether each relevant backend has hardware execution evidence:

- Embree local/native execution.
- OptiX build and run with SDK headers and `librtdl_optix.so`.
- HIPRT, Vulkan, Apple RT only if explicitly in release scope.

For accepted pod evidence, require:

- exact command;
- machine/pod identity;
- backend library paths;
- test list;
- pass/fail/skip counts;
- artifact paths;
- date and reviewer;
- explicit claim boundary.

If pod evidence is unavailable, the audit verdict for release readiness must
remain `needs-more-evidence`.

## Required Validation Slice

At minimum, rerun:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal1699_db_to_columnar_payload_native_migration_test `
  tests.goal1680_current_native_app_leakage_gap_test `
  tests.goal1697_polygon_to_shape_native_migration_test `
  tests.goal1695_knn_to_k_closest_hits_native_migration_test `
  tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test `
  tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test `
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test `
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test `
  tests.goal1672_native_app_leakage_migration_classification_test `
  tests.goal1676_native_leakage_delta_regression_test `
  tests.goal1668_native_engine_app_agnostic_directive_test `
  tests.goal1658_python_rtdl_product_checkpoint_test `
  tests.goal1683_consensus_audit_remediation_plan_test `
  tests.goal1671_v1_8_v2_0_partner_gate_test `
  tests.goal1675_partner_protocol_substrate_test
```

Then rerun a broader modified-goal slice if time allows, including Goal467,
Goal513, Goal804, Goal1156, Goal1157, Goal1424, Goal1432, and Goal870.

## Expected Audit Outputs

Create a report:

`docs/reports/goal1703_audit_since_v1_6_11_release_candidate_2026-05-11.md`

Optionally create machine-readable JSON:

`docs/reports/goal1703_audit_since_v1_6_11_release_candidate_2026-05-11.json`

Required verdict fields:

- strict tracked-family cleanup: `accept` if `9/14/0` is verified;
- broader native app-agnostic readiness: likely `accept-with-boundary` or
  `needs-more-evidence` depending on expanded audit and six-symbol handling;
- v1.8 release readiness: `needs-more-evidence` until pod/hardware and
  consensus are complete;
- v2.0 partner readiness: `needs-more-evidence` until partner conformance and
  pod/hardware are complete.

## Immediate Next Tasks

1. Complete Gemini Goal1702 post-Goal1700 boundary audit.
2. Complete Claude Goal1701 independent boundary review when Claude is
   available.
3. Decide whether to migrate/quarantine the six remaining legacy purity symbols
   before pod validation.
4. Run expanded semantic audit and document every `table`, `column`, `edge`,
   `vertex`, `agent`, and `trajectory` finding.
5. Only after the above, plan pod/hardware validation.

## Non-Negotiable Claim Boundary

Until the expanded audit, six-symbol legacy purity decision, pod/hardware
validation, and distinct-AI consensus are complete, do not publish:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording:

```text
The tracked lowercase app-family native ABI cleanup is locally complete, with
strict scan `9/14/0`; release readiness remains blocked pending expanded
semantic audit, remaining legacy purity-symbol disposition, independent
consensus, and pod/hardware validation.
```
