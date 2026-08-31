from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from experiments.goal5802_premeasurement import pyoptix_scalar_arm as arm
from experiments.goal5802_premeasurement import workload
from experiments import goal5809_pyoptix_bulk_input as bulk
from scripts import goal5809_pyoptix_two_app_pilot as pilot


BOX_DTYPE = np.dtype([
    ("lower_x", "f4"), ("lower_y", "f4"), ("lower_z", "f4"),
    ("upper_x", "f4"), ("upper_y", "f4"), ("upper_z", "f4"),
    ("item_id", "u4"),
], align=True)
ROW_DTYPE = np.dtype([
    ("source_id", "u4"), ("item_id", "u4"),
], align=True)
RAY_DTYPE = np.dtype([
    ("origin_x", "f4"), ("origin_y", "f4"), ("origin_z", "f4"),
    ("direction_x", "f4"), ("direction_y", "f4"),
    ("direction_z", "f4"),
], align=True)
PARAM_DTYPE = np.dtype({
    "names": [
        "traversable", "boxes", "queries", "rows", "row_count",
        "overflow", "box_count", "query_count", "raw_row_capacity",
        "reverse_orientation", "minimum_overlap", "tmin", "tmax",
        "reserved0", "rays", "weights", "per_ray", "weighted_sum",
        "status",
    ],
    "formats": [
        "u8", "u8", "u8", "u8", "u8", "u8", "u4", "u4", "u4",
        "u4", "f4", "f4", "f4", "u4", "u8", "u8", "u8", "u8",
        "u8",
    ],
    "align": True,
})


def _legacy_boxes(rows: list[list[object]]) -> np.ndarray:
    result = np.zeros(len(rows), dtype=BOX_DTYPE)
    for index, row in enumerate(rows):
        result[index] = (
            np.float32(row[0]), np.float32(row[1]), np.float32(0.0),
            np.float32(row[2]), np.float32(row[3]), np.float32(0.0),
            np.uint32(row[4]),
        )
    return result


def _legacy_rays(rows: list[list[object]]) -> np.ndarray:
    result = np.zeros(len(rows), dtype=RAY_DTYPE)
    for index, (origin, direction, _maximum) in enumerate(rows):
        result[index] = tuple(
            np.float32(value) for value in (*origin, *direction))
    return result


class _CpuArrays:
    uint32 = np.uint32
    uint64 = np.uint64

    @staticmethod
    def zeros(shape: object, *, dtype: object) -> np.ndarray:
        return np.zeros(shape, dtype=dtype)

    @staticmethod
    def empty(shape: object, *, dtype: object) -> np.ndarray:
        return np.empty(shape, dtype=dtype)


class _Launcher:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.stream = object()

    @staticmethod
    def pinned_array(shape: object, dtype: object) -> np.ndarray:
        return np.zeros(shape, dtype=dtype)

    def close(self) -> None:
        return None


class _ConstructorBaseline:
    np = np
    cp = _CpuArrays()
    BOX_DTYPE = BOX_DTYPE
    ROW_DTYPE = ROW_DTYPE
    RAY_DTYPE = RAY_DTYPE
    PARAM_DTYPE = PARAM_DTYPE

    def __init__(self, *, allow_legacy_boxes: bool = False) -> None:
        self.boxes_array = mock.Mock(
            side_effect=(
                _legacy_boxes if allow_legacy_boxes else
                AssertionError("legacy boxes_array was called")))

    @staticmethod
    def new_operation_counts() -> dict[str, int]:
        return {
            "prepare_device_allocation_call_count": 0,
            "prepare_h2d_call_count": 0,
            "prepare_pinned_host_allocation_call_count": 0,
            "prepare_stream_creation_count": 0,
        }

    @staticmethod
    def to_device(value: np.ndarray, **_kwargs: object) -> np.ndarray:
        return value

    @staticmethod
    def build_custom_gas(
        _context: object, _boxes: np.ndarray, **_kwargs: object,
    ) -> tuple[int, object]:
        return 17, object()

    @staticmethod
    def build_triangle_gas(
        _context: object, _vertices: np.ndarray, **_kwargs: object,
    ) -> tuple[int, object]:
        return 19, object()


