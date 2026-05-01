from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1205_repaired_rtx_pod_intake import build_intake, to_markdown


def _write_json(root: Path, name: str, payload: dict) -> None:
    (root / name).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _status(root: Path, label: str, status: str = "ok") -> None:
    _write_json(root, f"{label}.status.json", {"label": label, "exit_code": 0, "status": status})


class Goal1205RepairedRtxPodIntakeTest(unittest.TestCase):
    def test_intake_promotes_repaired_paths_only_as_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root, "goal1204_status_summary.json", {"status_count": 8, "failed_count": 0, "failed_labels": []})
            for copies in (100000, 300000):
                for backend, sec in (("embree", 0.4), ("optix", 0.2)):
                    label = f"db_{backend}_{copies}_chunked_repair"
                    _status(root, label)
                    _write_json(
                        root,
                        f"{label}.json",
                        {
                            "results": [
                                {
                                    "prepared_session_warm_query_sec": {"median_sec": sec},
                                    "prepared_session_output": {
                                        "sections": {
                                            "sales_risk": {
                                                "prepared_dataset": {
                                                    "transfer": "chunked_columnar",
                                                    "chunk_count": 2,
                                                },
                                                "session": {
                                                    "chunked_compact_summary": True,
                                                    "chunk_count": 2,
                                                },
                                            }
                                        }
                                    },
                                }
                            ],
                        },
                    )
            _status(root, "jaccard_optix_8192_public_safe_chunk_512")
            _write_json(
                root,
                "jaccard_optix_8192_public_safe_chunk_512.json",
                {
                    "chunk_policy": {"public_safe": True, "policy": "public_safe"},
                    "parity_vs_cpu": True,
                    "phases": {"optix_candidate_discovery_sec": 0.3},
                },
            )
            _status(root, "jaccard_optix_8192_diagnostic_chunk_64")
            _write_json(
                root,
                "jaccard_optix_8192_diagnostic_chunk_64.json",
                {
                    "chunk_policy": {"public_safe": False, "policy": "diagnostic_only"},
                    "parity_vs_cpu": False,
                    "phases": {"optix_candidate_discovery_sec": 0.05},
                },
            )
            _status(root, "road_hazard_embree_control_40000")
            _write_json(root, "road_hazard_embree_control_40000.json", {"run_phases": {"query_and_materialize_sec": 0.8}})
            _status(root, "road_hazard_optix_control_40000")
            _write_json(
                root,
                "road_hazard_optix_control_40000.json",
                {"timings_sec": {"optix_query_sec": {"median_sec": 0.2}}},
            )

            payload = build_intake(root)
            self.assertTrue(payload["valid"])
            self.assertEqual(payload["decisions"]["database_analytics"], "repair_passed")
            self.assertEqual(payload["decisions"]["polygon_set_jaccard"], "public_safe_chunk_ready")
            self.assertEqual(payload["decisions"]["road_hazard_screening"], "same_scale_public_positive_candidate")
            self.assertIn("public_safe_chunk_ready", payload["decisions"].values())

    def test_incomplete_artifact_blocks_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root, "goal1204_status_summary.json", {"status_count": 8, "failed_count": 1, "failed_labels": ["x"]})
            payload = build_intake(root)
            self.assertEqual(payload["decisions"]["database_analytics"], "blocked_or_incomplete")
            self.assertEqual(payload["decisions"]["polygon_set_jaccard"], "blocked_or_incomplete")
            self.assertEqual(payload["decisions"]["road_hazard_screening"], "blocked_or_floor_not_met")

    def test_markdown_preserves_non_claim_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root, "goal1204_status_summary.json", {"status_count": 0, "failed_count": 0, "failed_labels": []})
            text = to_markdown(build_intake(root))
            self.assertIn("does not authorize public docs", text)
            self.assertIn("Database Analytics", text)
            self.assertIn("Polygon Jaccard", text)
            self.assertIn("Road Hazard", text)


if __name__ == "__main__":
    unittest.main()
