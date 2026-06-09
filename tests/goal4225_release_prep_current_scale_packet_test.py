from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4225_release_grade_current_scale_packet_rtx4000ada"
PACKET = ARTIFACT_DIR / "current_scale_profile_packet.json"
REPORT = ROOT / "docs" / "reports" / "goal4225_release_prep_current_scale_packet_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
    "v2_0_release_authorized",
    "v2_6_release_authorized",
    "v2_8_release_authorized",
    "v2_9_release_authorized",
    "v2_10_release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "true_zero_copy_claim_authorized",
    "true_zero_copy_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
    "amd_performance_claim_authorized",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _forbidden_true_paths(value, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_forbidden_true_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_forbidden_true_paths(child, f"{path}[{index}]"))
    return hits


class Goal4225ReleasePrepCurrentScalePacketTest(unittest.TestCase):
    def test_packet_and_report_exist(self) -> None:
        self.assertTrue(PACKET.is_file())
        self.assertTrue(REPORT.is_file())

    def test_all_current_front_doors_pass_on_clean_pod_head(self) -> None:
        packet = _load(PACKET)
        self.assertTrue(packet["all_pass"])
        self.assertEqual(packet["json_pass_count"], 10)
        self.assertEqual(packet["summary"]["row_count"], 10)
        self.assertEqual(packet["summary"]["app_count"], 10)
        runtime = packet["runtime_environment"]
        self.assertEqual(runtime["source_commit_short"], "0d9786ca")
        self.assertTrue(runtime["working_tree_clean"])
        self.assertEqual(runtime["git_status_short"], [])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", runtime["nvidia_smi"])
        self.assertEqual({row["status"] for row in packet["rows"]}, {"pass"})
        self.assertEqual(len({row["app"] for row in packet["rows"]}), 10)

    def test_claim_boundaries_remain_closed_in_packet_and_payloads(self) -> None:
        packet = _load(PACKET)
        self.assertEqual(_forbidden_true_paths(packet), [])
        for row in packet["rows"]:
            semantic = row["semantic_stdout_check"]
            self.assertTrue(semantic["stdout_json_parseable"], row["row_id"])
            self.assertEqual(semantic["claim_flag_violations"], [], row["row_id"])
            payload = _load(ROOT / row["stdout_path"])
            self.assertEqual(_forbidden_true_paths(payload), [], row["row_id"])

    def test_packet_is_not_promoted_to_release_claim_grade(self) -> None:
        packet = _load(PACKET)
        statuses = set(packet["summary"]["scale_calibration_statuses"])
        self.assertIn("internal_current_scale_not_claim_grade", statuses)
        self.assertIn("resident_high_repeat_summary_contract_goal3984", statuses)
        classes = {row["expected_runtime_class"] for row in packet["rows"]}
        self.assertIn("safe_but_short", classes)
        self.assertIn("resident_high_repeat_hot_path_summary", classes)

    def test_rayjoin_and_rtdbscan_current_rows_keep_latest_policy(self) -> None:
        packet = _load(PACKET)
        by_app = {row["app"]: row for row in packet["rows"]}
        rayjoin = _load(ROOT / by_app["spatial_rayjoin"]["stdout_path"])
        hot = rayjoin["representative_hot_path_summary"]
        self.assertEqual(hot["recommended_route_summary"]["numba_contracts"], ["pip_one_shot"])
        self.assertIn("lsi_scalar_count", hot["recommended_route_summary"]["rtdl_optix_contracts"])
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 100.0)

        rtdbscan = _load(ROOT / by_app["rt_dbscan"]["stdout_path"])
        metadata = rtdbscan["metadata"]
        self.assertEqual(metadata["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(metadata["grouped_stream_continuation_pass_count"], 1)


if __name__ == "__main__":
    unittest.main()