class Goal5809PyOptixBulkInputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = SimpleNamespace(
            np=np, BOX_DTYPE=BOX_DTYPE, RAY_DTYPE=RAY_DTYPE)
        cls.relation = workload.relation_workload()
        cls.triangle = workload.triangle_workload()

    def test_full_matched_arrays_are_byte_identical_to_goal5802_semantics(
            self) -> None:
        relation = bulk.pack_relation_host_inputs(
            self.baseline, self.relation)
        triangle = bulk.pack_triangle_host_inputs(
            self.baseline, self.triangle)

        self.assertEqual(
            relation.indexed.tobytes(),
            _legacy_boxes(self.relation["indexed"]).tobytes())
        self.assertEqual(
            relation.sources.tobytes(),
            _legacy_boxes(self.relation["sources"]).tobytes())
        self.assertEqual(
            triangle.vertices.tobytes(),
            np.asarray(
                self.triangle["vertices"], dtype=np.float32).tobytes())
        self.assertEqual(
            triangle.rays.tobytes(),
            _legacy_rays(self.triangle["queries"]).tobytes())
        self.assertEqual(
            triangle.weights.tobytes(),
            np.asarray(
                self.triangle["weights"], dtype=np.uint64).tobytes())
        self.assertEqual(triangle.maximum.tobytes(), np.float32(2.0).tobytes())
        self.assertEqual(relation.indexed.shape, (4096,))
        self.assertEqual(triangle.rays.shape, (16384,))
        self.assertEqual(relation.indexed.dtype, BOX_DTYPE)
        self.assertEqual(triangle.rays.dtype, RAY_DTYPE)
        self.assertEqual(triangle.weights.dtype, np.dtype(np.uint64))
        for value in (
                relation.indexed, relation.sources, triangle.vertices,
                triangle.rays, triangle.weights):
            self.assertTrue(value.flags.c_contiguous)
            self.assertFalse(value.flags.writeable)

    def test_real_owner_bulk_branches_never_call_legacy_row_packer(self) \
            -> None:
        baseline = _ConstructorBaseline()
        relation_inputs = bulk.pack_relation_host_inputs(
            baseline, self.relation)
        triangle_inputs = bulk.pack_triangle_host_inputs(
            baseline, self.triangle)
        relation_fixture = {
            "minimum_overlap": self.relation["minimum_overlap_f32"],
            "capacity": self.relation["semantic_capacity"],
            "expected_rows": self.relation["expected_rows"],
        }
        triangle_task = {
            "expected_reduced_u64": self.triangle["expected_reduced_u64"],
            "tmin": 0.0,
        }
        with mock.patch.object(
                arm, "_ComparativePreparedLaunch", _Launcher):
            relation_owner = arm.DeferredRelationPrepared(
                baseline, object(), object(), object(), relation_fixture,
                pipeline_keepalive=object(), sbt_keepalive=object(),
                compaction_kernel=object(), host_inputs=relation_inputs)
            triangle_owner = arm.ScalarTrianglePrepared(
                baseline, object(), object(), object(), triangle_task,
                pipeline_keepalive=object(), sbt_keepalive=object(),
                host_inputs=triangle_inputs)
        self.assertIs(relation_owner.indexed, relation_inputs.indexed)
        self.assertIs(relation_owner.sources, relation_inputs.sources)
        self.assertIs(triangle_owner.rays, triangle_inputs.rays)
        self.assertEqual(triangle_owner.d_per_ray.shape, (16384,))
        baseline.boxes_array.assert_not_called()

    def test_goal5802_default_constructor_paths_remain_available(self) -> None:
        baseline = _ConstructorBaseline(allow_legacy_boxes=True)
        relation_fixture = {
            "indexed": [[0.0, 0.0, 1.0, 1.0, 7]],
            "sources": [[0.0, 0.0, 1.0, 1.0, 7]],
            "minimum_overlap": 1.0,
            "capacity": 1,
            "expected_rows": [[7, 7]],
        }
        triangle_task = {
            "vertices": [
                [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0],
                [0.0, 1.0, 1.0],
            ],
            "queries": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 2.0]],
            "weights": [5],
            "expected_reduced_u64": 5,
            "tmin": 0.0,
        }
        with mock.patch.object(
                arm, "_ComparativePreparedLaunch", _Launcher):
            relation_owner = arm.DeferredRelationPrepared(
                baseline, object(), object(), object(), relation_fixture,
                pipeline_keepalive=object(), sbt_keepalive=object(),
                compaction_kernel=object())
            triangle_owner = arm.ScalarTrianglePrepared(
                baseline, object(), object(), object(), triangle_task,
                pipeline_keepalive=object(), sbt_keepalive=object())
        self.assertIsNone(relation_owner.goal5809_bulk_input_receipt)
        self.assertIsNone(triangle_owner.goal5809_bulk_input_receipt)
        self.assertEqual(baseline.boxes_array.call_count, 2)
        self.assertEqual(triangle_owner.rays.shape, (1,))

    def test_bulk_admission_fails_closed(self) -> None:
        cases = []
        bad_relation = dict(self.relation)
        bad_relation["indexed"] = [[0.0, 0.0, 1.0]]
        cases.append(lambda: bulk.pack_relation_host_inputs(
            self.baseline, bad_relation))
        bad_relation = dict(self.relation)
        bad_relation["sources"] = [[0.0, 0.0, float("nan"), 1.0, 0]]
        cases.append(lambda: bulk.pack_relation_host_inputs(
            self.baseline, bad_relation))
        bad_relation = dict(self.relation)
        bad_relation["sources"] = [[0.0, 0.0, 1.0, 1.0, 1 << 32]]
        cases.append(lambda: bulk.pack_relation_host_inputs(
            self.baseline, bad_relation))
        bad_triangle = dict(self.triangle)
        bad_triangle["queries"] = [
            [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 1.0],
            [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], 2.0],
        ]
        bad_triangle["weights"] = [1, 1]
        cases.append(lambda: bulk.pack_triangle_host_inputs(
            self.baseline, bad_triangle))
        bad_triangle = dict(self.triangle)
        bad_triangle["weights"] = [-1] * len(self.triangle["queries"])
        cases.append(lambda: bulk.pack_triangle_host_inputs(
            self.baseline, bad_triangle))
        for case in cases:
            with self.subTest(case=case), self.assertRaises(
                    (ValueError, RuntimeError)):
                case()

        relation = bulk.pack_relation_host_inputs(
            self.baseline, self.relation)
        relation.indexed.setflags(write=True)
        with self.assertRaisesRegex(RuntimeError, "bulk host ABI is invalid"):
            relation.checked_arrays(self.baseline)

    def test_worker_imports_bulk_helper_only_in_timed_runtime_preload(self) \
            -> None:
        source = Path(pilot.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        top_imports = [
            node for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and "goal5809_pyoptix_bulk_input" in ast.unparse(node)
        ]
        self.assertEqual(top_imports, [])
        preload = next(
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_preload_runtime")
        self.assertIn(
            "experiments.goal5809_pyoptix_bulk_input", ast.unparse(preload))

    def test_helper_has_no_size_dependent_python_assignment_loop(self) -> None:
        tree = ast.parse(Path(bulk.__file__).read_text(encoding="utf-8"))
        forbidden = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.ListComp, ast.SetComp,
                                 ast.DictComp, ast.GeneratorExp)):
                text = ast.unparse(node)
                if "enumerate(queries)" in text \
                        or "enumerate(rows)" in text \
                        or "for row in" in text:
                    forbidden.append(text)
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
