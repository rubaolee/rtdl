from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2803_barnes_hut_v25_consolidated_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2933_barnes_hut_cupy_vector_selection_2026-06-01.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2933_barnes_hut_cupy_vector_selection_pod" / "goal2933_barnes_hut_cupy_vector_selection.json"


class Goal2933BarnesHutCupyVectorSelectionTest(unittest.TestCase):
    def test_harness_considers_cupy_without_forcing_partner(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("cupy_available", source)
        self.assertIn('partner="cupy"', source)
        self.assertIn("selected_partner, selected_median = min", source)
        self.assertIn('f"{selected_partner}_wins_same_contract_timing"', source)

    def test_pod_artifact_selects_cupy_and_preserves_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        vector = payload["vector_sum"]

        self.assertEqual("pass", payload["status"])
        self.assertEqual("da4507c4214c32c50380ea31bb1414806b6e12ac", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertTrue(all(row["rows_match_between_backends"] for row in payload["membership_rows"]))
        self.assertTrue(all(row["optix_rt_core_accelerated"] for row in payload["membership_rows"]))
        self.assertEqual("cupy", vector["selected_partner"])
        self.assertTrue(vector["cupy_matches_torch"])
        self.assertLess(vector["cupy_over_torch_ratio"], 1.0)
        self.assertGreater(vector["triton_over_torch_ratio"], 1.0)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_manifest_and_readiness_index_goal2933(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        barnes = next(row for row in manifest["apps"] if row["app_id"] == "barnes_hut")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertIn("Goal2933", barnes["pod_evidence_status"])
        self.assertIn("CuPy", barnes["next_action"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2933_barnes_hut_cupy_vector_selection_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2933_barnes_hut_cupy_vector_selection_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])

    def test_report_records_no_release_or_public_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2933",
            "partner choice is real",
            "CuPy is the measured fastest same-contract partner",
            "does not authorize v2.5 release",
            "automatic CuPy selection",
            "app-specific native engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
