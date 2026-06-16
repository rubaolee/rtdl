from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4460_v3_0_m64_rtnn_shell_app_bridge_2026-06-16.md"
EVIDENCE = (
    ROOT
    / "docs/reports/goal4460_v3_0_m64_rtnn_app_bridge_shell_1048576q65536_r1000_2026-06-16.json"
)
UNIFORM_EVIDENCE = (
    ROOT
    / "docs/reports/goal4443_v3_0_m47_rtnn_app_bridge_uniform_1048576q65536_r1000_2026-06-16.json"
)
CLUSTERED_EVIDENCE = (
    ROOT
    / "docs/reports/goal4459_v3_0_m63_rtnn_app_bridge_clustered_1048576q65536_r1000_2026-06-16.json"
)
RTNN_README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
EVIDENCE_INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
RT_CORE_MATRIX = ROOT / "docs/learn/rt_core_evidence_matrix.md"


class Goal4460V30M64RtnnShellAppBridgeTest(unittest.TestCase):
    def test_shell_distribution_is_supported_without_app_specific_native_abi(self) -> None:
        points = rt.make_v3_m19_ranked_summary_points(1024, distribution="shell")
        radii = [((point.x - 0.5) ** 2 + (point.y - 0.5) ** 2 + (point.z - 0.5) ** 2) ** 0.5 for point in points]

        self.assertEqual(("uniform", "clustered", "shell"), rt.V3_M19_DISTRIBUTIONS)
        self.assertEqual(1024, len(points))
        self.assertGreater(min(radii), 0.20)
        self.assertLess(max(radii), 0.49)
        self.assertGreater(sum(abs(point.z - 0.5) for point in points) / len(points), 0.12)

    def test_shell_app_bridge_artifact_is_large_and_signature_clean(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        compact = payload["compact_summary"]

        self.assertEqual(payload["benchmark_app"], "rtnn_neighbor_search")
        self.assertEqual(payload["mode"], "prepared_ranked_summary_graph_partner_bridge")
        self.assertEqual(compact["distribution"], "shell")
        self.assertEqual(compact["point_count"], 1_048_576)
        self.assertEqual(compact["query_count"], 65_536)
        self.assertEqual(compact["repeats"], 1000)
        self.assertEqual(compact["warmups"], 2)
        self.assertEqual(compact["partners"], ["cupy", "numba"])
        self.assertTrue(compact["signature_match"])
        self.assertTrue(compact["hot_no_hidden_column_copy_ready"])
        self.assertTrue(compact["device_result_materialization_after_hot_window"])
        self.assertFalse(compact["public_claim_authorized"])

        cupy = compact["partner_rows"]["cupy"]
        numba = compact["partner_rows"]["numba"]
        cupy_hot = float(cupy["hot_device_run_seconds_median"])
        numba_hot = float(numba["hot_device_run_seconds_median"])

        self.assertGreater(cupy_hot, 0.03)
        self.assertLess(cupy_hot, 0.05)
        self.assertGreater(numba_hot, 0.03)
        self.assertLess(numba_hot, 0.05)
        self.assertGreater(cupy_hot * compact["repeats"], 30.0)
        self.assertGreater(numba_hot * compact["repeats"], 30.0)
        self.assertLess(numba_hot / cupy_hot, 1.05)

        for row in (cupy, numba):
            self.assertTrue(row["cuda_graph_replay_used"])
            self.assertTrue(row["same_stream_partner_device_reduction_used"])
            self.assertTrue(row["hot_no_hidden_column_copy_ready"])
            self.assertTrue(row["device_result_materialization_after_hot_window"])

    def test_shell_sits_between_uniform_and_clustered_large_rows(self) -> None:
        uniform = json.loads(UNIFORM_EVIDENCE.read_text(encoding="utf-8"))["compact_summary"]
        shell = json.loads(EVIDENCE.read_text(encoding="utf-8"))["compact_summary"]
        clustered = json.loads(CLUSTERED_EVIDENCE.read_text(encoding="utf-8"))["compact_summary"]

        self.assertEqual("uniform", uniform["distribution"])
        self.assertEqual("shell", shell["distribution"])
        self.assertEqual("clustered", clustered["distribution"])
        for partner in ("cupy", "numba"):
            uniform_hot = float(uniform["partner_rows"][partner]["hot_device_run_seconds_median"])
            shell_hot = float(shell["partner_rows"][partner]["hot_device_run_seconds_median"])
            clustered_hot = float(clustered["partner_rows"][partner]["hot_device_run_seconds_median"])
            self.assertLess(uniform_hot, shell_hot)
            self.assertLess(shell_hot, clustered_hot)

    def test_shell_app_bridge_updates_docs_and_route_registry(self) -> None:
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}["rtnn"]
        report = REPORT.read_text(encoding="utf-8")
        readme = RTNN_README.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        rt_core_matrix = RT_CORE_MATRIX.read_text(encoding="utf-8")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4465.v1",
            route["version"],
        )
        self.assertIn("Goal4460", route["evidence_refs"])
        self.assertIn("shell distribution row", route["current_reader_decision"])
        self.assertIn("38.588ms", route["current_reader_decision"])
        self.assertIn("39.267ms", route["current_reader_decision"])
        self.assertIn(
            "treating the shell resident app bridge as a full RTNN paper row",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("not more synthetic distribution timing", route["next_runtime_action"])
        self.assertFalse(route["paper_reproduction_claim_authorized"])
        self.assertFalse(route["automatic_partner_selection_authorized"])

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4465.v1",
            adequacy["version"],
        )
        self.assertEqual("strong", adequacy["adequacy"])
        self.assertIn("Goal4460", adequacy["evidence_refs"])
        self.assertIn("shell distribution row", adequacy["current_performance_reading"])
        self.assertFalse(adequacy["public_speedup_claim_authorized"])

        for text in (report, readme, evidence_index, partner_matrix, rt_core_matrix):
            self.assertIn("Goal4460", text)
            self.assertIn("shell", text)
        self.assertIn("not a synthetic substitute for an official RTNN paper dataset", readme)
        self.assertIn("It is not full RTNN paper reproduction", report)


if __name__ == "__main__":
    unittest.main()
