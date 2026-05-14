from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_hausdorff_distance_app.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1975_exact_hausdorff_partner_reference_2026-05-14.md"


class Goal1975ExactHausdorffPartnerReferenceTest(unittest.TestCase):
    def test_partner_adapter_exposes_exact_directed_hausdorff_reference(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def point_rows_to_partner_columns", adapters)
        self.assertIn("def directed_hausdorff_2d_partner_columns", adapters)
        self.assertIn("generic_exact_directed_hausdorff_2d", adapters)
        self.assertIn("nearest_distance_sq", adapters)
        self.assertIn("torch.min", adapters)
        self.assertIn("cupy.min", adapters)
        self.assertIn("torch.max", adapters)
        self.assertIn("cupy.argmax", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("rt_core_speedup_claim_authorized", adapters)
        self.assertIn("from .partner_adapters import directed_hausdorff_2d_partner_columns", init_text)
        self.assertIn('"directed_hausdorff_2d_partner_columns"', init_text)

    def test_hausdorff_app_has_partner_exact_mode_without_rt_core_claim(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_exact"', text)
        self.assertIn("rt.point_rows_to_partner_columns", text)
        self.assertIn("rt.directed_hausdorff_2d_partner_columns", text)
        self.assertIn("generic_exact_directed_hausdorff_2d", text)
        self.assertIn('"rt_core_accelerated": False', text)
        self.assertIn("native engine is not app-customized", text)

    def test_cpu_reference_path_still_matches_oracle(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--copies",
                "1",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertTrue(payload["matches_oracle"])
        self.assertIsNotNone(payload["hausdorff_distance"])

    def test_report_and_preflight_record_goal1975(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("threshold-decision proxy", report)
        self.assertIn("exact directed Hausdorff definition", report)
        self.assertIn("OptiX or claim RT-core acceleration", report)
        self.assertIn("Pod CuPy timing is the next step", report)
        self.assertIn("tests.goal1975_exact_hausdorff_partner_reference_test", preflight)


if __name__ == "__main__":
    unittest.main()
