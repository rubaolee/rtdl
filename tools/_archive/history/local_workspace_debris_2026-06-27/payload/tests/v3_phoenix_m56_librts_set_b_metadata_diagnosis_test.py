import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_m47_librts_stability_protocol as m47


ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m55_librts_authorized_execution_20260623_2340"
)


class V3PhoenixM56LibRTSSetBMetadataDiagnosisTest(unittest.TestCase):
    def _load_payload(self, name: str) -> dict[str, object]:
        return json.loads((EXEC_DIR / name).read_text(encoding="utf-8"))

    def test_m55_red_payloads_used_productized_runner_but_lacked_set_b_metadata(self) -> None:
        for name, expected_contract in (
            (
                "optix_cold_single_shot_current_s01.stdout.json",
                "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            ),
            (
                "embree_32768_stress_current_s01.stdout.json",
                "generic_prepared_aabb_index_query_2d_count",
            ),
        ):
            payload = self._load_payload(name)
            metadata = payload["prepared_execution_session_runner_metadata"]

            self.assertTrue(payload["prepared_execution_session_runner_used"])
            self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
            self.assertEqual(payload["primitive_contract"], expected_contract)
            self.assertIsInstance(metadata, dict)
            self.assertEqual(metadata["runtime_executed_count"], 1)
            self.assertIsNot(metadata.get("set_b_control_candidate"), True)

    def test_m47_future_preflight_requires_current_set_b_source_signature(self) -> None:
        args = m47.parse_args(["--v2-root", str(ROOT)])
        preflight = m47.build_preflight(args)
        signature = preflight["current_librts_set_b_source_signature"]

        self.assertTrue(signature["required"])
        self.assertEqual(signature["command"][1], "-c")
        self.assertIn("set_b_control_candidate", signature["command"][2])
        self.assertIn("prepared_query_mode", signature["command"][2])

    def test_local_librts_runner_source_now_exposes_set_b_control_metadata(self) -> None:
        prepared = (ROOT / "src" / "rtdsl" / "prepared_execution.py").read_text(encoding="utf-8")
        app = (
            ROOT
            / "examples"
            / "current"
            / "research_benchmarks"
            / "librts_spatial_index"
            / "rtdl_librts_spatial_index_benchmark_app.py"
        ).read_text(encoding="utf-8")

        self.assertGreaterEqual(prepared.count('metadata["set_b_control_candidate"] = True'), 3)
        self.assertGreaterEqual(prepared.count('metadata["set_a_probe_candidate"] = False'), 3)
        self.assertIn('metadata["prepared_query_mode"] = "optix_prepared_query_set"', prepared)
        self.assertGreaterEqual(
            app.count('"set_b_control_candidate": bool(runner_metadata.get("set_b_control_candidate"))'),
            2,
        )
        self.assertIn('"prepared_query_mode": runner_metadata.get("prepared_query_mode")', app)

    def test_m56_external_reviews_and_completion_preserve_no_pod_scope(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m56_librts_set_b_metadata_diagnosis_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m56_goal_completion_audit_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m56_goal_completion_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m56_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "accept_m56_local_diagnosis_and_preflight_repair_no_pod_authorization",
            claude,
        )
        self.assertIn(
            "accept_m56_goal_complete_preflight_repair_no_pod_no_release",
            antigravity,
        )
        self.assertIn("m56_goal_complete_preflight_repair_no_pod_no_release", consensus)
        self.assertIn("m56_goal_complete_preflight_repair_no_pod_no_release", audit)
        for text in (claude, antigravity, consensus, audit):
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no second M47 run", text)
            self.assertIn("no public speedup wording", text)
            self.assertIn("no watch-row closure", text)


if __name__ == "__main__":
    unittest.main()
