from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from rtdsl import aggregate_hierarchy_native as native
from rtdsl import v4_hierarchy_frontier as hierarchy


def _compiled(count: int = 2):
    return SimpleNamespace(
        point_count=count,
        plan_sha256="a" * 64,
        schema=SimpleNamespace(maximum_visits_per_source=9),
    )


def _row(index: int):
    return {
        "source_id": index,
        "reducer_value_0": float(index + 1),
        "reducer_value_1": 0.0,
        "reducer_value_2": 0.0,
        "visited_node_count": 2,
        "aggregate_contribution_count": 1,
        "exact_contribution_count": 1,
        "status_code": 0,
    }


def _bound_endpoint(*rows):
    frozen = tuple(native._FrozenHierarchyRow(dict(row)) for row in rows)
    values = np.asarray([row["reducer_value_0"] for row in rows], dtype=np.float64)
    visited = np.asarray([row["visited_node_count"] for row in rows], dtype=np.int64)
    aggregate = np.asarray(
        [row["aggregate_contribution_count"] for row in rows], dtype=np.int64)
    exact = np.asarray(
        [row["exact_contribution_count"] for row in rows], dtype=np.int64)
    status = np.asarray([row["status_code"] for row in rows], dtype=np.int64)
    digest = native._validate_and_hash_canonical_hierarchy_columns(
        reducer_value_0=values,
        visited=visited,
        aggregate=aggregate,
        exact=exact,
        status_codes=status,
        maximum_visits_per_source=9,
    )
    endpoint = {
        "rows": frozen,
        "row_count": len(frozen),
        "partial_result_returned": False,
        "selected_backend": "optix_traversal",
        "selected_template": hierarchy.AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
        "metadata": {
            "physical_executor_kind":
                "true_optix_triangle_traversal_with_exact_f64_opening",
        },
    }
    binding = native._CanonicalHierarchyOutputBinding(
        rows=frozen,
        rows_identity=id(frozen),
        output_sha256=digest,
        point_count=len(frozen),
        selected_backend=str(endpoint["selected_backend"]),
        selected_template=str(endpoint["selected_template"]),
        physical_executor_kind=str(endpoint["metadata"]["physical_executor_kind"]),
        authority_seal="",
    )
    binding.authority_seal = native._seal_canonical_hierarchy_output(binding)
    endpoint["_canonical_output_binding"] = binding
    return endpoint


def _bound_columns_endpoint(*rows):
    values = np.asarray([row["reducer_value_0"] for row in rows], dtype=np.float64)
    visited = np.asarray([row["visited_node_count"] for row in rows], dtype=np.int64)
    aggregate = np.asarray(
        [row["aggregate_contribution_count"] for row in rows], dtype=np.int64)
    exact = np.asarray(
        [row["exact_contribution_count"] for row in rows], dtype=np.int64)
    status = np.asarray([row["status_code"] for row in rows], dtype=np.int64)
    digest = native._validate_and_hash_canonical_hierarchy_columns(
        reducer_value_0=values,
        visited=visited,
        aggregate=aggregate,
        exact=exact,
        status_codes=status,
        maximum_visits_per_source=9,
    )
    columns = native._freeze_canonical_hierarchy_columns(
        reducer_value_0=values,
        visited=visited,
        aggregate=aggregate,
        exact=exact,
        status_codes=status,
    )
    endpoint = {
        "columns": columns,
        "row_count": len(rows),
        "partial_result_returned": False,
        "selected_backend": "optix_traversal",
        "selected_template": hierarchy.AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
        "metadata": {
            "physical_executor_kind":
                "true_optix_triangle_traversal_with_exact_f64_opening",
        },
    }
    binding = native._CanonicalHierarchyColumnsOutputBinding(
        columns=columns,
        columns_identity=id(columns),
        column_identities=columns.identities(),
        column_descriptors=native._canonical_hierarchy_columns_descriptors(
            columns
        ),
        output_sha256=digest,
        point_count=len(rows),
        selected_backend=str(endpoint["selected_backend"]),
        selected_template=str(endpoint["selected_template"]),
        physical_executor_kind=str(endpoint["metadata"]["physical_executor_kind"]),
        authority_seal="",
    )
    binding.authority_seal = native._seal_canonical_hierarchy_columns_output(
        binding)
    endpoint["_canonical_columns_output_binding"] = binding
    return endpoint


