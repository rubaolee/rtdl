from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import ast
from pathlib import Path
import sys
import unittest

from rtdsl.reference import Ray3D, Triangle3D, ray_triangle_closest_hit_cpu
from rtdsl.v4_builtin_triangle_standard_library import compile_adjacency_callback


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/goal5783-held-out-rtxrmq"
SELECTION = ROOT / "history/internal_docs/goal5783_postfreeze_held_out_selection_20260814.json"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Goal5783PostfreezeRTXRMQExamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load("goal5783_rtxrmq_app_test", APP / "v4_whole_app.py")
        cls.oracle = load("goal5783_rtxrmq_oracle_test", APP / "independent_oracle.py")

    def test_selection_is_post_goal5782_freeze_and_preclaims_nothing(self):
        row = json.loads(SELECTION.read_text(encoding="utf-8"))
        self.assertTrue(row["selection_happened_after_goal5782_freeze"])
        self.assertEqual(
            hashlib.sha256((ROOT / "history/internal_docs/goal5782_local_functional_candidate_v5_20260814.tar.gz").read_bytes()).hexdigest(),
            row["frozen_preselection_authority"]["goal5782_candidate_bundle_sha256"],
        )
        self.assertTrue(row["exam_contract"]["core_or_native_change_means_exam_failure"])
        self.assertFalse(row["claim_boundary"]["paper_app_status_claimed"])

    def test_independent_oracle_is_leftmost_and_fail_closed(self):
        self.assertEqual(
            self.oracle.range_minimum_indices(
                (4.0, 1.0, 7.0, 1.0, 2.0),
                ((0, 4), (2, 4), (3, 3))),
            (1, 3, 3),
        )
        with self.assertRaises(ValueError):
            self.oracle.range_minimum_indices((1.0,), ((0, 1),))

    def test_paper_geometry_matches_oracle_in_cpu_route(self):
        data = self.app.build_v4_input(
            values=(4.0, 1.0, 7.0, 1.0, 2.0),
            intervals=((0, 4), (2, 4), (3, 3), (0, 0), (1, 3)),
        )
        triangles = tuple(Triangle3D(
            triangle_id,
            *(data.vertices[a] + data.vertices[b] + data.vertices[c]),
        ) for triangle_id, (a, b, c) in enumerate(data.triangles))
        rays = tuple(Ray3D(
            ray_id, *(origin + direction + (tmax,)),
        ) for ray_id, (origin, direction, tmax) in enumerate(data.queries))
        rows = ray_triangle_closest_hit_cpu(rays, triangles)
        self.assertEqual(
            tuple(int(row["triangle_id"]) for row in rows),
            data.expected_indices,
        )
        self.assertEqual(data.expected_indices, (1, 3, 3, 0, 1))

    def test_mapping_rejects_nonfinite_and_oversized_domains(self):
        with self.assertRaises(ValueError):
            self.app.build_v4_input(values=(1.0, math.nan), intervals=((0, 1),))
        with self.assertRaises(ValueError):
            self.app.build_v4_input(values=(), intervals=())

    def test_frozen_restricted_callback_compiles_without_app_dispatch(self):
        callback = compile_adjacency_callback()
        self.assertEqual(
            {function.role.value for function in callback.program.functions},
            {"make_ray", "closest_hit", "miss", "finalize"},
        )
        source = (APP / "v4_whole_app.py").read_text(encoding="utf-8").lower()
        for forbidden in ("src/native", "optixlaunch", "culaunchkernel", "candidate_override"):
            self.assertNotIn(forbidden, source)

    def test_expected_output_is_never_fed_to_the_device_runtime(self):
        tree = ast.parse((APP / "v4_whole_app.py").read_text(encoding="utf-8"))
        checked = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = (
                node.func.id if isinstance(node.func, ast.Name)
                else node.func.attr if isinstance(node.func, ast.Attribute)
                else None
            )
            if name not in {"run_builtin_triangle_callback", "execute"}:
                continue
            keywords = {item.arg: item.value for item in node.keywords}
            if "expected_output" not in keywords:
                continue
            checked += 1
            value = keywords["expected_output"]
            self.assertIsInstance(value, ast.Constant)
            self.assertIsNone(value.value)
        self.assertEqual(checked, 2)


if __name__ == "__main__":
    unittest.main()
