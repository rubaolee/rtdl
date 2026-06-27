# Goal 414 Report: v0.7 RT DB Kernel Surface

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_414_v0_7_rt_db_kernel_surface.md`

Planning basis:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal413_v0_7_rt_db_workload_scope_and_goal_ladder_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`

## Summary

The first RTDL database-style kernel surface for `v0.7` should remain small and
fit the existing RTDL execution model:

- `input`
- `traverse`
- `refine`
- `emit`

The database-style additions should therefore enter as bounded workload
primitives and input types layered on top of the existing kernel model, not as
new language syntax.

## Chosen surface position

The first public kernel family is:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

The surface is built around one logical build input and one logical probe
input.

## Proposed logical input types

### Build-side type

- `rt.DenormTable`

Meaning:

- a denormalized or pre-joined flat analytical record set
- the public logical table contract, not the backend primitive stream

### Probe-side types

- `rt.PredicateSet`
  - bounded predicate bundle for scan/filter workloads
- `rt.GroupedQuery`
  - bounded grouped aggregate query for grouped-count/sum workloads

These are logical query-side inputs. The user writes them as query intent;
lowering/runtime owns the RT encoding details.

## Proposed traverse modes

Keep `rt.traverse(...)`, but extend it with database meaning:

- `mode="db_scan"`
- `mode="db_group"`

The important point is unchanged:

- `traverse` is still candidate generation
- the mode gives it bounded workload-family semantics

## Proposed workload primitives

### 1. `rt.conjunctive_scan(...)`

This is the first bounded scan/filter primitive.

Example intent:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_scan():
    table = rt.input("table", rt.DenormTable, role="build")
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")

    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(
        candidates,
        predicate=rt.conjunctive_scan(exact=True),
    )
    return rt.emit(matches, fields=["row_id"])
```

Meaning:

- the host supplies a denormalized table and a bounded conjunction of
  predicates
- `traverse` explores only the RT query region induced by the predicates
- `refine` performs exact predicate confirmation
- `emit` returns matching rows or projected fields

Expected emitted fields for the first bounded form:

- `row_id`
- optional projected fields if the implementation slice supports them

### 2. `rt.grouped_count(...)`

This is the first grouped aggregate primitive.

Example intent:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_count():
    table = rt.input("table", rt.DenormTable, role="build")
    query = rt.input("query", rt.GroupedQuery, role="probe")

    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_count(group_keys=("group_key_0",)),
    )
    return rt.emit(groups, fields=["group_key_0", "count"])
```

Meaning:

- the host supplies a grouped aggregate query with:
  - scan predicates
  - group key definition
- `traverse` finds candidate records in the query region
- `refine` performs exact match confirmation and grouped counting
- `emit` returns grouped counts

### 3. `rt.grouped_sum(...)`

This is the first numeric grouped aggregate primitive.

Example intent:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_sum():
    table = rt.input("table", rt.DenormTable, role="build")
    query = rt.input("query", rt.GroupedQuery, role="probe")

    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(
            group_keys=("group_key_0",),
            value_field="value_0",
        ),
    )
    return rt.emit(groups, fields=["group_key_0", "sum"])
```

Meaning:

- the host supplies a grouped aggregate query with:
  - scan predicates
  - grouping fields
  - one numeric value field
- `refine` performs exact match confirmation and grouped accumulation
- `emit` returns grouped sums

## Host versus kernel boundary

The host still owns:

- denormalization / pre-join responsibility
- offline encoding/index preparation
- query parsing or user-level query construction
- final result formatting outside the bounded emitted schema

The RTDL kernel owns:

- bounded candidate discovery
- bounded exact refine
- bounded grouped accumulation for the selected primitives

This is the same discipline used by the graph line:

- host owns the outer algorithm/system responsibilities
- the RTDL kernel owns the bounded expensive RT-shaped step

## Public-surface non-goals

The first `v0.7` surface does not expose:

- SQL text
- `join(...)`
- `order_by(...)`
- `having(...)`
- arbitrary aggregate composition
- arbitrary disjunctive predicate trees

Those may exist in surrounding host logic later, but they are not part of the
first RTDL DB kernel surface.

## Design judgment

The right first database-style surface is not a mini query language.

It is a bounded set of workload primitives layered on:

- logical denormalized table inputs
- logical query-side probe inputs
- the existing `input -> traverse -> refine -> emit` RTDL kernel form

That keeps `v0.7` aligned with the accepted RTDL design direction and makes the
next implementation goals concrete.
