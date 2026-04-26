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


if __name__ == "__main__":
    unittest.main()