class Goal5782CanonicalPackedHierarchyBindingTest(unittest.TestCase):
    def test_same_semantic_rows_have_stable_binding_without_json(self):
        endpoint = _bound_endpoint(_row(0), _row(1))
        with mock.patch.object(
            hierarchy, "_digest",
            side_effect=AssertionError("row binding must not use JSON"),
        ):
            first = hierarchy._bind_canonical_packed_hierarchy_endpoint(
                _compiled(), endpoint)
            second = hierarchy._bind_canonical_packed_hierarchy_endpoint(
                _compiled(), _bound_endpoint(_row(0), _row(1)))
        self.assertEqual(first.output_sha256, second.output_sha256)
        self.assertEqual(64, len(first.output_sha256))
        with self.assertRaises(TypeError):
            first.rows[0]["source_id"] = 9

    def test_any_semantic_value_change_changes_binding(self):
        baseline = hierarchy._bind_canonical_packed_hierarchy_endpoint(
            _compiled(), _bound_endpoint(_row(0), _row(1)))
        changed = _row(1)
        changed["reducer_value_0"] = 3.0
        successor = hierarchy._bind_canonical_packed_hierarchy_endpoint(
            _compiled(), _bound_endpoint(_row(0), changed))
        self.assertNotEqual(baseline.output_sha256, successor.output_sha256)

    def test_malformed_columns_fail_closed_before_authority_issue(self):
        valid_float = np.asarray([1.0, 2.0], dtype=np.float64)
        valid_i64 = np.asarray([1, 1], dtype=np.int64)
        attacks = [
            {"reducer_value_0": np.asarray([float("nan"), 2.0])},
            {"visited": np.asarray([10, 1], dtype=np.int64)},
            {"aggregate": np.asarray([-1, 1], dtype=np.int64)},
            {"exact": np.asarray([-1, 1], dtype=np.int64)},
            {"status_codes": np.asarray([7, 0], dtype=np.int64)},
            {"visited": np.asarray([1], dtype=np.int64)},
        ]
        for attack in attacks:
            kwargs = {
                "reducer_value_0": valid_float,
                "visited": valid_i64,
                "aggregate": valid_i64,
                "exact": valid_i64,
                "status_codes": np.zeros(2, dtype=np.int64),
                "maximum_visits_per_source": 9,
                **attack,
            }
            with self.subTest(attack=attack), self.assertRaises(RuntimeError):
                native._validate_and_hash_canonical_hierarchy_columns(**kwargs)

    def test_omission_replacement_partial_and_replay_fail_closed(self):
        endpoint = _bound_endpoint(_row(0), _row(1))
        hierarchy._bind_canonical_packed_hierarchy_endpoint(_compiled(), endpoint)
        with self.assertRaisesRegex(hierarchy.HierarchyFrontierError, "replayed"):
            hierarchy._bind_canonical_packed_hierarchy_endpoint(_compiled(), endpoint)
        for mutate in (
            lambda value: value.pop("_canonical_output_binding"),
            lambda value: value.__setitem__("rows", tuple(reversed(value["rows"]))),
            lambda value: value.__setitem__("partial_result_returned", True),
        ):
            attacked = _bound_endpoint(_row(0), _row(1))
            mutate(attacked)
            with self.assertRaises(hierarchy.HierarchyFrontierError):
                hierarchy._bind_canonical_packed_hierarchy_endpoint(
                    _compiled(), attacked)

    def test_endpoint_mutation_or_forged_seal_cannot_be_accepted(self):
        compiled = _compiled()
        endpoint = _bound_endpoint(_row(0), _row(1))
        binding = hierarchy._bind_canonical_packed_hierarchy_endpoint(
            compiled, endpoint)
        receipt = {"receipt_sha256": "test"}
        endpoint["selected_backend"] = "cuda"
        with mock.patch.object(hierarchy, "_verify_receipt"), \
                self.assertRaisesRegex(
                    hierarchy.HierarchyFrontierError, "packed_binding"):
            hierarchy._accept_hierarchy_endpoint(
                compiled, endpoint, receipt, binding=binding)
        endpoint["selected_backend"] = "optix_traversal"
        forged = replace(binding, authority_seal="0" * 64)
        with mock.patch.object(hierarchy, "_verify_receipt"), \
                self.assertRaisesRegex(
                    hierarchy.HierarchyFrontierError, "packed_binding"):
            hierarchy._accept_hierarchy_endpoint(
                compiled, endpoint, receipt, binding=forged)

    def test_typed_columns_match_row_digest_and_are_genuinely_immutable(self):
        rows = (_row(0), _row(1))
        row_binding = hierarchy._bind_canonical_packed_hierarchy_endpoint(
            _compiled(), _bound_endpoint(*rows))
        endpoint = _bound_columns_endpoint(*rows)
        column_binding = hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
            _compiled(), endpoint)
        self.assertEqual(row_binding.output_sha256, column_binding.output_sha256)
        self.assertNotIn("rows", endpoint)
        self.assertFalse(column_binding.columns.reducer_value_0.flags.writeable)
        with self.assertRaises(ValueError):
            column_binding.columns.reducer_value_0[0] = 7.0
        with self.assertRaises(ValueError):
            column_binding.columns.reducer_value_0.setflags(write=True)

    def test_typed_columns_accept_full_contract_without_row_materialization(self):
        compiled = _compiled()
        endpoint = _bound_columns_endpoint(_row(0), _row(1))
        binding = hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
            compiled, endpoint)
        receipt = {"receipt_sha256": "test-only"}
        with mock.patch.object(hierarchy, "_verify_receipt") as verify:
            result = hierarchy._accept_hierarchy_columns_endpoint(
                compiled, endpoint, receipt, binding=binding)
        verify.assert_called_once_with(receipt, binding.output_sha256)
        self.assertEqual(result.point_count, 2)
        self.assertEqual(tuple(result.reducer_value_0), (1.0, 2.0))
        self.assertEqual(tuple(result.status_code), (0, 0))

    def test_typed_column_metadata_is_immutable_at_all_contract_boundaries(self):
        compiled = _compiled()

        endpoint = _bound_columns_endpoint(_row(0), _row(1))
        provider_columns = endpoint["columns"]
        for field, name, value in (
            ("reducer_value_0", "dtype", np.dtype("<u8")),
            ("reducer_value_0", "strides", (0,)),
            ("status_code", "shape", (1, 2)),
        ):
            with self.subTest(
                    stage="before_provider_consume", field=field, name=name), \
                    self.assertRaises((AttributeError, TypeError)):
                setattr(getattr(provider_columns, field), name, value)

        binding = hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
            compiled, endpoint)
        bound_columns = binding.columns
        for field, name, value in (
            ("reducer_value_0", "dtype", np.dtype("<u8")),
            ("reducer_value_0", "strides", (0,)),
            ("status_code", "shape", (1, 2)),
        ):
            with self.subTest(
                    stage="after_frontier_bind", field=field, name=name), \
                    self.assertRaises((AttributeError, TypeError)):
                setattr(getattr(bound_columns, field), name, value)

        with mock.patch.object(hierarchy, "_verify_receipt"):
            result = hierarchy._accept_hierarchy_columns_endpoint(
                compiled, endpoint, {}, binding=binding)
        public_column = result.reducer_value_0
        detached = np.asarray(public_column)
        detached.dtype = np.dtype("<u8")
        self.assertEqual(
            detached.tolist(),
            [4607182418800017408, 4611686018427387904],
        )
        self.assertEqual(np.asarray(public_column).tolist(), [1.0, 2.0])
        self.assertEqual(result.output_sha256, binding.output_sha256)
        for field, name, value in (
            ("reducer_value_0", "dtype", np.dtype("<u8")),
            ("reducer_value_0", "strides", (0,)),
            ("status_code", "shape", (1, 2)),
        ):
            with self.subTest(
                    stage="after_public_result", field=field, name=name), \
                    self.assertRaises((AttributeError, TypeError)):
                setattr(getattr(result, field), name, value)

    def test_forced_typed_column_internal_metadata_drift_fails_closed(self):
        endpoint = _bound_columns_endpoint(_row(0), _row(1))
        column = endpoint["columns"].reducer_value_0
        with self.assertRaises(AttributeError):
            object.__setattr__(column, "_dtype_string", "<u8")
        replacement = native._ImmutableHierarchyColumn(bytes(16), "<i8", 2)
        object.__setattr__(
            endpoint["columns"], "reducer_value_0", replacement,
        )
        with self.assertRaisesRegex(
            hierarchy.HierarchyFrontierError, "packed_columns_binding",
        ):
            hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
                _compiled(), endpoint)

        endpoint = _bound_columns_endpoint(_row(0), _row(1))
        binding = hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
            _compiled(), endpoint)
        replacement = native._ImmutableHierarchyColumn(bytes(16), "<i8", 2)
        object.__setattr__(binding.columns, "status_code", replacement)
        with mock.patch.object(hierarchy, "_verify_receipt"), \
                self.assertRaisesRegex(
                    hierarchy.HierarchyFrontierError, "packed_columns_binding",
                ):
            hierarchy._accept_hierarchy_columns_endpoint(
                _compiled(), endpoint, {}, binding=binding)

    def test_typed_columns_replay_and_endpoint_replacement_fail_closed(self):
        endpoint = _bound_columns_endpoint(_row(0), _row(1))
        hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
            _compiled(), endpoint)
        with self.assertRaisesRegex(
            hierarchy.HierarchyFrontierError, "replayed",
        ):
            hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
                _compiled(), endpoint)
        attacked = _bound_columns_endpoint(_row(0), _row(1))
        attacked["columns"] = _bound_columns_endpoint(
            _row(0), _row(1))["columns"]
        with self.assertRaises(hierarchy.HierarchyFrontierError):
            hierarchy._bind_canonical_packed_hierarchy_columns_endpoint(
                _compiled(), attacked)


if __name__ == "__main__":
    unittest.main()
