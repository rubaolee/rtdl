"""
Attacking test suite for RTDL v0.7 DB workloads.

Covers conjunctive_scan, grouped_count, grouped_sum across:
- all six predicate operators
- edge cases: empty table, no matches, all match, single row
- boundary arithmetic (between inclusive, le/ge vs lt/gt)
- multi-predicate AND semantics
- multi-key GROUP BY ordering
- integer vs float sums, negative values, zero
- dict / tuple / dataclass input normalization paths
- error contract: invalid ops, missing row_id, missing fields
- SQL generation for every operator
- FakePostgresqlConnection roundtrip for all three workloads
- cpu vs cpu_python_reference agreement
- kernel compilation contract (traverse mode, input roles, emit fields)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.db_reference import (
    PredicateClause,
    PredicateBundle,
    GroupedAggregateQuery,
    conjunctive_scan_cpu,
    grouped_count_cpu,
    grouped_sum_cpu,
    normalize_predicate_bundle,
    normalize_grouped_query,
    normalize_denorm_table,
)
from rtdsl.db_postgresql import (
    FakePostgresqlConnection,
    build_postgresql_conjunctive_scan_sql,
    build_postgresql_grouped_count_sql,
    build_postgresql_grouped_sum_sql,
    run_postgresql_conjunctive_scan,
    run_postgresql_grouped_count,
    run_postgresql_grouped_sum,
)


# ---------------------------------------------------------------------------
# Shared kernel definitions
# ---------------------------------------------------------------------------

@rt.kernel(backend="rtdl", precision="float_approx")
def scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


# ---------------------------------------------------------------------------
# Canonical test tables
# ---------------------------------------------------------------------------

SALES_TABLE = (
    {"row_id": 1, "region": "east", "ship_date": 10, "discount": 5,  "quantity": 12, "revenue": 5},
    {"row_id": 2, "region": "west", "ship_date": 11, "discount": 8,  "quantity": 30, "revenue": 8},
    {"row_id": 3, "region": "east", "ship_date": 12, "discount": 6,  "quantity": 18, "revenue": 6},
    {"row_id": 4, "region": "west", "ship_date": 13, "discount": 6,  "quantity": 10, "revenue": 10},
    {"row_id": 5, "region": "west", "ship_date": 13, "discount": 6,  "quantity":  8, "revenue": 2},
    {"row_id": 6, "region": "north", "ship_date": 9, "discount": 3,  "quantity":  5, "revenue": 1},
)

FLOAT_TABLE = (
    {"row_id": 1, "region": "a", "value": 1.5, "score": 0.1},
    {"row_id": 2, "region": "a", "value": 2.5, "score": 0.9},
    {"row_id": 3, "region": "b", "value": 3.0, "score": 0.5},
    {"row_id": 4, "region": "b", "value": -1.0, "score": 0.2},
)


def _run_scan(predicates, table=None):
    return rt.run_cpu_python_reference(
        scan_kernel,
        predicates=predicates,
        table=table if table is not None else SALES_TABLE,
    )


def _run_scan_cpu(predicates, table=None):
    return rt.run_cpu(
        scan_kernel,
        predicates=predicates,
        table=table if table is not None else SALES_TABLE,
    )


def _run_count(query, table=None):
    return rt.run_cpu_python_reference(
        count_kernel,
        query=query,
        table=table if table is not None else SALES_TABLE,
    )


def _run_sum(query, table=None):
    return rt.run_cpu_python_reference(
        sum_kernel,
        query=query,
        table=table if table is not None else SALES_TABLE,
    )


# ===========================================================================
# 1. Kernel compilation contract
# ===========================================================================

class TestKernelCompilation(unittest.TestCase):
    def test_scan_kernel_compiled_shape(self):
        k = rt.compile_kernel(scan_kernel)
        names = tuple(i.geometry.name for i in k.inputs)
        self.assertEqual(names, ("predicate_set", "denorm_table"))
        self.assertEqual(k.candidates.mode, "db_scan")
        self.assertEqual(k.refine_op.predicate.name, "conjunctive_scan")
        self.assertTrue(k.refine_op.predicate.options["exact"])
        self.assertEqual(k.emit_op.fields, ("row_id",))

    def test_count_kernel_compiled_shape(self):
        k = rt.compile_kernel(count_kernel)
        self.assertEqual(k.candidates.mode, "db_group")
        self.assertEqual(k.refine_op.predicate.name, "grouped_count")
        self.assertEqual(k.refine_op.predicate.options["group_keys"], ("region",))
        self.assertEqual(k.emit_op.fields, ("region", "count"))

    def test_sum_kernel_compiled_shape(self):
        k = rt.compile_kernel(sum_kernel)
        self.assertEqual(k.candidates.mode, "db_group")
        self.assertEqual(k.refine_op.predicate.name, "grouped_sum")
        self.assertEqual(k.refine_op.predicate.options["group_keys"], ("region",))
        self.assertEqual(k.refine_op.predicate.options["value_field"], "revenue")
        self.assertEqual(k.emit_op.fields, ("region", "sum"))

    def test_traverse_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            @rt.kernel(backend="rtdl", precision="float_approx")
            def bad():
                predicates = rt.input("predicates", rt.PredicateSet, role="probe")
                table = rt.input("table", rt.DenormTable, role="build")
                candidates = rt.traverse(predicates, table, accel="bvh", mode="db_bogus")
                matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
                return rt.emit(matches, fields=["row_id"])
            rt.compile_kernel(bad)

    def test_input_rejects_unknown_role(self):
        with self.assertRaises(ValueError):
            @rt.kernel(backend="rtdl", precision="float_approx")
            def bad():
                predicates = rt.input("predicates", rt.PredicateSet, role="lookup")
                table = rt.input("table", rt.DenormTable, role="build")
                candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
                matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
                return rt.emit(matches, fields=["row_id"])
            rt.compile_kernel(bad)

    def test_duplicate_input_name_rejected(self):
        with self.assertRaises(ValueError):
            @rt.kernel(backend="rtdl", precision="float_approx")
            def bad():
                predicates = rt.input("x", rt.PredicateSet, role="probe")
                table = rt.input("x", rt.DenormTable, role="build")
                candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
                matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
                return rt.emit(matches, fields=["row_id"])
            rt.compile_kernel(bad)

    def test_grouped_count_predicate_rejects_empty_group_keys(self):
        with self.assertRaises(ValueError):
            rt.grouped_count(group_keys=())

    def test_grouped_sum_predicate_rejects_empty_group_keys(self):
        with self.assertRaises(ValueError):
            rt.grouped_sum(group_keys=(), value_field="revenue")

    def test_grouped_sum_predicate_rejects_empty_value_field(self):
        with self.assertRaises(ValueError):
            rt.grouped_sum(group_keys=("region",), value_field="")


# ===========================================================================
# 2. Predicate normalization
# ===========================================================================

class TestPredicateNormalization(unittest.TestCase):
    def test_tuple3_normalizes(self):
        b = normalize_predicate_bundle((("ship_date", "eq", 10),))
        self.assertEqual(len(b.clauses), 1)
        self.assertEqual(b.clauses[0].field, "ship_date")
        self.assertEqual(b.clauses[0].op, "eq")
        self.assertEqual(b.clauses[0].value, 10)
        self.assertIsNone(b.clauses[0].value_hi)

    def test_tuple4_between_normalizes(self):
        b = normalize_predicate_bundle((("ship_date", "between", 5, 15),))
        c = b.clauses[0]
        self.assertEqual(c.op, "between")
        self.assertEqual(c.value, 5)
        self.assertEqual(c.value_hi, 15)

    def test_dict_form_normalizes(self):
        b = normalize_predicate_bundle({
            "clauses": ({"field": "discount", "op": "ge", "value": 6},)
        })
        self.assertEqual(b.clauses[0].field, "discount")
        self.assertEqual(b.clauses[0].op, "ge")

    def test_predicate_clause_passthrough(self):
        clause = PredicateClause(field="quantity", op="lt", value=20)
        b = normalize_predicate_bundle((clause,))
        self.assertIs(b.clauses[0], clause)

    def test_bundle_passthrough(self):
        original = normalize_predicate_bundle((("x", "eq", 1),))
        again = normalize_predicate_bundle(original)
        self.assertIs(again, original)

    def test_empty_bundle_allowed(self):
        b = normalize_predicate_bundle(())
        self.assertEqual(len(b.clauses), 0)

    def test_invalid_operator_rejected(self):
        with self.assertRaises(ValueError, msg="unsupported predicate operator"):
            normalize_predicate_bundle((("x", "!=", 5),))

    def test_between_without_value_hi_rejected(self):
        with self.assertRaises(ValueError):
            normalize_predicate_bundle(
                (PredicateBundle(clauses=(PredicateClause(field="x", op="between", value=1, value_hi=None),)),)
            )

    def test_invalid_clause_type_rejected(self):
        with self.assertRaises(ValueError):
            normalize_predicate_bundle((42,))

    def test_denorm_table_missing_row_id_rejected(self):
        with self.assertRaises(ValueError, msg="row_id"):
            normalize_denorm_table(({"ship_date": 10, "discount": 5},))

    def test_denorm_table_non_dict_row_rejected(self):
        with self.assertRaises(ValueError):
            normalize_denorm_table(((1, 2, 3),))

    def test_grouped_query_from_dict(self):
        q = normalize_grouped_query({
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        })
        self.assertEqual(q.group_keys, ("region",))
        self.assertEqual(q.value_field, "revenue")
        self.assertEqual(len(q.predicates), 1)

    def test_grouped_query_passthrough(self):
        q = GroupedAggregateQuery(
            predicates=(),
            group_keys=("region",),
            value_field=None,
        )
        self.assertIs(normalize_grouped_query(q), q)

    def test_grouped_query_non_mapping_rejected(self):
        with self.assertRaises(ValueError):
            normalize_grouped_query("bad")


# ===========================================================================
# 3. Conjunctive scan — all operators
# ===========================================================================

class TestConjunctiveScanOperators(unittest.TestCase):
    """One test per operator to confirm correct inclusive/exclusive semantics."""

    def test_eq(self):
        rows = _run_scan((("discount", "eq", 6),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_lt(self):
        # quantity < 12  => rows 4 (10), 5 (8), 6 (5)
        rows = _run_scan((("quantity", "lt", 12),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {4, 5, 6})

    def test_le(self):
        # quantity <= 12 => rows 1 (12), 4 (10), 5 (8), 6 (5)
        rows = _run_scan((("quantity", "le", 12),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {1, 4, 5, 6})

    def test_gt(self):
        # ship_date > 12 => rows 4, 5
        rows = _run_scan((("ship_date", "gt", 12),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {4, 5})

    def test_ge(self):
        # ship_date >= 12 => rows 3, 4, 5
        rows = _run_scan((("ship_date", "ge", 12),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_between_inclusive_both_ends(self):
        # ship_date BETWEEN 10 AND 11  => rows 1 (10), 2 (11)  — both ends inclusive
        rows = _run_scan((("ship_date", "between", 10, 11),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {1, 2})

    def test_between_boundary_hi_exact(self):
        # ship_date BETWEEN 13 AND 13 => rows 4, 5
        rows = _run_scan((("ship_date", "between", 13, 13),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {4, 5})

    def test_between_empty_range(self):
        # value_hi < value  => no rows (invalid range — value > value_hi is vacuously false)
        rows = _run_scan((("ship_date", "between", 15, 10),))
        self.assertEqual(rows, ())

    def test_le_boundary_exact(self):
        # discount <= 5 => row 1 (5), row 6 (3)
        rows = _run_scan((("discount", "le", 5),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {1, 6})

    def test_ge_boundary_exact(self):
        # discount >= 8 => row 2 (8)
        rows = _run_scan((("discount", "ge", 8),))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {2})


# ===========================================================================
# 4. Conjunctive scan — edge cases
# ===========================================================================

class TestConjunctiveScanEdgeCases(unittest.TestCase):
    def test_empty_table_returns_empty(self):
        rows = _run_scan((("discount", "eq", 6),), table=())
        self.assertEqual(rows, ())

    def test_zero_predicates_returns_all_rows(self):
        # No clauses → everything passes
        rows = _run_scan(())
        self.assertEqual(len(rows), len(SALES_TABLE))

    def test_no_matches(self):
        rows = _run_scan((("discount", "eq", 99),))
        self.assertEqual(rows, ())

    def test_all_rows_match(self):
        # ship_date >= 0 → all rows
        rows = _run_scan((("ship_date", "ge", 0),))
        self.assertEqual(len(rows), len(SALES_TABLE))

    def test_single_row_table_matches(self):
        table = ({"row_id": 7, "discount": 6, "quantity": 10},)
        rows = _run_scan((("discount", "eq", 6),), table=table)
        self.assertEqual(rows, ({"row_id": 7},))

    def test_single_row_table_no_match(self):
        table = ({"row_id": 7, "discount": 3, "quantity": 10},)
        rows = _run_scan((("discount", "eq", 6),), table=table)
        self.assertEqual(rows, ())

    def test_multi_predicate_intersection(self):
        # ship_date BETWEEN 11 AND 13 AND discount eq 6 AND quantity < 20
        rows = _run_scan((
            ("ship_date", "between", 11, 13),
            ("discount", "eq", 6),
            ("quantity", "lt", 20),
        ))
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_contradictory_predicates_yield_empty(self):
        # discount > 10 AND discount < 5 → impossible
        rows = _run_scan((
            ("discount", "gt", 10),
            ("discount", "lt", 5),
        ))
        self.assertEqual(rows, ())

    def test_emit_only_row_id_field(self):
        rows = _run_scan((("discount", "eq", 6),))
        for row in rows:
            self.assertEqual(set(row.keys()), {"row_id"})

    def test_row_missing_predicate_field_raises(self):
        table = ({"row_id": 1, "quantity": 10},)  # missing "discount"
        with self.assertRaises(ValueError):
            _run_scan((("discount", "eq", 6),), table=table)

    def test_dict_wrapped_table_rows_accepted(self):
        rows = rt.run_cpu_python_reference(
            scan_kernel,
            predicates=(("discount", "eq", 6),),
            table={"rows": SALES_TABLE},
        )
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_dict_clauses_predicate_form(self):
        rows = rt.run_cpu_python_reference(
            scan_kernel,
            predicates={"clauses": [{"field": "discount", "op": "eq", "value": 6}]},
            table=SALES_TABLE,
        )
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})


# ===========================================================================
# 5. Conjunctive scan — cpu vs cpu_python_reference agreement
# ===========================================================================

class TestConjunctiveScanCpuAgreement(unittest.TestCase):
    CASES = [
        (("discount", "eq", 6),),
        (("quantity", "lt", 15),),
        (("ship_date", "between", 11, 13), ("discount", "ge", 6)),
        (),
        (("discount", "eq", 99),),
    ]

    def test_cpu_matches_python_reference(self):
        for predicates in self.CASES:
            with self.subTest(predicates=predicates):
                ref = _run_scan(predicates)
                cpu = _run_scan_cpu(predicates)
                self.assertEqual(
                    sorted(r["row_id"] for r in ref),
                    sorted(r["row_id"] for r in cpu),
                    msg=f"mismatch for {predicates}",
                )


# ===========================================================================
# 6. Grouped count — correctness
# ===========================================================================

class TestGroupedCount(unittest.TestCase):
    def _query(self, predicates=(), group_keys=("region",)):
        return {"predicates": predicates, "group_keys": group_keys}

    def test_basic_group_by_region(self):
        rows = _run_count(self._query())
        by_region = {r["region"]: r["count"] for r in rows}
        self.assertEqual(by_region["east"], 2)
        self.assertEqual(by_region["west"], 3)
        self.assertEqual(by_region["north"], 1)

    def test_predicate_filters_before_grouping(self):
        # Rows with ship_date >= 11: row2 (west,11), row3 (east,12), row4 (west,13), row5 (west,13)
        rows = _run_count(self._query(predicates=(("ship_date", "ge", 11),)))
        by_region = {r["region"]: r["count"] for r in rows}
        self.assertEqual(by_region.get("east", 0), 1)
        self.assertEqual(by_region.get("west", 0), 3)
        self.assertNotIn("north", by_region)  # row6 has ship_date=9

    def test_predicate_no_matches_returns_empty(self):
        rows = _run_count(self._query(predicates=(("discount", "eq", 99),)))
        self.assertEqual(rows, ())

    def test_all_rows_one_group(self):
        table = tuple(
            {"row_id": i, "region": "x", "value": i} for i in range(1, 6)
        )
        rows = _run_count(self._query(), table=table)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["region"], "x")
        self.assertEqual(rows[0]["count"], 5)

    def test_all_rows_unique_groups(self):
        table = tuple(
            {"row_id": i, "region": str(i), "value": i} for i in range(1, 6)
        )
        rows = _run_count(self._query(), table=table)
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["count"] == 1 for r in rows))

    def test_empty_table_returns_empty(self):
        rows = _run_count(self._query(), table=())
        self.assertEqual(rows, ())

    def test_output_sorted_by_group_key(self):
        rows = _run_count(self._query())
        keys = [r["region"] for r in rows]
        self.assertEqual(keys, sorted(keys))

    def test_emit_fields_only_region_and_count(self):
        rows = _run_count(self._query())
        for row in rows:
            self.assertEqual(set(row.keys()), {"region", "count"})

    def test_count_is_always_int(self):
        rows = _run_count(self._query())
        for row in rows:
            self.assertIsInstance(row["count"], int)


# ===========================================================================
# 7. Grouped count — multi-key GROUP BY
# ===========================================================================

@rt.kernel(backend="rtdl", precision="float_approx")
def count_multikey_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_count(group_keys=("region", "discount")),
    )
    return rt.emit(groups, fields=["region", "discount", "count"])


class TestGroupedCountMultiKey(unittest.TestCase):
    def _run(self, predicates=()):
        return rt.run_cpu_python_reference(
            count_multikey_kernel,
            query={"predicates": predicates, "group_keys": ("region", "discount")},
            table=SALES_TABLE,
        )

    def test_multikey_groups_correct(self):
        rows = self._run()
        keys = {(r["region"], r["discount"]) for r in rows}
        self.assertIn(("east", 5), keys)
        self.assertIn(("east", 6), keys)
        self.assertIn(("west", 6), keys)
        self.assertIn(("west", 8), keys)
        self.assertIn(("north", 3), keys)

    def test_multikey_output_sorted(self):
        rows = self._run()
        pairs = [(r["region"], r["discount"]) for r in rows]
        self.assertEqual(pairs, sorted(pairs))

    def test_multikey_count_values(self):
        rows = self._run()
        by_key = {(r["region"], r["discount"]): r["count"] for r in rows}
        self.assertEqual(by_key[("west", 6)], 2)  # rows 4 and 5
        self.assertEqual(by_key[("east", 5)], 1)


# ===========================================================================
# 8. Grouped sum — correctness
# ===========================================================================

class TestGroupedSum(unittest.TestCase):
    def _query(self, predicates=(), group_keys=("region",), value_field="revenue"):
        return {"predicates": predicates, "group_keys": group_keys, "value_field": value_field}

    def test_basic_sum_by_region(self):
        rows = _run_sum(self._query())
        by_region = {r["region"]: r["sum"] for r in rows}
        self.assertEqual(by_region["east"], 11)    # 5 + 6
        self.assertEqual(by_region["west"], 20)    # 8 + 10 + 2
        self.assertEqual(by_region["north"], 1)

    def test_predicate_filters_before_summing(self):
        # ship_date >= 12 → east row3 (6), west rows 4 (10) + 5 (2)
        rows = _run_sum(self._query(predicates=(("ship_date", "ge", 12),)))
        by_region = {r["region"]: r["sum"] for r in rows}
        self.assertEqual(by_region.get("east", 0), 6)
        self.assertEqual(by_region.get("west", 0), 12)
        self.assertNotIn("north", by_region)

    def test_no_matches_returns_empty(self):
        rows = _run_sum(self._query(predicates=(("discount", "eq", 99),)))
        self.assertEqual(rows, ())

    def test_empty_table_returns_empty(self):
        rows = _run_sum(self._query(), table=())
        self.assertEqual(rows, ())

    def test_float_values_summed(self):
        rows = rt.run_cpu_python_reference(
            sum_kernel,
            query={"predicates": (), "group_keys": ("region",), "value_field": "value"},
            table=FLOAT_TABLE,
        )
        by_region = {r["region"]: r["sum"] for r in rows}
        self.assertAlmostEqual(by_region["a"], 4.0)   # 1.5 + 2.5
        self.assertAlmostEqual(by_region["b"], 2.0)   # 3.0 + (-1.0)

    def test_negative_values_summed(self):
        table = (
            {"row_id": 1, "region": "x", "revenue": -5},
            {"row_id": 2, "region": "x", "revenue": 3},
        )
        rows = _run_sum(self._query(), table=table)
        self.assertEqual(rows[0]["sum"], -2)

    def test_sum_zero_result(self):
        table = (
            {"row_id": 1, "region": "x", "revenue": 5},
            {"row_id": 2, "region": "x", "revenue": -5},
        )
        rows = _run_sum(self._query(), table=table)
        self.assertEqual(rows[0]["sum"], 0)

    def test_sum_returns_int_for_integral_result(self):
        rows = _run_sum(self._query())
        for row in rows:
            self.assertIsInstance(row["sum"], int, msg=f"expected int sum, got {row['sum']!r}")

    def test_sum_returns_float_for_fractional_result(self):
        table = (
            {"row_id": 1, "region": "x", "revenue": 1.5},
            {"row_id": 2, "region": "x", "revenue": 0.3},
        )
        rows = _run_sum(self._query(), table=table)
        self.assertIsInstance(rows[0]["sum"], float)

    def test_output_sorted_by_group_key(self):
        rows = _run_sum(self._query())
        keys = [r["region"] for r in rows]
        self.assertEqual(keys, sorted(keys))

    def test_emit_fields_only_region_and_sum(self):
        rows = _run_sum(self._query())
        for row in rows:
            self.assertEqual(set(row.keys()), {"region", "sum"})

    def test_missing_value_field_in_row_raises(self):
        table = ({"row_id": 1, "region": "x"},)  # no "revenue"
        with self.assertRaises(ValueError):
            _run_sum(self._query(), table=table)

    def test_missing_group_key_in_row_raises_value_error(self):
        table = ({"row_id": 1, "revenue": 5},)  # no "region"
        with self.assertRaises(ValueError):
            _run_sum(self._query(), table=table)


# ===========================================================================
# 9. grouped_count_cpu / grouped_sum_cpu direct unit tests
# ===========================================================================

class TestDbReferenceCpuDirect(unittest.TestCase):
    """Call the CPU reference functions directly — no kernel overhead."""

    def _table(self):
        return normalize_denorm_table(SALES_TABLE)

    def test_conjunctive_scan_all_ops(self):
        table = self._table()
        ops = [
            ((("discount", "eq", 6),), {3, 4, 5}),
            ((("quantity", "lt", 10),), {5, 6}),
            ((("quantity", "le", 10),), {4, 5, 6}),
            ((("ship_date", "gt", 12),), {4, 5}),
            ((("ship_date", "ge", 12),), {3, 4, 5}),
            ((("ship_date", "between", 10, 11),), {1, 2}),
        ]
        for predicates_raw, expected_ids in ops:
            bundle = normalize_predicate_bundle(predicates_raw)
            result = conjunctive_scan_cpu(table, bundle)
            ids = {r["row_id"] for r in result}
            self.assertEqual(ids, expected_ids, msg=f"op={predicates_raw}")

    def test_grouped_count_requires_group_keys(self):
        table = self._table()
        q = GroupedAggregateQuery(predicates=(), group_keys=(), value_field=None)
        with self.assertRaises(ValueError, msg="grouped_count requires"):
            grouped_count_cpu(table, q)

    def test_grouped_sum_requires_group_keys(self):
        table = self._table()
        q = GroupedAggregateQuery(predicates=(), group_keys=(), value_field="revenue")
        with self.assertRaises(ValueError):
            grouped_sum_cpu(table, q)

    def test_grouped_sum_requires_value_field(self):
        table = self._table()
        q = GroupedAggregateQuery(predicates=(), group_keys=("region",), value_field=None)
        with self.assertRaises(ValueError):
            grouped_sum_cpu(table, q)

    def test_grouped_count_missing_group_key_raises_value_error(self):
        q = GroupedAggregateQuery(predicates=(), group_keys=("region",), value_field=None)
        with self.assertRaises(ValueError):
            grouped_count_cpu(({"row_id": 1},), q)

    def test_grouped_sum_missing_value_field_in_row_raises_value_error(self):
        q = GroupedAggregateQuery(predicates=(), group_keys=("region",), value_field="revenue")
        with self.assertRaises(ValueError):
            grouped_sum_cpu(({"row_id": 1, "region": "x"},), q)


# ===========================================================================
# 10. SQL generation correctness
# ===========================================================================

class TestSqlGeneration(unittest.TestCase):
    def test_eq_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "eq", 1),))
        self.assertIn("x = %s", sql)

    def test_lt_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "lt", 1),))
        self.assertIn("x < %s", sql)

    def test_le_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "le", 1),))
        self.assertIn("x <= %s", sql)

    def test_gt_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "gt", 1),))
        self.assertIn("x > %s", sql)

    def test_ge_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "ge", 1),))
        self.assertIn("x >= %s", sql)

    def test_between_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "between", 1, 5),))
        self.assertIn("x BETWEEN %s AND %s", sql)

    def test_empty_predicates_uses_true(self):
        sql = build_postgresql_conjunctive_scan_sql(())
        self.assertIn("WHERE TRUE", sql)

    def test_multi_predicate_uses_and(self):
        sql = build_postgresql_conjunctive_scan_sql((
            ("x", "eq", 1),
            ("y", "lt", 5),
        ))
        self.assertIn("AND", sql)

    def test_scan_sql_selects_row_id(self):
        sql = build_postgresql_conjunctive_scan_sql((("x", "eq", 1),))
        self.assertIn("SELECT row_id", sql)
        self.assertIn("ORDER BY row_id", sql)

    def test_grouped_count_sql_structure(self):
        query = {"predicates": (("x", "ge", 1),), "group_keys": ("region",)}
        sql = build_postgresql_grouped_count_sql(query)
        self.assertIn("COUNT(*) AS count", sql)
        self.assertIn("GROUP BY region", sql)
        self.assertIn("ORDER BY region", sql)

    def test_grouped_sum_sql_structure(self):
        query = {"predicates": (), "group_keys": ("region",), "value_field": "revenue"}
        sql = build_postgresql_grouped_sum_sql(query)
        self.assertIn("SUM(revenue) AS sum", sql)
        self.assertIn("GROUP BY region", sql)

    def test_grouped_count_sql_no_predicates_uses_true(self):
        query = {"predicates": (), "group_keys": ("region",)}
        sql = build_postgresql_grouped_count_sql(query)
        self.assertIn("WHERE TRUE", sql)

    def test_grouped_count_sql_requires_group_keys(self):
        with self.assertRaises(ValueError):
            build_postgresql_grouped_count_sql({"predicates": (), "group_keys": ()})

    def test_grouped_sum_sql_requires_group_keys(self):
        with self.assertRaises(ValueError):
            build_postgresql_grouped_sum_sql({"predicates": (), "group_keys": (), "value_field": "revenue"})

    def test_grouped_sum_sql_requires_value_field(self):
        with self.assertRaises(ValueError):
            build_postgresql_grouped_sum_sql({"predicates": (), "group_keys": ("region",), "value_field": None})

    def test_custom_table_name_in_sql(self):
        sql = build_postgresql_conjunctive_scan_sql((), table_name="my_tbl")
        self.assertIn("my_tbl", sql)


# ===========================================================================
# 11. FakePostgresqlConnection roundtrip
# ===========================================================================

class TestFakePostgresqlRoundtrip(unittest.TestCase):
    def test_conjunctive_scan_roundtrip(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_conjunctive_scan(
            conn,
            SALES_TABLE,
            (("discount", "eq", 6),),
        )
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_conjunctive_scan_no_match(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_conjunctive_scan(
            conn,
            SALES_TABLE,
            (("discount", "eq", 99),),
        )
        self.assertEqual(rows, ())

    def test_conjunctive_scan_multi_predicate(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_conjunctive_scan(
            conn,
            SALES_TABLE,
            (("ship_date", "between", 11, 13), ("discount", "eq", 6)),
        )
        ids = {r["row_id"] for r in rows}
        self.assertEqual(ids, {3, 4, 5})

    def test_grouped_count_roundtrip(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_grouped_count(
            conn,
            SALES_TABLE,
            {"predicates": (), "group_keys": ("region",)},
        )
        by_region = {r["region"]: r["count"] for r in rows}
        self.assertEqual(by_region["east"], 2)
        self.assertEqual(by_region["west"], 3)
        self.assertEqual(by_region["north"], 1)

    def test_grouped_count_with_predicate(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_grouped_count(
            conn,
            SALES_TABLE,
            {"predicates": (("ship_date", "ge", 12),), "group_keys": ("region",)},
        )
        by_region = {r["region"]: r["count"] for r in rows}
        self.assertNotIn("north", by_region)
        self.assertEqual(by_region.get("west", 0), 2)

    def test_grouped_sum_roundtrip(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_grouped_sum(
            conn,
            SALES_TABLE,
            {"predicates": (), "group_keys": ("region",), "value_field": "revenue"},
        )
        by_region = {r["region"]: r["sum"] for r in rows}
        self.assertEqual(by_region["east"], 11)
        self.assertEqual(by_region["west"], 20)
        self.assertEqual(by_region["north"], 1)

    def test_grouped_sum_with_predicate(self):
        conn = FakePostgresqlConnection()
        rows = run_postgresql_grouped_sum(
            conn,
            SALES_TABLE,
            {"predicates": (("ship_date", "ge", 12),), "group_keys": ("region",), "value_field": "revenue"},
        )
        by_region = {r["region"]: r["sum"] for r in rows}
        self.assertEqual(by_region.get("east", 0), 6)
        self.assertEqual(by_region.get("west", 0), 12)

    def test_fake_connection_records_executed_sql(self):
        conn = FakePostgresqlConnection()
        run_postgresql_conjunctive_scan(conn, SALES_TABLE, (("discount", "eq", 6),))
        # Should have CREATE TABLE, INSERT, CREATE INDEX x2, ANALYZE, SELECT
        self.assertTrue(
            any("SELECT row_id" in sql for sql in conn.executed_sql),
            msg=f"executed_sql: {conn.executed_sql}",
        )

    def test_fake_connection_records_inserted_rows(self):
        conn = FakePostgresqlConnection()
        run_postgresql_conjunctive_scan(conn, SALES_TABLE, (("discount", "eq", 6),))
        self.assertEqual(len(conn.inserted_rows), len(SALES_TABLE))


# ===========================================================================
# 12. run_cpu agreement with cpu_python_reference for all three workloads
# ===========================================================================

class TestCpuAgreementAllWorkloads(unittest.TestCase):
    def test_scan_cpu_agrees_with_reference_multi_pred(self):
        predicates = (
            ("ship_date", "between", 10, 13),
            ("discount", "ge", 5),
            ("quantity", "lt", 30),
        )
        ref = rt.run_cpu_python_reference(scan_kernel, predicates=predicates, table=SALES_TABLE)
        cpu = rt.run_cpu(scan_kernel, predicates=predicates, table=SALES_TABLE)
        self.assertEqual(
            sorted(r["row_id"] for r in ref),
            sorted(r["row_id"] for r in cpu),
        )

    def test_count_cpu_agrees_with_reference(self):
        query = {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",)}
        ref = rt.run_cpu_python_reference(count_kernel, query=query, table=SALES_TABLE)
        cpu = rt.run_cpu(count_kernel, query=query, table=SALES_TABLE)
        ref_map = {r["region"]: r["count"] for r in ref}
        cpu_map = {r["region"]: r["count"] for r in cpu}
        self.assertEqual(ref_map, cpu_map)

    def test_sum_cpu_agrees_with_reference(self):
        query = {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",), "value_field": "revenue"}
        ref = rt.run_cpu_python_reference(sum_kernel, query=query, table=SALES_TABLE)
        cpu = rt.run_cpu(sum_kernel, query=query, table=SALES_TABLE)
        ref_map = {r["region"]: r["sum"] for r in ref}
        cpu_map = {r["region"]: r["sum"] for r in cpu}
        self.assertEqual(ref_map, cpu_map)


# ===========================================================================
# 13. run_cpu / run_cpu_python_reference error contract
# ===========================================================================

class TestRuntimeErrors(unittest.TestCase):
    def test_missing_input_raises(self):
        with self.assertRaises(ValueError, msg="missing"):
            rt.run_cpu_python_reference(scan_kernel, predicates=(("x", "eq", 1),))

    def test_unexpected_input_raises(self):
        with self.assertRaises(ValueError, msg="unexpected"):
            rt.run_cpu_python_reference(
                scan_kernel,
                predicates=(("x", "eq", 1),),
                table=SALES_TABLE,
                extra_garbage=(1, 2),
            )

    def test_non_float_approx_precision_rejected(self):
        @rt.kernel(backend="rtdl", precision="float_exact")
        def strict():
            predicates = rt.input("predicates", rt.PredicateSet, role="probe")
            table = rt.input("table", rt.DenormTable, role="build")
            candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
            matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
            return rt.emit(matches, fields=["row_id"])

        with self.assertRaises(ValueError):
            rt.run_cpu(strict, predicates=(("x", "eq", 1),), table=SALES_TABLE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
