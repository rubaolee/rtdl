from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1206_repaired_rtx_recovery_merge_intake import build_merged_intake


def _write_json(root: Path, name: str, payload: dict) -> None:
    (root / name).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _status(root: Path, label: str, status: str = "ok") -> None:
    _write_json(root, f"{label}.status.json", {"label": label, "exit_code": 0 if status == "ok" else 1, "status": status})


class Goal1206RepairedRtxRecoveryMergeIntakeTest(unittest.TestCase):
    def test_recovery_rows_replace_failed_original_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "original"
            recovery = root / "recovery"
            original.mkdir()
            recovery.mkdir()
            _write_json(original, "goal1204_status_summary.json", {"status_count": 8, "failed_count": 3, "failed_labels": []})
            for copies in (100000, 300000):
                _status(original, f"db_embree_{copies}_chunked_repair", "failed")
                _status(original, f"db_optix_{copies}_chunked_repair", "ok")
                _write_json(
                    original,
                    f"db_optix_{copies}_chunked_repair.json",
                    {
                        "results": [
                            {
                                "prepared_session_warm_query_sec": {"median_sec": 0.2},
                                "prepared_session_output": {
                                    "sections": {
                                        "sales_risk": {
                                            "prepared_dataset": {"transfer": "chunked_columnar"},
                                            "session": {"chunked_compact_summary": True},
                                        }
                                    }
                                },
                            }
                        ]
                    },
                )
                label = f"db_embree_{copies}_chunked_repair_usr_recovery"
                _status(recovery, label, "ok")
                _write_json(
                    recovery,
                    f"{label}.json",
                    {
                        "results": [
                            {
                                "prepared_session_warm_query_sec": {"median_sec": 0.4},
                                "prepared_session_output": {
                                    "sections": {
                                        "sales_risk": {
                                            "prepared_dataset": {"transfer": "chunked_columnar"},
                                            "session": {"chunked_compact_summary": True},
                                        }
                                    }
                                },
                            }
                        ]
                    },
                )
            _status(original, "jaccard_optix_8192_public_safe_chunk_512")
            _write_json(
                original,
                "jaccard_optix_8192_public_safe_chunk_512.json",
                {"chunk_policy": {"policy": "public_safe", "public_safe": True}, "parity_vs_cpu": True},
            )
            _status(original, "jaccard_optix_8192_diagnostic_chunk_64")
            _write_json(
                original,
                "jaccard_optix_8192_diagnostic_chunk_64.json",
                {"chunk_policy": {"policy": "diagnostic_only", "public_safe": False}, "parity_vs_cpu": False},
            )
            _status(original, "road_hazard_embree_control_40000", "failed")
            _status(original, "road_hazard_optix_control_40000", "ok")
            _write_json(original, "road_hazard_optix_control_40000.json", {"timings_sec": {"optix_query_sec": {"median_sec": 0.2}}})
            _status(recovery, "road_hazard_embree_control_40000_usr_recovery", "ok")
            _write_json(recovery, "road_hazard_embree_control_40000_usr_recovery.json", {"run_phases": {"query_and_materialize_sec": 0.8}})

            payload = build_merged_intake(original, recovery)
            self.assertEqual(payload["decisions"]["database_analytics"], "repair_passed")
            self.assertEqual(payload["decisions"]["polygon_set_jaccard"], "public_safe_chunk_ready")
            self.assertEqual(payload["decisions"]["road_hazard_screening"], "same_scale_public_positive_candidate")
            self.assertGreaterEqual(len(payload["recovery_copied_files"]), 6)


if __name__ == "__main__":
    unittest.main()
