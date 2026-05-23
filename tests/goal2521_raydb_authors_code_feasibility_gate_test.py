import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2521_raydb_authors_code_feasibility_gate_2026-05-23.md"
ARTIFACT = ROOT / "docs/reports/goal2521_raydb_authors_code_feasibility_gate_2026-05-23.json"


class Goal2521RaydbAuthorsCodeFeasibilityGateTest(unittest.TestCase):
    def test_report_identifies_authors_repo_and_current_branch_head(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("https://github.com/LonelySlim/myOptixDB.git", text)
        self.assertIn("branch: `fin`", text)
        self.assertIn("a610c00d7334d8907435cc0a124f9ca8392ee456", text)
        self.assertIn("/tmp/rtdl_goal2521_myOptixDB", text)
        self.assertIn("third-party source copied into RTDL: no", text)

    def test_report_blocks_immediate_timing_and_performance_comparison(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not run or claim a performance comparison", text)
        self.assertIn("authors code built: no", text)
        self.assertIn("authors code timed: no", text)
        self.assertIn("same-contract comparison authorized: no", text)
        self.assertIn("public speedup claim authorized: no", text)
        self.assertIn("Performance comparison | Blocked", text)

    def test_report_records_build_data_license_and_same_contract_gates(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "blocked_without_dedicated_pod_and_legacy_toolchain",
            "blocked_generated_ssb_sf20_data_not_present",
            "unresolved_no_repo_level_license_file",
            "blocked_not_same_contract_yet",
            "dataset_size = 119994608",
            "CMAKE_C_COMPILER=/usr/bin/gcc-8",
        ):
            self.assertIn(phrase, text)

    def test_report_defines_same_contract_requirements_before_comparison(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "same input rows and columns",
            "same predicates",
            "same grouping keys",
            "same aggregate result modes",
            "same result materialization boundary",
            "same correctness oracle",
        ):
            self.assertIn(phrase, text)
        self.assertIn("Goal2524", text)
        self.assertIn("Goal2525", text)

    def test_artifact_matches_gate_decision(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["verdict"], "do_not_time_or_compare_yet")
        self.assertIs(payload["authors_code_available"], True)
        self.assertIs(payload["authors_code_built"], False)
        self.assertIs(payload["authors_code_timed"], False)
        self.assertIs(payload["performance_comparison_authorized"], False)
        self.assertIs(payload["public_speedup_claim_authorized"], False)
        self.assertIs(payload["source_copied_into_rtdl"], False)
        self.assertEqual(payload["authors_repository_branch"], "fin")
        self.assertEqual(payload["authors_repository_head"], "a610c00d7334d8907435cc0a124f9ca8392ee456")
        self.assertEqual(payload["dataset_size_in_authors_run_script"], 119994608)
        self.assertEqual(payload["build_gate_status"], "blocked_without_dedicated_pod_and_legacy_toolchain")
        self.assertEqual(payload["data_gate_status"], "blocked_generated_ssb_sf20_data_not_present")
        self.assertEqual(payload["license_gate_status"], "unresolved_no_repo_level_license_file")
        self.assertEqual(payload["comparison_gate_status"], "blocked_not_same_contract_yet")
        self.assertFalse(any(payload["same_contract_status"].values()))


if __name__ == "__main__":
    unittest.main()
