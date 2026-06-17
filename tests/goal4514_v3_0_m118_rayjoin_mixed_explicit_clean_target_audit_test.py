from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/spatial_rayjoin/README.md"
SCRIPT = ROOT / "scripts/goal4514_m118_rayjoin_mixed_explicit_clean_target_audit.py"


class Goal4514V30M118RayJoinMixedExplicitCleanTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4514_m118_rayjoin_mixed_explicit_clean_target_audit"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_closes_rayjoin_as_mixed_explicit_not_primitive_only(self) -> None:
        route = self.packet["route"]
        readiness = self.packet["readiness"]

        self.assertEqual(
            "rtdl.v3_0.rayjoin_mixed_explicit_clean_target_audit.goal4514.v1",
            self.packet["version"],
        )
        self.assertEqual("spatial_rayjoin", self.packet["app"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1",
            route["route_version"],
        )
        self.assertIn("prepared point/closed-shape batch count", route["primitive_contract"])
        self.assertFalse(self.packet["m113_applicability"]["current_route_should_use_m113"])
        self.assertTrue(readiness["internal_v3_mixed_explicit_target_closed"])
        self.assertFalse(readiness["full_rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(readiness["full_section57_8_of_8_reproduction_claim_authorized"])
        self.assertFalse(readiness["public_speedup_claim_authorized"])
        self.assertFalse(readiness["automatic_partner_selection_authorized"])
        self.assertFalse(readiness["rtdl_beats_rayjoin_claim_authorized"])

    def test_recommended_routes_preserve_pip_lsi_overlay_distinctions(self) -> None:
        rows = {row["contract"]: row for row in self.packet["representative_route_matrix"]}

        pip_one_shot = rows["PIP one-shot scalar count"]
        self.assertIn("Numba", pip_one_shot["recommended_route"])
        self.assertLess(pip_one_shot["rtdl_optix_vs_numba"], 1.0)

        pip_repeated = rows["PIP repeated-request scalar count"]
        self.assertIn("batch executor", pip_repeated["recommended_route"])
        self.assertAlmostEqual(0.145265, pip_repeated["median_ms_per_request_at_100_requests"])

        lsi = rows["LSI scalar count"]
        overlay = rows["Overlay active count"]
        self.assertIn("RTDL/OptiX", lsi["recommended_route"])
        self.assertGreater(lsi["rtdl_optix_vs_numba"], 100.0)
        self.assertIn("RTDL/OptiX", overlay["recommended_route"])
        self.assertGreater(overlay["rtdl_optix_vs_numba"], 100.0)

    def test_author_human_scale_overlay_and_graph_boundaries_are_locked(self) -> None:
        author = self.packet["author_comparison"]["direct_comparison"]
        human = self.packet["human_scale_optix_vs_embree"]["rows"]
        overlay = self.packet["section57_overlay"]
        active = self.packet["overlay_active_count_same_contract"]
        graph = self.packet["pip_graph_status"]

        self.assertGreater(author["lsi:optix"]["rayjoin_rt_over_rtdl"], 1.0)
        self.assertIn("RTDL backend faster", author["lsi:optix"]["readout"])
        self.assertLess(author["pip:optix"]["rayjoin_rt_over_rtdl"], 1.0)
        self.assertIn("RayJoin RT faster", author["pip:optix"]["readout"])

        self.assertAlmostEqual(
            29.93,
            human["spatial_rayjoin_lsi"]["speedup_embree_per_iter_div_optix_per_iter"],
            places=2,
        )
        self.assertAlmostEqual(
            1.10,
            human["spatial_rayjoin_pip"]["speedup_embree_per_iter_div_optix_per_iter"],
            places=2,
        )

        self.assertEqual(2, overlay["coverage"]["overlay_pairs_complete"])
        self.assertEqual(6, overlay["coverage"]["overlay_pairs_incomplete"])
        self.assertEqual(8, overlay["coverage"]["overlay_pairs_total"])
        self.assertEqual(2, len(overlay["complete_rows"]))
        self.assertTrue(all(row["lsi_counts_match"] for row in overlay["complete_rows"]))
        self.assertTrue(all(row["optix_vs_embree_total_speedup"] > 1.0 for row in overlay["complete_rows"]))
        self.assertFalse(overlay["full_section57_reproduction_claim_authorized"])

        self.assertEqual(174, active["active_count"])
        self.assertTrue(active["same_output_contract"])
        self.assertTrue(active["row_materialization_avoided"])
        self.assertGreater(active["optix_speedup_by_timed_median"], 400.0)
        self.assertFalse(active["public_speedup_claim_authorized"])

        self.assertEqual("failed_closed_before_native_prepare", graph["unvalidated_graph_status"])
        self.assertEqual("failed_closed_native_prepare", graph["validated_graph_status"])
        self.assertFalse(graph["graph_replay_current_path"])
        self.assertIn("batch executor", graph["recommended_repeated_pip_path"])

    def test_report_readme_index_and_script_capture_goal4514(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4514 / V3 M118", report)
        self.assertIn("RayJoin RT wins PIP", report)
        self.assertIn("Goal4514 RayJoin mixed-explicit clean-target audit", index)
        self.assertIn("Goal4514", readme)
        self.assertIn("mixed explicit", readme)
        self.assertIn("M113 is not", readme)
        self.assertIn("2/8", readme)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
