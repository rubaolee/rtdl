from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada"
PACKET = ARTIFACT_DIR / "current_scale_profile_packet.json"
REPORT = ROOT / "docs" / "reports" / "goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
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


def _load_packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def _load_row_payload(row: dict) -> dict:
    stdout_path = ROOT / row["stdout_path"]
    return json.loads(stdout_path.read_text(encoding="utf-8"))


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


class Goal4215CurrentBenchmarkScaleProfileAfterPolicyTest(unittest.TestCase):
    def test_packet_and_report_exist(self) -> None:
        self.assertTrue(PACKET.is_file())
        self.assertTrue(REPORT.is_file())

    def test_all_ten_rows_pass_at_expected_source_commit(self) -> None:
        packet = _load_packet()
        self.assertTrue(packet["all_pass"])
        self.assertEqual(packet["json_pass_count"], 10)
        self.assertEqual(packet["summary"]["row_count"], 10)
        self.assertEqual(packet["runtime_environment"]["source_commit_short"], "63289bbc")
        self.assertIn("NVIDIA RTX 4000 Ada Generation", packet["runtime_environment"]["nvidia_smi"])
        self.assertEqual({row["status"] for row in packet["rows"]}, {"pass"})
        self.assertEqual(len({row["app"] for row in packet["rows"]}), 10)

    def test_claim_boundaries_remain_closed(self) -> None:
        packet = _load_packet()
        self.assertEqual(_forbidden_true_paths(packet), [])
        for row in packet["rows"]:
            semantic = row["semantic_stdout_check"]
            self.assertTrue(semantic["stdout_json_parseable"], row["row_id"])
            self.assertEqual(semantic["claim_flag_violations"], [], row["row_id"])
            payload = _load_row_payload(row)
            self.assertEqual(_forbidden_true_paths(payload), [], row["row_id"])

    def test_rtdbscan_uses_canonical_single_pass_policy_in_broad_packet(self) -> None:
        packet = _load_packet()
        row = next(row for row in packet["rows"] if row["app"] == "rt_dbscan")
        payload = _load_row_payload(row)
        metadata = payload["metadata"]
        self.assertEqual(metadata["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(metadata["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(metadata["grouped_stream_continuation_pass_count"], 1)
        native = metadata["native_grouped_stream_metadata"]
        self.assertEqual(native["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(native["boundary_assignment_pass_count"], 1)

    def test_rayjoin_fixture_repair_is_recorded_and_final_row_passes(self) -> None:
        fixture = ARTIFACT_DIR / "rayjoin_fixture_materialization.json"
        self.assertTrue(fixture.is_file())
        materialization = json.loads(fixture.read_text(encoding="utf-8"))
        slice_paths = {Path(row["path"]).name for row in materialization["slices"].values()}
        self.assertIn("br_county_start256_count512.cdb", slice_paths)
        self.assertIn("br_soil_start256_count512.cdb", slice_paths)

        packet = _load_packet()
        row = next(row for row in packet["rows"] if row["app"] == "spatial_rayjoin")
        payload = _load_row_payload(row)
        summary = payload["representative_hot_path_summary"]
        self.assertTrue(summary["all_contract_counts_match"])
        self.assertEqual(summary["contract_count"], 4)
        self.assertEqual(summary["recommended_route_summary"]["numba_contracts"], ["pip_one_shot"])
        self.assertIn("lsi_scalar_count", summary["recommended_route_summary"]["rtdl_optix_contracts"])
        self.assertGreater(summary["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 100.0)
        self.assertGreater(summary["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 100.0)


if __name__ == "__main__":
    unittest.main()
