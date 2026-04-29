import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal887_prepared_decision_phase_profiler.py"


class Goal887PreparedDecisionPhaseProfilerTest(unittest.TestCase):
    def test_dry_run_profiles_all_prepared_decision_scenarios(self) -> None:
        scenarios = (
            "hausdorff_threshold",
            "ann_candidate_coverage",
            "facility_service_coverage",
            "facility_service_coverage_recentered",
            "barnes_hut_node_coverage",
        )
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            tmp = Path(tmpdir)
            for scenario in scenarios:
                output = tmp / f"{scenario}.json"
                command = [
                    sys.executable,
                    str(SCRIPT),
                    "--scenario",
                    scenario,
                    "--mode",
                    "dry-run",
                    "--copies",
                    "2",
                    "--body-count",
                    "32",
                    "--iterations",
                    "2",
                    "--output-json",
                    str(output.relative_to(ROOT)),
                ]
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                summary = json.loads(completed.stdout)
                payload = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(summary["scenario"], scenario)
                self.assertEqual(payload["schema_version"], "goal887_prepared_decision_phase_contract_v1")
                self.assertEqual(payload["scenario"]["scenario"], scenario)
                self.assertEqual(payload["scenario"]["mode"], "dry-run")
                self.assertIn("cloud_claim_contract", payload)
                self.assertIn("required_phase_groups", payload["cloud_claim_contract"])
                self.assertIn("does not authorize an RTX speedup claim", payload["boundary"])

    def test_manifest_uses_phase_profiler_for_new_prepared_decision_entries(self) -> None:
        from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest

        manifest = build_manifest()
        by_path = {
            entry["path_name"]: entry
            for entry in (manifest["entries"] + manifest["deferred_entries"])
        }
        expected = {
            "directed_threshold_prepared": "hausdorff_threshold",
            "candidate_threshold_prepared": "ann_candidate_coverage",
            "coverage_threshold_prepared": "facility_service_coverage",
            "node_coverage_prepared": "barnes_hut_node_coverage",
        }
        for path_name, scenario in expected.items():
            with self.subTest(path_name=path_name):
                command = by_path[path_name]["command"]
                self.assertIn("scripts/goal887_prepared_decision_phase_profiler.py", command)
                self.assertIn("--scenario", command)
                self.assertIn(scenario, command)
                self.assertIn("--output-json", command)
                if scenario == "facility_service_coverage":
                    self.assertIn("--skip-validation", command)
                else:
                    self.assertNotIn("--skip-validation", command)

    def test_ann_dry_run_uses_tiled_threshold_oracle(self) -> None:
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        payload = goal887.run_profile(
            scenario="ann_candidate_coverage",
            mode="dry-run",
            copies=5000,
            body_count=32,
            iterations=1,
            radius=0.2,
            skip_validation=False,
        )
        result = payload["scenario"]["result"]
        self.assertTrue(result["within_candidate_radius"])
        self.assertEqual(result["query_count"], 15000)
        self.assertEqual(result["covered_query_count"], 15000)

    def test_facility_recentered_keeps_large_copy_coordinates_local(self) -> None:
        from examples import rtdl_facility_knn_assignment as facility_app
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        case = facility_app.make_facility_knn_case(copies=1000)
        recentered = goal887._recenter_facility_points(case["customers"])

        self.assertGreater(max(point.x for point in case["customers"]), 5000.0)
        self.assertLess(max(point.x for point in recentered), 4.0)

    def test_facility_recentered_dry_run_records_mapping(self) -> None:
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        payload = goal887.run_profile(
            scenario="facility_service_coverage_recentered",
            mode="dry-run",
            copies=1000,
            body_count=32,
            iterations=1,
            radius=1.0,
            skip_validation=False,
        )
        result = payload["scenario"]["result"]
        self.assertEqual(payload["scenario"]["scenario"], "facility_service_coverage_recentered")
        self.assertEqual(payload["scenario"]["coordinate_mapping"], "copy_local_recentered_queries_canonical_depots")
        self.assertEqual(result["coordinate_mapping"], "copy_local_recentered_queries_canonical_depots")
        self.assertTrue(result["all_customers_covered"])
        self.assertEqual(result["customer_count"], 4000)

    def test_barnes_hut_rich_contract_uses_depth_and_hit_threshold(self) -> None:
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        payload = goal887.run_profile(
            scenario="barnes_hut_node_coverage",
            mode="dry-run",
            copies=1,
            body_count=64,
            iterations=1,
            radius=1.0,
            skip_validation=False,
            barnes_tree_depth=4,
            hit_threshold=4,
        )
        result = payload["scenario"]["result"]
        self.assertEqual(payload["parameters"]["barnes_tree_depth"], 4)
        self.assertEqual(payload["parameters"]["hit_threshold"], 4)
        self.assertEqual(result["node_count"], 256)
        self.assertEqual(result["barnes_tree_depth"], 4)
        self.assertEqual(result["threshold"], 4)
        self.assertGreaterEqual(result["max_candidate_count"], result["min_candidate_count"])

    def test_barnes_hut_rich_contract_cli_flags_are_recorded(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output = Path(tmpdir) / "barnes_rich.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scenario",
                    "barnes_hut_node_coverage",
                    "--mode",
                    "dry-run",
                    "--body-count",
                    "64",
                    "--iterations",
                    "1",
                    "--radius",
                    "1.0",
                    "--barnes-tree-depth",
                    "4",
                    "--hit-threshold",
                    "4",
                    "--output-json",
                    str(output.relative_to(ROOT)),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn("barnes_hut_node_coverage", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["parameters"]["barnes_tree_depth"], 4)
            self.assertEqual(payload["parameters"]["hit_threshold"], 4)
            self.assertEqual(payload["scenario"]["result"]["node_count"], 256)


if __name__ == "__main__":
    unittest.main()
