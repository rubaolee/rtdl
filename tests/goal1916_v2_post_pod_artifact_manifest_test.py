from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from scripts.goal1916_v2_post_pod_artifact_manifest import main


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1916_v2_post_pod_artifact_manifest_2026-05-13.md"
SCRIPT = ROOT / "scripts" / "goal1916_v2_post_pod_artifact_manifest.py"


def _write_json(root: pathlib.Path, relative: str, payload: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _boundary() -> dict[str, bool]:
    return {
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
    }


class Goal1916V2PostPodArtifactManifestTest(unittest.TestCase):
    def test_report_documents_manifest_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pre-pod-ready", text)
        self.assertIn("Goal1905 answers", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("does not authorize v2.0", text)
        self.assertIn("Goal1916 manifest reports `pass`", text)

    def test_script_mentions_all_required_artifacts(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal1903_fixed_radius_batch_pod.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_512.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_2048.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("goal1903_v2_partner_pod_batch_summary.json", text)
        self.assertIn("missing RTX GPU provenance", text)
        self.assertIn("source_commit_label mismatch", text)

    def test_allow_missing_snapshot_blocks_without_release_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            rc = main(["--root", str(root), "--allow-missing"])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "docs/reports/goal1916_v2_post_pod_artifact_manifest.json").read_text())
            self.assertEqual(payload["status"], "blocked_missing_artifacts")
            self.assertTrue(payload["missing_artifacts"])
            self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])

    def test_complete_fixture_passes_and_summarizes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            common = {
                "git_commit": "abc123",
                "source_commit_label": "abc123",
                "gpu": "NVIDIA RTX A4500, 550.127.05",
            }
            _write_json(
                root,
                "docs/reports/goal1903_fixed_radius_batch_pod.json",
                {
                    "goal": 1878,
                    "status": "measurement",
                    **common,
                    "results": [{"partner": "torch", "claim_boundaries": _boundary()}],
                },
            )
            for count in (512, 2048):
                _write_json(
                    root,
                    f"docs/reports/goal1903_segment_polygon_batch_pod_{count}.json",
                    {
                        "goal": "Goal1863",
                        "status": "pass",
                        "count": count,
                        **common,
                        "partners": {"torch": {}, "cupy": {}},
                        "claim_boundary": {"same_contract_timing_row": True, **_boundary()},
                    },
                )
                _write_json(
                    root,
                    f"docs/reports/goal1889_road_hazard_prepared_reuse_pod_{count}.json",
                    {
                        "goal": "Goal1869",
                        "goal_extension": "Goal1889",
                        "status": "pass",
                        "count": count,
                        **common,
                        "partners": {"torch": {}, "cupy": {}},
                        "claim_boundary": _boundary(),
                    },
                )
            _write_json(
                root,
                "docs/reports/goal1903_v2_partner_pod_batch_summary.json",
                {
                    "source_commit_label": "abc123",
                    "fixed_radius": {"requested": True},
                    "segment_polygon": {"requested": True},
                    "road_hazard": {"requested": True},
                    "claim_boundary": _boundary(),
                },
            )
            rc = main(["--root", str(root)])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "docs/reports/goal1916_v2_post_pod_artifact_manifest.json").read_text())
            self.assertEqual(payload["status"], "pass")
            self.assertFalse(payload["errors"])
            self.assertEqual(payload["source_commit_label"], "abc123")
            self.assertTrue(all(entry["review_ready"] for entry in payload["artifacts"]))


if __name__ == "__main__":
    unittest.main()
