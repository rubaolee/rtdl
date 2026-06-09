from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    RT_DBSCAN_DIRECT_STATUS_APP_MODE,
    RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
    explain_rt_dbscan_explicit_route_choice,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4121_rt_dbscan_explicit_route_choice_advisor_2026-06-09.md"


class Goal4121RtDbscanExplicitRouteChoiceAdvisorTest(unittest.TestCase):
    def test_repeated_profiles_return_explicit_direct_status_factor_options(self) -> None:
        cases = {
            "clustered3d": 0.25,
            "road3d": 0.25,
            "ngsim_dense": 0.5,
        }
        for dataset, factor in cases.items():
            with self.subTest(dataset=dataset):
                packet = explain_rt_dbscan_explicit_route_choice(
                    dataset,
                    repeated_component_signature=True,
                    point_count=65536,
                )
                first = packet["options"][0]

                self.assertEqual("advisory_only_no_dispatch", packet["status"])
                self.assertTrue(packet["user_must_select_route"])
                self.assertFalse(packet["automatic_dispatch_authorized"])
                self.assertFalse(packet["automatic_partner_selection_authorized"])
                self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])
                self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, first["mode"])
                self.assertEqual("cupy", first["partner"])
                self.assertEqual(factor, first["partition_cell_factor"])
                self.assertEqual(65536, first["tested_point_count"])
                self.assertIn("Goal4117", first["evidence_refs"])
                self.assertFalse(packet["release_authorized"])
                self.assertFalse(packet["public_speedup_claim_authorized"])

    def test_one_shot_exposes_direct_status_option_without_dispatch(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=False,
            point_count=65536,
        )
        first = packet["options"][0]

        self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, first["mode"])
        self.assertEqual("cupy", first["partner"])
        self.assertEqual(0.5, first["partition_cell_factor"])
        self.assertGreater(first["one_shot_total_speedup_vs_current"], 1.8)
        self.assertIn("Goal4130", first["evidence_refs"])
        self.assertEqual(RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE, packet["options"][-1]["mode"])
        self.assertFalse(packet["automatic_dispatch_authorized"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])

    def test_unknown_profile_requires_existing_dataset(self) -> None:
        with self.assertRaisesRegex(ValueError, "dataset must be tiny"):
            explain_rt_dbscan_explicit_route_choice(
                "new_profile",
                repeated_component_signature=True,
                point_count=65536,
            )

    def test_ngsim_scale_aware_options_rank_closest_evidence_first(self) -> None:
        packet = explain_rt_dbscan_explicit_route_choice(
            "ngsim_dense",
            repeated_component_signature=True,
            point_count=131072,
        )
        first = packet["options"][0]
        second = packet["options"][1]

        self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, first["mode"])
        self.assertEqual(0.25, first["partition_cell_factor"])
        self.assertEqual(131072, first["tested_point_count"])
        self.assertIn("Goal4122", first["evidence_refs"])
        self.assertEqual(0.5, second["partition_cell_factor"])
        self.assertEqual(65536, second["tested_point_count"])
        self.assertFalse(packet["automatic_partition_cell_factor_selection_authorized"])

    def test_cli_explain_route_choice_prints_advisory_without_running(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--dataset",
                "ngsim_dense",
                "--point-count",
                "131072",
                "--explain-route-choice",
                "--repeated-component-signature",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        packet = json.loads(completed.stdout)

        self.assertEqual("advisory_only_no_dispatch", packet["status"])
        self.assertEqual(RT_DBSCAN_DIRECT_STATUS_APP_MODE, packet["options"][0]["mode"])
        self.assertEqual(0.25, packet["options"][0]["partition_cell_factor"])
        self.assertEqual(131072, packet["options"][0]["tested_point_count"])
        self.assertFalse(packet["automatic_dispatch_authorized"])
        self.assertFalse(packet["automatic_partner_selection_authorized"])

    def test_report_documents_no_dispatch_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "explain_rt_dbscan_explicit_route_choice",
            "--explain-route-choice",
            "--repeated-component-signature",
            "0.25",
            "0.5",
            "not a dispatcher",
            "does not run a route",
            "select a partner",
            "select a factor",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
