import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2226_current_rayjoin_same_stream_snapshot_pod_2026-05-17.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2226_current_rayjoin_same_stream_snapshot_pod"
LSI = ARTIFACT_DIR / "rtdl_lsi_current_cpu_optix.json"
PIP = ARTIFACT_DIR / "rtdl_pip_current_embree_optix.json"


class Goal2226CurrentRayJoinSameStreamSnapshotPodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lsi = json.loads(LSI.read_text(encoding="utf-8"))
        cls.pip = json.loads(PIP.read_text(encoding="utf-8"))

    def test_lsi_current_snapshot_has_cpu_and_optix_parity(self) -> None:
        self.assertEqual(self.lsi["workload"], "lsi")
        self.assertEqual(self.lsi["reference_row_count"], 8921)
        self.assertTrue(self.lsi["commit"].startswith("0ff12cef"))
        for backend in ("cpu", "optix"):
            item = self.lsi["backends"][backend]
            self.assertTrue(item["all_parity_vs_reference"])
            self.assertTrue(item["row_count_consistent"])
        self.assertLess(
            self.lsi["backends"]["optix"]["elapsed_sec_median"],
            self.lsi["backends"]["cpu"]["elapsed_sec_median"] / 10.0,
        )

    def test_pip_current_snapshot_has_embree_and_optix_parity(self) -> None:
        self.assertEqual(self.pip["workload"], "pip")
        self.assertEqual(self.pip["reference_row_count"], 8686)
        self.assertTrue(self.pip["commit"].startswith("0ff12cef"))
        for backend in ("embree", "optix"):
            item = self.pip["backends"][backend]
            self.assertTrue(item["all_parity_vs_reference"])
            self.assertTrue(item["row_count_consistent"])
        self.assertLess(
            self.pip["backends"]["optix"]["elapsed_sec_median"],
            self.pip["backends"]["embree"]["elapsed_sec_median"],
        )

    def test_report_records_boundaries_and_artifacts(self) -> None:
        for name in (
            "progress.log",
            "build_optix.log",
            "rtdl_lsi_current_cpu_optix.log",
            "rtdl_lsi_current_cpu_optix.json",
            "rtdl_pip_current_embree_optix.log",
            "rtdl_pip_current_embree_optix.json",
        ):
            self.assertTrue((ARTIFACT_DIR / name).exists(), name)
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2226", text)
        self.assertIn("16.28x", text)
        self.assertIn("1.20x", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL beats RayJoin", text)


if __name__ == "__main__":
    unittest.main()
