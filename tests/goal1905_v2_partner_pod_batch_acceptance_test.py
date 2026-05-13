from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from scripts.goal1905_v2_partner_pod_batch_acceptance import main


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1905_v2_partner_pod_batch_acceptance_2026-05-13.md"


def _write_json(root: pathlib.Path, relative: str, payload: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class Goal1905V2PartnerPodBatchAcceptanceTest(unittest.TestCase):
    def test_report_documents_fail_closed_post_pod_validator(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pre-pod-ready", text)
        self.assertIn("scripts/goal1905_v2_partner_pod_batch_acceptance.py", text)
        self.assertIn("goal1903_fixed_radius_batch_pod.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("same-contract timing row flag", text)
        self.assertIn("prepared scene/output reuse", text)
        self.assertIn("RTX GPU provenance", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("reported as warnings", text)
        self.assertIn("Local Linux Check", text)
        self.assertIn("blocked_missing_artifacts", text)
        self.assertIn("/tmp/rtdl_goal1889_smoke", text)
        self.assertIn("does not replace external review", text)

    def test_allow_missing_records_blocker_without_authorizing_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            rc = main(["--base-dir", str(root), "--allow-missing"])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json").read_text())
            self.assertEqual(payload["status"], "blocked_missing_artifacts")
            self.assertTrue(payload["missing_artifacts"])
            self.assertEqual(payload["warnings"], [])
            self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])

    def test_allow_missing_demotes_partial_summary_request_flags_to_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _write_json(
                root,
                "docs/reports/goal1903_v2_partner_pod_batch_summary.json",
                {
                    "fixed_radius": {"requested": False},
                    "segment_polygon": {"requested": False},
                    "road_hazard": {"requested": True},
                    "source_commit_label": "abc123",
                    "claim_boundary": {
                        "v2_0_release_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                        "broad_rt_core_speedup_claim_authorized": False,
                    },
                },
            )
            rc = main(["--base-dir", str(root), "--allow-missing"])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json").read_text())
            self.assertEqual(payload["status"], "blocked_missing_artifacts")
            self.assertFalse(payload["errors"])
            self.assertEqual(len(payload["warnings"]), 2)

    def test_complete_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _write_json(
                root,
                "docs/reports/goal1903_fixed_radius_batch_pod.json",
                {
                    "status": "measurement",
                    "git_commit": "abc123",
                    "source_commit_label": "abc123",
                    "gpu": "NVIDIA RTX A4500, 550.127.05",
                    "results": [
                        {
                            "claim_boundaries": {
                                "v2_0_release_authorized": False,
                                "whole_app_speedup_claim_authorized": False,
                                "broad_rt_core_speedup_claim_authorized": False,
                            }
                        }
                    ],
                },
            )
            for count in (512, 2048):
                _write_json(
                    root,
                    f"docs/reports/goal1903_segment_polygon_batch_pod_{count}.json",
                    {
                        "status": "pass",
                        "git_commit": "abc123",
                        "source_commit_label": "abc123",
                        "gpu": "NVIDIA RTX A4500, 550.127.05",
                        "parity": {"strict_counts_match": True},
                        "claim_boundary": {
                            "same_contract_timing_row": True,
                            "v2_0_release_authorized": False,
                            "whole_app_speedup_claim_authorized": False,
                            "broad_rt_core_speedup_claim_authorized": False,
                        },
                    },
                )
                _write_json(
                    root,
                    f"docs/reports/goal1889_road_hazard_prepared_reuse_pod_{count}.json",
                    {
                        "status": "pass",
                        "goal_extension": "Goal1889",
                        "git_commit": "abc123",
                        "source_commit_label": "abc123",
                        "gpu": "NVIDIA RTX A4500, 550.127.05",
                        "parity": {"strict_priority_flags_match": True},
                        "claim_boundary": {
                            "v2_0_release_authorized": False,
                            "whole_app_speedup_claim_authorized": False,
                            "broad_rt_core_speedup_claim_authorized": False,
                        },
                        "partners": {
                            "torch": {
                                "goal1889_prepared_reuse": {
                                    "prepared_scene_reused": True,
                                    "witness_output_columns_reused": True,
                                }
                            }
                        },
                    },
                )
            _write_json(
                root,
                "docs/reports/goal1903_v2_partner_pod_batch_summary.json",
                {
                    "fixed_radius": {"requested": True},
                    "segment_polygon": {"requested": True},
                    "road_hazard": {"requested": True},
                    "source_commit_label": "abc123",
                    "claim_boundary": {
                        "v2_0_release_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                        "broad_rt_core_speedup_claim_authorized": False,
                    },
                },
            )

            rc = main(["--base-dir", str(root)])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json").read_text())
            self.assertEqual(payload["status"], "pass")
            self.assertFalse(payload["errors"])
            self.assertFalse(payload["missing_artifacts"])


if __name__ == "__main__":
    unittest.main()
