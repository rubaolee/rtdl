from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_overlay_active_count_full_scale_candidate.py"


def _evidence(*, include_m3: bool = True) -> dict[str, object]:
    optix_row: dict[str, object] = {
        "backend": "optix",
        "output_contract": "overlay_active_pair_dependency_count",
        "active_count": 123,
        "counts_stable": True,
        "left_shape_count": 2000,
        "right_shape_count": 1500,
        "repeat": 25,
        "warmup": 3,
        "timed_median_sec": 0.002,
        "row_materialization_avoided": True,
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
    }
    if include_m3:
        optix_row.update(
            {
                "topology_stream_m3_phase_table": {
                    "contract": "topology_stream_m3_phase_table_v1",
                    "full_m3_phase_table_complete": True,
                    "phase_seconds": {
                        "static_scene_prepare_sec": 0.010,
                        "query_stream_prepare_sec": 0.009,
                        "device_transfer_or_residency_sec": 0.0,
                        "rt_traversal_sec": 0.006,
                        "topology_continuation_sec": 0.015,
                        "host_return_or_scalar_materialization_sec": 0.0001,
                    },
                    "public_speedup_claim_authorized": False,
                    "m7_promotion_authorized": False,
                },
                "topology_stream_prepared_handle": {
                    "contract": "topology_stream_prepared_handle_v1",
                    "generic_capability": "point_location_topology_stream",
                    "output_contract": "overlay_active_pair_dependency_count",
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                },
            }
        )
    return {
        "status": "ok",
        "case_shape": {
            "left_shape_count": 2000,
            "right_shape_count": 1500,
        },
        "comparison": {
            "same_output_contract": True,
            "active_counts_match": True,
            "all_counts_stable": True,
            "all_row_materialization_avoided": True,
            "active_count": 123,
            "embree_over_optix_timed_median": 10.0,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
        "rows": [
            {
                "backend": "embree",
                "output_contract": "overlay_active_pair_dependency_count",
                "active_count": 123,
                "counts_stable": True,
                "repeat": 25,
                "warmup": 3,
                "timed_median_sec": 0.020,
                "row_materialization_avoided": True,
                "claim_boundary": {"public_speedup_claim_authorized": False},
            },
            optix_row,
        ],
    }


class V3PhoenixSpatialOverlayActiveCountFullScaleCandidateTest(unittest.TestCase):
    def run_script(self, evidence: dict[str, object]):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            evidence_path = tmp_path / "evidence.json"
            json_out = tmp_path / "out.json"
            md_out = tmp_path / "out.md"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--evidence",
                    str(evidence_path),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertTrue(json_out.exists(), completed.stdout + completed.stderr)
            return completed.returncode, json.loads(json_out.read_text(encoding="utf-8")), md_out.read_text(
                encoding="utf-8"
            )

    def test_complete_full_scale_evidence_is_review_ready_not_promoted(self):
        code, payload, markdown = self.run_script(_evidence(include_m3=True))

        self.assertEqual(code, 0)
        self.assertEqual(
            payload["status"],
            "spatial_overlay_active_count_full_scale_m7_candidate_pending_external_review",
        )
        self.assertTrue(payload["local_evidence_sufficient_for_external_public_row_review"])
        self.assertEqual(payload["candidate_m7_contribution_if_external_review_approves"], 1)
        self.assertEqual(payload["m7_qualified_release_rows_added_now"], 0)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["metrics"]["shape_pair_count"], 3_000_000)
        self.assertEqual(payload["metrics"]["optix_active_count"], 123)
        self.assertEqual(payload["metrics"]["embree_active_count"], 123)
        self.assertEqual(payload["metrics"]["optix_minus_embree_active_count"], 0)
        self.assertEqual(payload["metrics"]["embree_over_optix_timed_median"], 10.0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertIn("Was I foolish?", markdown)

    def test_missing_m3_metadata_blocks_candidate(self):
        code, payload, _markdown = self.run_script(_evidence(include_m3=False))

        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "spatial_overlay_active_count_full_scale_no_go")
        self.assertFalse(payload["local_evidence_sufficient_for_external_public_row_review"])
        self.assertEqual(payload["candidate_m7_contribution_if_external_review_approves"], 0)
        self.assertIn("optix_m3_table_present", payload["failed_checks"])
        self.assertIn("optix_m3_table_complete", payload["failed_checks"])
        self.assertIn("optix_prepared_handle_present", payload["failed_checks"])


if __name__ == "__main__":
    unittest.main()
