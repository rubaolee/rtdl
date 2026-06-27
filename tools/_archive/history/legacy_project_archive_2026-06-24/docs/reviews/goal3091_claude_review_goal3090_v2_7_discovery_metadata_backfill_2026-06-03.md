# Review: Goal3090 v2.7 Discovery Metadata Backfill

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-06-03
Verdict: **accept**

---

## Method

Read-only static review of all five files listed in the handoff. The full test
suite (`47 tests`) could not be executed in this environment. The catalog
already embeds the strict-validation snapshot, and the test file was reviewed
structurally. All findings below are derived from source inspection.

---

## Review Questions

### Q1 — Does `require_discovery_metadata=True` make D-2 executable without changing default validation?

Yes. `_discovery_metadata_missing()` returns `()` immediately when the flag is
`False` (`primitive_hierarchy.py:1127`). The `valid` key in the validation dict
always includes `and not discovery_metadata_missing`; because that term is the
empty tuple in the default call, the gate is a no-op until opted in. The
catalog renderer makes two separate calls (`primitive_catalog.py:37–38`) —
one default, one strict — and surfaces them independently on lines 144 and 149.
The generated catalog at `docs/rtdl_primitive_catalog.md:106,111` confirms
`True` / `True` / `-` for both passes. This is the correct gating pattern: D-2
is now machine-checkable on demand and non-intrusive by default.

### Q2 — Are the backfilled tags, aliases, intent phrases, reference paths, and backend scopes app-agnostic and conservative?

Yes, with no exceptions found.

Intent phrases are factual descriptions of operation contracts (e.g., "fail
closed when exact bounded output capacity is exceeded", "count hits without
returning every witness row"). None reference DBSCAN, robot, Barnes-Hut,
SQL/DBMS, RayJoin, RTNN, collision physics, or any other app-owned domain.

Aliases are short, structural names derived from the node id and outputs (e.g.,
`fail_closed_capacity`, `bounded_capacity`, `scalar_count`). No alias implies
app-level results.

Reference paths point to documented feature README files or the catalog itself.
None points to a paper, an external benchmark, or an unreleased feature doc.

Backend scopes are either explicit production backend lists
(`cpu_python_reference`, `cpu`, `embree`, `optix`) or `metadata_only` for
nodes that are not directly executable (see Q3).

### Q3 — Is `metadata_only` an honest backend marker for abstract layer/overview nodes?

Yes. Three nodes use `backends=("metadata_only",)`:
- `layer.execution_residency` (`stable_behavior`) — abstract layer description
  node; the executable children carry their own backend lists.
- `layer.candidate_experimental` (`candidate_behavior`) — abstract layer
  description for unaccepted candidate pressure.
- `candidate.zero_copy_row_streams` (`candidate_behavior`) — explicitly a
  future primitive with no current implementation.

`("metadata_only",)` is a non-empty tuple and therefore satisfies the
`bool(getattr(node, "backends"))` truthiness check in
`_discovery_metadata_missing()`. The marker accurately represents these nodes
without over-claiming backend coverage.

Minor observation (non-blocking): `layer.traversal`, `layer.bounded_materialization`,
and `layer.reduction` carry concrete backend lists on their layer overview rows,
while `layer.execution_residency` and `layer.candidate_experimental` use
`metadata_only`. The inconsistency is defensible — the traversal and
materialization layers have direct, fully-executable primitives whose backends
logically aggregate upward — but the mixed convention could be clarified in a
future catalog iteration. It does not affect correctness or the machine check.

### Q4 — Does the generated catalog accurately report strict discovery metadata validation?

Yes. `primitive_catalog.py` calls `validate_primitive_hierarchy(require_discovery_metadata=True)`
on line 38 and formats the result into two lines (`149–150`). The current
catalog (`docs/rtdl_primitive_catalog.md:111–112`) shows:

```
- Strict discovery metadata validation valid: `True`
- Strict discovery metadata missing: `-`
```

Both entries are sourced live from the Python hierarchy at generation time.
The test `test_catalog_records_strict_discovery_metadata_snapshot` checks these
exact strings, so any regression would fail closed. The catalog also explicitly
states the `"Promotion metadata enforced by default: False"` line (line 118),
correctly distinguishing strict-mode from the default gate.

### Q5 — Does Goal3090 avoid release, performance, zero-copy, broad RT-core, paper-reproduction, and app-specific native-engine claims?

Yes. Goal3090 adds only metadata fields to existing hierarchy nodes. No node
acquires a new runtime lowering, a new promoted status, or any performance
annotation.

The `candidate.zero_copy_row_streams` node uses `backends=("metadata_only",)`
and intent phrases that begin with "future", correctly not claiming a working
implementation. The catalog claim boundary section (`docs/rtdl_primitive_catalog.md:460–464`)
and the report boundary section (`docs/reports/goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md:18–21`)
both explicitly exclude release readiness, public speedup wording, zero-copy
wording, broad RT-core claims, paper-reproduction claims, stable primitive
promotion, and app-specific native engine logic.

No alias, intent phrase, or reference path in any backfilled node implies any
of these excluded categories.

---

## Summary

All five review questions are answered affirmatively. The `require_discovery_metadata`
flag is correctly opt-in, the backfilled metadata is conservative and
app-agnostic, `metadata_only` is used honestly, the catalog reflects the strict
validation state live, and the goal avoids all listed claim categories. The
minor inconsistency in `metadata_only` usage across layer overview nodes is
noted as optional future cleanup, not a required fix.

---

## Required Follow-Up Fixes

None.

## Optional Future Work

- Normalize the `backends` field on layer overview nodes: either use
  `metadata_only` consistently for all layer-level wrapper rows, or document
  the convention that a layer node inherits backend scope from its children.
  Neither choice affects the machine check; the inconsistency is stylistic.
