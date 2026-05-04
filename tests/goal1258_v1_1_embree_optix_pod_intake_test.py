from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1258_v1_1_embree_optix_pod_intake import build_intake
from scripts.goal1258_v1_1_embree_optix_pod_intake import to_markdown


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _db_payload(sec: float) -> dict[str, object]:
    return {
        "results": [
            {
                "prepared_session_warm_query_sec": {"median_sec": sec},
                "db_review_observation": {
                    "status": "phase_clean_candidate_for_rtx_review",
                    "row_materializing_operation_count": 0,
                },
            }
        ]
    }


class Goal1258V11EmbreeOptixPodIntakeTest(unittest.TestCase):
    def test_missing_default_artifacts_are_non_claim_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = build_intake(Path(tmp))
        self.assertFalse(payload["valid"])
        self.assertGreater(len(payload["missing_artifacts"]), 0)
        self.assertFalse(payload["public_wording_authorized"])
        self.assertEqual(payload["decisions"]["database_analytics"], "baseline_contract_incomplete")

    def test_intake_classifies_synthetic_complete_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "goal1257_status_summary.json", {"status_count": 17, "failed_count": 0, "failed_labels": []})
            for copies in (30000, 100000):
                _write(root / f"db_embree_{copies}.status.json", {"status": "ok", "exit_code": 0})
                _write(root / f"db_optix_{copies}.status.json", {"status": "ok", "exit_code": 0})
                _write(root / f"db_embree_{copies}.json", _db_payload(2.0))
                _write(root / f"db_optix_{copies}.json", _db_payload(1.0))
            for copies in (30000, 60000):
                _write(
                    root / f"graph_embree_visibility_{copies}.json",
                    {"graph_phase_totals_sec": {"query_visibility_pair_rows_sec": 3.0}},
                )
                _write(
                    root / f"graph_optix_visibility_{copies}.json",
                    {
                        "status": "pass",
                        "strict_pass": True,
                        "records": [
                            {
                                "label": "optix_visibility_anyhit",
                                "status": "ok",
                                "sec": 6.0,
                                "section_run_phases": {"query_anyhit_count_sec": 0.5},
                            }
                        ],
                    },
                )
            for copies in (10000, 40000):
                _write(
                    root / f"polygon_pair_embree_{copies}.json",
                    {"run_phases": {"rt_candidate_discovery_sec": 2.0}},
                )
                _write(
                    root / f"polygon_pair_optix_{copies}.json",
                    {
                        "status": "pass",
                        "parity_vs_cpu": True,
                        "phases": {"optix_candidate_discovery_sec": 1.0},
                        "candidate_diagnostics": {"candidate_count_matches_expected": True},
                    },
                )
            for copies in (4096, 8192):
                _write(
                    root / f"polygon_jaccard_embree_{copies}.json",
                    {"run_phases": {"rt_candidate_discovery_sec": 1.0}},
                )
                _write(
                    root / f"polygon_jaccard_optix_{copies}.json",
                    {
                        "status": "pass",
                        "parity_vs_cpu": True,
                        "chunk_copies": 1024,
                        "chunk_policy": {"policy": "public_safe", "public_safe": True},
                        "phases": {"optix_candidate_discovery_sec": 2.0},
                        "candidate_diagnostics": {"candidate_count_matches_expected": True},
                    },
                )
            payload = build_intake(root)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["decisions"]["database_analytics"], "optix_improved")
        self.assertEqual(payload["decisions"]["graph_analytics"], "optix_still_slower_with_reason")
        self.assertGreater(payload["graph_analytics"][0]["ratio_embree_over_optix_kernel"], 1.0)
        self.assertEqual(payload["decisions"]["polygon_pair_overlap_area_rows"], "optix_improved")
        self.assertEqual(payload["decisions"]["polygon_set_jaccard"], "optix_still_slower_with_reason")
        self.assertFalse(payload["public_wording_authorized"])

    def test_markdown_preserves_key_goal_consensus_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = to_markdown(build_intake(Path(tmp)))
        self.assertIn("does not authorize public RTX speedup wording", text)
        self.assertIn("requires 3-AI consensus", text)
        self.assertIn("Public wording authorized: `False`", text)


if __name__ == "__main__":
    unittest.main()
