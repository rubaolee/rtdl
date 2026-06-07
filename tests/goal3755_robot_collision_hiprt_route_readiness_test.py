from __future__ import annotations

import argparse
import ast
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "apps" / "robotics" / "rtdl_robot_collision_screening_app.py"
REPORT = ROOT / "docs" / "reports" / "goal3755_robot_collision_hiprt_route_readiness_2026-06-07.md"


class _BackendCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.run_hiprt_calls = 0
        self.backend_choices: tuple[str, ...] | None = None

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "run_hiprt":
            self.run_hiprt_calls += 1
        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
            first_arg = node.args[0] if node.args else None
            if isinstance(first_arg, ast.Constant) and first_arg.value == "--backend":
                for keyword in node.keywords:
                    if keyword.arg == "choices" and isinstance(keyword.value, ast.Tuple):
                        values: list[str] = []
                        for element in keyword.value.elts:
                            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                                values.append(element.value)
                        self.backend_choices = tuple(values)
        self.generic_visit(node)


class Goal3755RobotCollisionHiprtRouteReadinessTest(unittest.TestCase):
    def test_app_exposes_hiprt_backend_choice_and_dispatch(self) -> None:
        tree = ast.parse(APP.read_text(encoding="utf-8"))
        visitor = _BackendCallVisitor()
        visitor.visit(tree)
        self.assertIn("hiprt", visitor.backend_choices or ())
        self.assertEqual(visitor.run_hiprt_calls, 1)

    def test_machine_readable_app_matrix_exposes_hiprt_without_claiming_performance(self) -> None:
        support = rt.app_engine_support("robot_collision_screening", "hiprt")
        self.assertEqual(support.status, "direct_cli_native")
        self.assertIn("AMD functional validation", support.note)
        self.assertIn("not AMD performance evidence", support.note)

    def test_public_matrix_doc_matches_machine_readable_hiprt_row(self) -> None:
        text = (ROOT / "docs" / "app_engine_support_matrix.md").read_text(encoding="utf-8")
        expected = (
            "| `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | "
            "`portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | "
            "`not_exposed_by_app_cli` | `direct_cli_native` | `not_exposed_by_app_cli` |"
        )
        self.assertIn(expected, text)

    def test_prepared_summary_modes_stay_optix_only(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("robot_app_goal3755", APP)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        with self.assertRaisesRegex(ValueError, "prepared.*requires backend='optix'"):
            module.run_app("hiprt", optix_summary_mode="prepared_count")

    def test_report_documents_no_amd_runtime_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not provide AMD performance evidence", text)
        self.assertIn("no HIPRT SDK/runtime install", text)
        self.assertIn("--backend hiprt", text)
        self.assertIn("Prepared OptiX summary modes remain OptiX-only", text)


if __name__ == "__main__":
    unittest.main()
