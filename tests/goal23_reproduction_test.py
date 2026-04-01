import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl.goal23_reproduction import generate_goal23_artifacts
from rtdsl.goal23_reproduction import run_goal23_reproduction


class Goal23ReproductionTest(unittest.TestCase):
    def test_goal23_small_config_generates_payload(self) -> None:
        payload = run_goal23_reproduction(
            config={
                "figure13_build_polygons": 80,
                "figure13_probe_series": (80, 120),
                "figure14_build_polygons": 80,
                "figure14_probe_series": (8, 12),
                "scalability_iterations": 1,
                "scalability_warmup": 0,
                "table_iterations": 1,
                "table_warmup": 0,
            }
        )
        self.assertEqual(payload["suite"], "goal23_bounded_embree_reproduction")
        self.assertTrue(payload["table3_rows"])
        self.assertTrue(payload["table4_rows"])
        self.assertIn("records", payload["figure13"])
        self.assertIn("records", payload["figure14"])

    def test_goal23_artifact_generator_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = generate_goal23_artifacts(
                output_dir=tmpdir,
                publish_docs=False,
                config={
                    "figure13_build_polygons": 80,
                    "figure13_probe_series": (80, 120),
                    "figure14_build_polygons": 80,
                    "figure14_probe_series": (8, 12),
                    "scalability_iterations": 1,
                    "scalability_warmup": 0,
                    "table_iterations": 1,
                    "table_warmup": 0,
                },
            )
            self.assertEqual(
                set(artifacts.keys()),
                {
                    "json",
                    "table3",
                    "table4",
                    "figure13_svg",
                    "figure14_svg",
                    "figure15_svg",
                    "report_markdown",
                    "report_pdf",
                },
            )
            report_text = Path(artifacts["report_markdown"]).read_text(encoding="utf-8")
            self.assertIn("bounded-local executable slice only", report_text)
            self.assertIn("Missing / Unexecuted Families", report_text)
            self.assertIn("## Abstract", report_text)
            self.assertIn("## 3. Architecture", report_text)
            self.assertIn("Figure 13 bounded LSI analogue", report_text)


if __name__ == "__main__":
    unittest.main()
