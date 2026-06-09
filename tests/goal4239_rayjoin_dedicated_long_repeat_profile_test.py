from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4239_rayjoin_dedicated_long_repeat_rtx4000ada"
PAYLOAD = ARTIFACT_DIR / "rayjoin_long_repeat.stdout.json"
STDERR = ARTIFACT_DIR / "rayjoin_long_repeat.stderr.txt"
REPORT = ROOT / "docs" / "reports" / "goal4239_rayjoin_dedicated_long_repeat_profile_2026-06-09.md"

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
    "rtdl_beats_rayjoin_claim_authorized",
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


class Goal4239RayJoinDedicatedLongRepeatProfileTest(unittest.TestCase):
    def test_artifacts_and_report_exist(self) -> None:
        self.assertTrue(PAYLOAD.is_file())
        self.assertTrue(STDERR.is_file())
        self.assertTrue(REPORT.is_file())

    def test_long_repeat_payload_has_clean_provenance_and_counts(self) -> None:
        payload = _load(PAYLOAD)
        self.assertEqual(payload["schema"], "rtdl.goal3866.rayjoin_representative_scale_profile.v1")
        self.assertEqual(payload["git_commit"][:8], "048d940c")
        self.assertEqual(payload["git_status_short"], "")
        self.assertIn("NVIDIA RTX 4000 Ada Generation", payload["gpu"])
        self.assertEqual(payload["repeat"], 200)
        self.assertEqual(payload["warmup"], 20)
        self.assertGreater(payload["wrapper_elapsed_sec"], 20.0)
        self.assertTrue(payload["all_counts_match"])

        hot = payload["representative_hot_path_summary"]
        self.assertTrue(hot["all_contract_counts_match"])
        self.assertEqual(hot["contract_count"], 4)
        self.assertEqual(hot["metric_scope"], "per_contract_hot_medians_not_wrapper_wall_time")
        self.assertTrue(hot["scale_runner_elapsed_sec_is_not_hot_path_metric"])

    def test_route_split_remains_visible_and_stable(self) -> None:
        payload = _load(PAYLOAD)
        hot = payload["representative_hot_path_summary"]
        route_summary = hot["recommended_route_summary"]
        self.assertFalse(route_summary["automatic_dispatch"])
        self.assertTrue(route_summary["user_route_choice_visible"])
        self.assertEqual(route_summary["numba_contracts"], ["pip_one_shot"])
        self.assertEqual(
            route_summary["rtdl_optix_contracts"],
            ["pip_repeated_requests", "lsi_scalar_count", "overlay_active_count"],
        )

        self.assertLess(hot["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(hot["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 1.0)
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 100.0)
        self.assertGreater(hot["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 100.0)

    def test_claim_boundaries_remain_closed(self) -> None:
        payload = _load(PAYLOAD)
        self.assertEqual(_forbidden_true_paths(payload), [])
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "does not authorize release action",
            "RayJoin paper-reproduction wording",
            "RTDL-beats-RayJoin wording",
            "automatic partner selection",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
