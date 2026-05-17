import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2252_rayjoin_same_query_current_comparison_2026-05-17.md"
LSI = ROOT / "docs" / "reports" / "goal2252_rayjoin_lsi_current_same_query_pod_2026-05-17.json"
PIP = ROOT / "docs" / "reports" / "goal2252_rayjoin_pip_current_same_query_pod_2026-05-17.json"


class Goal2252RayjoinSameQueryCurrentComparisonTest(unittest.TestCase):
    def _artifact(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_lsi_current_artifact(self) -> None:
        data = self._artifact(LSI)
        optix = data["backends"]["optix"]

        self.assertEqual(data["commit"], "949ca4f60a19b61bade10682d17a645bc07ec588")
        self.assertEqual(data["workload"], "lsi")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(set(optix["row_counts"]), {8921})
        self.assertEqual(optix["implementation_path"], "compiled_rtdl_kernel")
        self.assertTrue(optix["all_parity_vs_reference"])
        self.assertLess(optix["elapsed_sec_median"], 0.1)

    def test_pip_current_artifact_uses_prepared_membership(self) -> None:
        data = self._artifact(PIP)
        optix = data["backends"]["optix"]

        self.assertEqual(data["commit"], "949ca4f60a19b61bade10682d17a645bc07ec588")
        self.assertEqual(data["workload"], "pip")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(set(optix["row_counts"]), {8686})
        self.assertEqual(optix["implementation_path"], "prepared_closed_shape_membership_2d_optix")
        self.assertEqual(
            optix["input_preparation_path"],
            "prepared_shape_scene_and_prepacked_points_once_per_run_stream",
        )
        self.assertTrue(optix["all_parity_vs_reference"])
        self.assertLess(optix["elapsed_sec_median"], 0.07)

    def test_report_keeps_rayjoin_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not to claim RTDL reproduces or beats RayJoin", text)
        self.assertIn("Python-visible runtime call", text)
        self.assertIn("does not authorize", text)
        self.assertIn("device-resident output streams", text)


if __name__ == "__main__":
    unittest.main()
