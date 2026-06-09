from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4182_current_benchmark_scale_profile_refresh_rtx4000ada"
PACKET = ARTIFACT_DIR / "current_scale_profile_packet.json"
REPORT = ROOT / "docs" / "reports" / "goal4182_current_benchmark_scale_profile_refresh_rtx4000ada_2026-06-09.md"

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


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _flag_violations(value: Any, *, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_flag_violations(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_flag_violations(child, path=f"{path}[{index}]"))
    return hits


class Goal4182CurrentBenchmarkScaleProfileRefreshTest(unittest.TestCase):
    def test_packet_is_clean_all_pass_internal_evidence(self) -> None:
        packet = _load(PACKET)

        self.assertTrue(packet["all_pass"])
        self.assertEqual(packet["json_pass_count"], 10)
        self.assertTrue(packet["runtime_environment"]["working_tree_clean"])
        self.assertEqual(
            packet["runtime_environment"]["source_commit"],
            "79afb95a65bfb7a359efb56210294c89ec210060",
        )
        self.assertEqual(packet["runtime_environment"]["nvidia_smi"].split(",")[0], "NVIDIA RTX 4000 Ada Generation")
        self.assertEqual(packet["validation"]["status"], "accept")
        self.assertEqual(packet["summary"]["row_count"], 10)
        self.assertEqual(packet["summary"]["app_count"], 10)
        self.assertEqual(_flag_violations(packet), [])

    def test_every_row_has_json_stdout_and_no_claim_leak(self) -> None:
        packet = _load(PACKET)
        expected_apps = {
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut",
            "librts_spatial_index",
            "rtnn",
            "triangle_counting",
        }

        self.assertEqual({row["app"] for row in packet["rows"]}, expected_apps)
        for row in packet["rows"]:
            self.assertEqual(row["status"], "pass", row["row_id"])
            semantic = row["semantic_stdout_check"]
            self.assertTrue(semantic["stdout_json_parseable"], row["row_id"])
            self.assertEqual(semantic["claim_flag_violations"], [], row["row_id"])

            stdout = ARTIFACT_DIR / "outputs" / Path(row["stdout_path"]).name
            self.assertTrue(stdout.exists(), stdout)
            payload = _load(stdout)
            self.assertEqual(_flag_violations(payload), [], row["row_id"])

    def test_rayjoin_contract_split_is_preserved(self) -> None:
        rayjoin = _load(
            ARTIFACT_DIR
            / "outputs"
            / "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default.stdout.json"
        )
        hot = rayjoin["representative_hot_path_summary"]

        self.assertIn("rayjoin_public_cdb", rayjoin["pip_batch_executor"]["dataset"])
        self.assertTrue(rayjoin["pip_batch_executor"]["dataset"].endswith("br_county_start256_count512.cdb"))
        self.assertTrue(hot["all_contract_counts_match"])
        self.assertLess(hot["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 1.0)
        self.assertTrue(hot["recommended_route_summary"]["user_route_choice_visible"])
        self.assertFalse(hot["automatic_partner_selection_authorized"])

    def test_report_states_non_authorizing_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("10/10", text)
        self.assertIn("internal evidence", text)
        self.assertIn("does not authorize a release", text)
        self.assertIn("automatic partner selection", text)
        self.assertIn("3-AI consensus", text)


if __name__ == "__main__":
    unittest.main()
